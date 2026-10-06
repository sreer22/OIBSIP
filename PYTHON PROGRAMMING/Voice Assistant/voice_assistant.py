"""A privacy-conscious, extensible voice assistant with a typed fallback."""

from __future__ import annotations

import json
import os
import re
import smtplib
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
from typing import Callable
from urllib.parse import quote_plus

import requests


APP_DIR = Path(__file__).resolve().parent
DEFAULT_COMMANDS_PATH = APP_DIR / "custom_commands.json"
CHANNEL_TIMEOUT = 10


@dataclass(frozen=True)
class Intent:
    """A normalized user request and its optional parameters."""

    name: str
    args: dict[str, str | int]


def parse_intent(text: str, custom_commands: dict | None = None) -> Intent:
    """Map a natural-language phrase to an intent using ordered phrase patterns."""
    original = text.strip()
    normalized = re.sub(r"\s+", " ", original.casefold())

    if not normalized:
        return Intent("unknown", {})

    reminder_match = re.search(
        r"\bremind me in\s+(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)"
        r"(?:\s+to\s+(.+))?$",
        normalized,
    )
    if reminder_match:
        amount = int(reminder_match.group(1))
        unit = reminder_match.group(2)
        task = reminder_match.group(3) or "your reminder"
        multiplier = 3600 if unit.startswith(("hour", "hr")) else 60 if unit.startswith(("minute", "min")) else 1
        return Intent("reminder", {"seconds": amount * multiplier, "task": task})

    email_match = re.search(
        r"\bemail\s+to\s+([^\s]+)\s+subject\s+(.+?)\s+message\s+(.+)$",
        original,
        flags=re.IGNORECASE,
    )
    if email_match:
        return Intent(
            "email",
            {
                "to": email_match.group(1).strip(),
                "subject": email_match.group(2).strip(),
                "body": email_match.group(3).strip(),
            },
        )

    weather_match = re.search(
        r"\b(?:what(?:'s| is)?\s+the\s+weather(?:\s+like)?\s+in|"
        r"(?:get|check|tell me)\s+(?:the\s+)?weather(?:\s+in)?)\s+(.+)$",
        normalized,
    )
    if weather_match:
        return Intent("weather", {"city": weather_match.group(1).strip(" ?.!")})

    search_match = re.search(
        r"\b(?:search(?:\s+the\s+web)?\s+for|look\s+up|google)\s+(.+)$",
        original,
        flags=re.IGNORECASE,
    )
    if search_match:
        return Intent("search", {"query": search_match.group(1).strip(" ?.!")})

    if re.search(r"\b(?:what time is it|tell me the time|current time|time now)\b", normalized):
        return Intent("time", {})
    if re.search(r"\b(?:what(?:'s| is)? (?:today'?s )?date|tell me the date|today'?s date)\b", normalized):
        return Intent("date", {})
    if re.search(r"\b(?:hello|hi|hey|good morning|good afternoon|good evening)\b", normalized):
        return Intent("greeting", {})
    if re.search(r"\b(?:help|what can you do|available commands)\b", normalized):
        return Intent("help", {})
    if re.search(r"\b(?:quit|exit|goodbye|stop listening)\b", normalized):
        return Intent("exit", {})

    for command_name, definition in (custom_commands or {}).items():
        phrases = definition.get("phrases", [])
        if any(normalized == phrase.casefold().strip() for phrase in phrases):
            return Intent("custom", {"name": command_name, "url": definition["url"]})

    return Intent("knowledge", {"query": original})


class VoiceInput:
    """Listen through a microphone using SpeechRecognition when installed."""

    def __init__(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError:
            self._sr = None
            self._pyaudio = None
            self._recognizer = None
            self.error = "Voice input is unavailable. Install SpeechRecognition and PyAudio."
            return
        self._sr = sr
        self._recognizer = sr.Recognizer()
        try:
            import pyaudio
        except ImportError:
            self._pyaudio = None
            self.error = "Voice input is unavailable. Install PyAudio to enable the microphone."
        else:
            self._pyaudio = pyaudio
            self.error = ""

    @property
    def available(self) -> bool:
        return self._sr is not None and self._pyaudio is not None

    def listen(self) -> str | None:
        if not self.available:
            raise RuntimeError(self.error or "Voice input is unavailable.")
        try:
            with self._sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return self._recognizer.recognize_google(audio)
        except self._sr.WaitTimeoutError:
            return None
        except self._sr.UnknownValueError:
            return None
        except self._sr.RequestError as exc:
            raise RuntimeError(f"Speech recognition service failed: {exc}") from exc
        except OSError as exc:
            raise RuntimeError(f"Microphone is unavailable: {exc}") from exc


class VoiceOutput:
    """Speak feedback with pyttsx3; fall back to console output if unavailable."""

    def __init__(self) -> None:
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self.error = ""
        except (ImportError, RuntimeError) as exc:
            self._engine = None
            self.error = f"Text-to-speech is unavailable; responses will be printed. ({exc})"

    def say(self, message: str) -> None:
        print(f"Assistant: {message}")
        if self._engine is not None:
            try:
                self._engine.say(message)
                self._engine.runAndWait()
            except RuntimeError as exc:
                print(f"Text-to-speech playback failed: {exc}")


class Assistant:
    """Dispatch assistant intents and provide optional online services."""

    def __init__(
        self,
        speak: Callable[[str], None],
        *,
        opener: Callable[[str], bool] = webbrowser.open,
        http: requests.Session | None = None,
        input_fn: Callable[[str], str] = input,
        commands_path: Path = DEFAULT_COMMANDS_PATH,
        environ: dict[str, str] | None = None,
    ) -> None:
        self.speak = speak
        self.opener = opener
        self.http = http or requests.Session()
        self.input_fn = input_fn
        self.environ = os.environ if environ is None else environ
        self.reminders: list[threading.Timer] = []
        self.custom_commands = self._load_custom_commands(commands_path)

    @staticmethod
    def _load_custom_commands(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not load custom commands from {path}: {exc}") from exc
        if not isinstance(content, dict):
            raise ValueError("Custom commands configuration must be a JSON object.")
        for name, definition in content.items():
            if (
                not isinstance(name, str)
                or not isinstance(definition, dict)
                or not isinstance(definition.get("phrases"), list)
                or not all(isinstance(phrase, str) for phrase in definition["phrases"])
                or not isinstance(definition.get("url"), str)
                or not definition["url"].startswith(("https://", "http://"))
            ):
                raise ValueError(f"Invalid custom command definition: {name!r}")
        return content

    def handle(self, text: str) -> bool:
        """Handle one utterance; return False when the caller should exit."""
        intent = parse_intent(text, self.custom_commands)
        try:
            if intent.name == "unknown":
                self.speak("Sorry, I didn't understand. Please repeat that or type help.")
            elif intent.name == "greeting":
                self.speak("Hello! How can I help you?")
            elif intent.name == "time":
                self.speak(f"The time is {datetime.now().strftime('%I:%M %p')}.")
            elif intent.name == "date":
                self.speak(f"Today is {datetime.now().strftime('%A, %B %d, %Y')}.")
            elif intent.name == "search":
                query = str(intent.args["query"])
                self.opener(f"https://www.google.com/search?q={quote_plus(query)}")
                self.speak(f"Here are search results for {query}.")
            elif intent.name == "reminder":
                self._set_reminder(int(intent.args["seconds"]), str(intent.args["task"]))
            elif intent.name == "weather":
                self._weather(str(intent.args["city"]))
            elif intent.name == "knowledge":
                self._knowledge(str(intent.args["query"]))
            elif intent.name == "email":
                self._send_email(intent.args)
            elif intent.name == "custom":
                self.opener(str(intent.args["url"]))
                self.speak(f"Opening {intent.args['name']}.")
            elif intent.name == "help":
                self.speak(
                    "You can say hello, ask for the time or date, search the web, "
                    "ask about the weather in a city, ask a general knowledge question, "
                    "set a reminder, or say goodbye."
                )
            elif intent.name == "exit":
                self.speak("Goodbye!")
                return False
            else:
                self.speak("Sorry, that request is not supported.")
        except requests.RequestException as exc:
            self.speak(f"The online service could not be reached: {exc}")
        except (ValueError, RuntimeError) as exc:
            self.speak(str(exc))
        return True

    def _set_reminder(self, seconds: int, task: str) -> None:
        if seconds <= 0 or seconds > 7 * 24 * 3600:
            self.speak("Please choose a reminder duration between 1 second and 7 days.")
            return
        timer = threading.Timer(seconds, self.speak, args=(f"Reminder: {task}.",))
        timer.daemon = True
        timer.start()
        self.reminders.append(timer)
        self.speak(f"I'll remind you to {task} in {seconds} seconds.")

    def _weather(self, city: str) -> None:
        if not city:
            self.speak("Please say a city, for example: weather in London.")
            return
        geocoding = self.http.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=CHANNEL_TIMEOUT,
        )
        geocoding.raise_for_status()
        locations = geocoding.json().get("results", [])
        if not locations:
            self.speak(f"I couldn't find a location named {city}.")
            return
        location = locations[0]
        weather = self.http.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=CHANNEL_TIMEOUT,
        )
        weather.raise_for_status()
        current = weather.json().get("current")
        if not current:
            raise ValueError("The weather service returned no current conditions.")
        description = self._weather_description(int(current["weather_code"]))
        self.speak(
            f"In {location['name']}, it is {current['temperature_2m']} degrees Celsius "
            f"and {description}. Feels like {current['apparent_temperature']} degrees, "
            f"with humidity at {current['relative_humidity_2m']} percent."
        )

    @staticmethod
    def _weather_description(code: int) -> str:
        if code == 0:
            return "clear"
        if code in (1, 2, 3):
            return "partly cloudy"
        if code in (45, 48):
            return "foggy"
        if code in (51, 53, 55, 56, 57):
            return "drizzling"
        if code in (61, 63, 65, 66, 67, 80, 81, 82):
            return "rainy"
        if code in (71, 73, 75, 77, 85, 86):
            return "snowy"
        if code in (95, 96, 99):
            return "thundery"
        return "conditions not classified"

    def _knowledge(self, query: str) -> None:
        response = self.http.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(query.replace(" ", "_")),
            headers={"User-Agent": "OIBSIPVoiceAssistant/1.0 (educational project)"},
            timeout=CHANNEL_TIMEOUT,
        )
        if response.status_code == 404:
            self.speak(f"I couldn't find a short reference for {query}.")
            return
        response.raise_for_status()
        summary = response.json().get("extract", "")
        if not summary:
            self.speak(f"I couldn't find a short reference for {query}.")
            return
        self.speak(summary[:900])

    def _send_email(self, details: dict[str, str | int]) -> None:
        recipient = str(details["to"])
        if parseaddr(recipient)[1] != recipient or "@" not in recipient:
            raise ValueError("That email address doesn't look valid.")

        host = self.environ.get("SMTP_HOST", "")
        port = int(self.environ.get("SMTP_PORT", "465"))
        username = self.environ.get("SMTP_USERNAME", "")
        password = self.environ.get("SMTP_PASSWORD", "")
        sender = self.environ.get("SMTP_FROM", username)
        if not all((host, username, password, sender)):
            raise ValueError(
                "Email is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
                "SMTP_PASSWORD, and SMTP_FROM in your environment."
            )
        if self.input_fn(f"Type SEND to confirm emailing {recipient}: ").strip() != "SEND":
            self.speak("Email cancelled.")
            return

        message = EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = str(details["subject"])
        message.set_content(str(details["body"]))
        with smtplib.SMTP_SSL(host, port, timeout=CHANNEL_TIMEOUT) as server:
            server.login(username, password)
            server.send_message(message)
        self.speak(f"Email sent to {recipient}.")

    def close(self) -> None:
        """Cancel pending reminders during a normal application shutdown."""
        for timer in self.reminders:
            timer.cancel()


def run() -> None:
    """Run an interactive loop with microphone and typed command modes."""
    voice_input = VoiceInput()
    voice_output = VoiceOutput()
    if voice_output.error:
        print(voice_output.error)
    if not voice_input.available:
        print(voice_input.error)

    assistant = Assistant(voice_output.say)
    print("Voice Assistant — enter text, or press Enter to use the microphone.")
    print("Type 'quit' or say 'goodbye' to exit.")
    try:
        while True:
            try:
                typed = input("\nYou (Enter for voice): ").strip()
                if typed:
                    utterance = typed
                elif voice_input.available:
                    voice_output.say("I'm listening.")
                    utterance = voice_input.listen()
                    if utterance is None:
                        voice_output.say("Sorry, I didn't catch that. Please repeat.")
                        continue
                    print(f"You said: {utterance}")
                else:
                    voice_output.say("Voice input is unavailable. Please type a command.")
                    continue
            except (EOFError, KeyboardInterrupt):
                print()
                break
            except RuntimeError as exc:
                voice_output.say(f"{exc} You can type a command instead.")
                continue
            try:
                if not assistant.handle(utterance):
                    break
            except Exception as exc:
                # Keep the interactive loop alive while exposing unexpected failures.
                print(f"Command failed: {type(exc).__name__}: {exc}")
    finally:
        assistant.close()


if __name__ == "__main__":
    run()
