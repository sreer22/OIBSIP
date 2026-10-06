# Python Voice Assistant

A beginner-friendly Python assistant with typed fallback plus optional microphone and speech output. It also supports natural-language intent patterns, web search, current date/time, reminders, live weather, short reference answers, configurable website commands, and explicitly confirmed email.

## Setup

Use Python 3.10 or newer:

```powershell
cd "DATA SCIENCE\Voice Assistant"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PyAudio cannot be installed on your OS/Python combination, the assistant still runs in typed mode. On Linux/macOS you may need the PortAudio development library before installing PyAudio. `SpeechRecognition`'s Google recognition backend needs an internet connection; microphone audio is sent to that service for transcription. `pyttsx3` speaks locally using the operating system's speech engine.

Run:

```powershell
python voice_assistant.py
```

Type a command at the prompt, or press Enter to speak (when microphone support is installed). If speech is not understood, the assistant asks you to repeat it.

## Example commands

- `Hello`, `What time is it?`, `What's today's date?`
- `Search the web for Python tutorials`
- `What is the weather in London?`
- `Remind me in 10 seconds to stretch`
- `Who is Ada Lovelace?` (uses Wikipedia's public summary API)
- `Email to test@example.com subject Test message Hello from my assistant`
- `Open YouTube` (custom phrases are configured in `custom_commands.json`)
- `Help`, `Goodbye`

Email sends only when SMTP settings are present and the user types the exact word `SEND` at the confirmation prompt. For testing, use a dedicated test mailbox/provider SMTP credentials, not a personal account password. Set configuration in the current shell's environment; never commit credentials:

```powershell
$env:SMTP_HOST = "smtp.example.test"
$env:SMTP_PORT = "465"
$env:SMTP_USERNAME = "assistant-test@example.test"
$env:SMTP_PASSWORD = "your-test-mailbox-app-password"
$env:SMTP_FROM = "assistant-test@example.test"
```

Weather uses Open-Meteo geocoding and forecast endpoints without an API key. Weather city queries are sent to Open-Meteo. General knowledge queries are sent to Wikipedia. Web search opens Google in the browser. Network failures are reported in the console/voice response.

## Privacy

- Speech recognition runs through the Google Web Speech API (`recognize_google`): recorded microphone audio is transmitted to Google for transcription. Do not speak passwords, financial details, or other sensitive information.
- Typed commands remain local except when they invoke web search, weather lookup, Wikipedia summaries, or email.
- Search terms go to Google; weather location queries and coordinates go to Open-Meteo; reference questions go to Wikipedia.
- Email content is transmitted to the configured SMTP provider and recipient only after the explicit typed confirmation.
- Reminder text stays in process memory and is removed when the program exits; pending reminders are cancelled on normal shutdown.
- TTS is local via `pyttsx3` and the installed system speech engine.

## Extending custom commands

Edit `custom_commands.json` to add a command name, one or more exact phrases, and an `http://` or `https://` URL. Commands only open a browser URL; arbitrary code execution is not supported.

## Tests

Run offline unit tests with:

```powershell
python -m unittest discover -s tests -v
```

The tests mock external services and do not use a microphone, send email, or contact the network.
