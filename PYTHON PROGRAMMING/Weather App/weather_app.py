"""Tkinter weather dashboard backed by Open-Meteo's free forecast APIs."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
import tkinter as tk
from tkinter import ttk


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
IP_INFO_URL = "https://ipinfo.io/json"
REQUEST_TIMEOUT = 12

WEATHER_CODES = {
    0: ("Clear sky", "☀"),
    1: ("Mainly clear", "🌤"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁"),
    45: ("Fog", "🌫"),
    48: ("Depositing rime fog", "🌫"),
    51: ("Light drizzle", "🌦"),
    53: ("Drizzle", "🌦"),
    55: ("Heavy drizzle", "🌧"),
    56: ("Freezing drizzle", "🌧"),
    57: ("Heavy freezing drizzle", "🌧"),
    61: ("Light rain", "🌦"),
    63: ("Rain", "🌧"),
    65: ("Heavy rain", "🌧"),
    66: ("Freezing rain", "🌧"),
    67: ("Heavy freezing rain", "🌧"),
    71: ("Light snow", "🌨"),
    73: ("Snow", "🌨"),
    75: ("Heavy snow", "❄"),
    77: ("Snow grains", "❄"),
    80: ("Rain showers", "🌦"),
    81: ("Rain showers", "🌧"),
    82: ("Heavy rain showers", "🌧"),
    85: ("Snow showers", "🌨"),
    86: ("Heavy snow showers", "❄"),
    95: ("Thunderstorm", "⛈"),
    96: ("Thunderstorm with hail", "⛈"),
    99: ("Thunderstorm with heavy hail", "⛈"),
}


class WeatherError(Exception):
    """A friendly, user-displayable weather lookup error."""


@dataclass(frozen=True)
class WeatherReport:
    location: str
    timezone: str
    current: dict[str, Any]
    hourly: list[dict[str, Any]]
    daily: list[dict[str, Any]]


def weather_description(code: int) -> tuple[str, str]:
    """Return a plain-language label and a compact weather symbol."""
    return WEATHER_CODES.get(code, ("Unknown conditions", "？"))


def convert_temperature(celsius: float, unit: str) -> float:
    """Convert a Celsius value to the selected display unit."""
    if unit == "C":
        return celsius
    if unit == "F":
        return (celsius * 9 / 5) + 32
    raise ValueError("Temperature unit must be 'C' or 'F'.")


def _display_location(place: dict[str, Any]) -> str:
    parts = [place.get("name"), place.get("admin1"), place.get("country")]
    return ", ".join(dict.fromkeys(str(part) for part in parts if part))


def _hour_label(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%I %p").lstrip("0")
    except ValueError:
        return value


def _day_label(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%a, %b %d")
    except ValueError:
        return value


class WeatherService:
    """Resolve a city or postal code and fetch current and forecast conditions."""

    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": "OIBSIPWeatherApp/1.0 (educational project)"})

    def find_location(self, query: str) -> dict[str, Any]:
        query = query.strip()
        if not query:
            raise WeatherError("Enter a city name or ZIP/postal code first.")

        try:
            response = self.session.get(
                GEOCODING_URL,
                params={"name": query, "count": 1, "language": "en", "format": "json"},
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 429:
                raise WeatherError("The location service is busy. Please wait a moment and try again.")
            response.raise_for_status()
            results = response.json().get("results", [])
        except requests.Timeout as exc:
            raise WeatherError("The location lookup timed out. Check your connection and retry.") from exc
        except requests.ConnectionError as exc:
            raise WeatherError("Could not connect to the location service. Check your internet connection.") from exc
        except requests.HTTPError as exc:
            raise WeatherError(f"The location service returned an error: {exc}") from exc
        except requests.RequestException as exc:
            raise WeatherError(f"Location lookup failed: {exc}") from exc
        except (ValueError, AttributeError) as exc:
            raise WeatherError("The location service returned an invalid response.") from exc

        if not results:
            raise WeatherError(f"No matching city or postal code found for “{query}”.")
        return results[0]

    def fetch_forecast(self, place: dict[str, Any]) -> WeatherReport:
        try:
            response = self.session.get(
                FORECAST_URL,
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": (
                        "temperature_2m,relative_humidity_2m,apparent_temperature,"
                        "weather_code,wind_speed_10m"
                    ),
                    "hourly": "temperature_2m,relative_humidity_2m,weather_code",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                    "forecast_days": 5,
                    "timezone": "auto",
                },
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 429:
                raise WeatherError("The weather service is busy. Please wait a moment and try again.")
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise WeatherError("The weather request timed out. Check your connection and retry.") from exc
        except requests.ConnectionError as exc:
            raise WeatherError("Could not connect to the weather service. Check your internet connection.") from exc
        except requests.HTTPError as exc:
            raise WeatherError(f"The weather service returned an error: {exc}") from exc
        except requests.RequestException as exc:
            raise WeatherError(f"Weather lookup failed: {exc}") from exc
        except (ValueError, AttributeError) as exc:
            raise WeatherError("The weather service returned invalid data.") from exc

        try:
            current = payload["current"]
            hourly_source = payload["hourly"]
            daily_source = payload["daily"]
            hourly_items = [
                {
                    "time": when,
                    "temperature": temperature,
                    "humidity": humidity,
                    "code": int(code),
                }
                for when, temperature, humidity, code in zip(
                    hourly_source["time"],
                    hourly_source["temperature_2m"],
                    hourly_source["relative_humidity_2m"],
                    hourly_source["weather_code"],
                )
            ]
            current_time = str(current["time"])
            next_hours = [item for item in hourly_items if item["time"] >= current_time][:6]
            daily_items = [
                {
                    "date": when,
                    "high": high,
                    "low": low,
                    "code": int(code),
                }
                for when, high, low, code in zip(
                    daily_source["time"],
                    daily_source["temperature_2m_max"],
                    daily_source["temperature_2m_min"],
                    daily_source["weather_code"],
                )
            ][:5]
            for key in (
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "time",
            ):
                if key not in current:
                    raise KeyError(key)
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherError("The weather service response was missing expected forecast values.") from exc

        return WeatherReport(
            location=_display_location(place),
            timezone=str(payload.get("timezone", place.get("timezone", "local time"))),
            current=current,
            hourly=next_hours,
            daily=daily_items,
        )

    def lookup(self, query: str) -> WeatherReport:
        return self.fetch_forecast(self.find_location(query))

    def locate_by_ip(self) -> str:
        """Return an approximate city from IP metadata; no coordinates are stored."""
        try:
            response = self.session.get(IP_INFO_URL, timeout=REQUEST_TIMEOUT)
            if response.status_code == 429:
                raise WeatherError("The IP location service is busy. Please enter a city instead.")
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise WeatherError("Automatic location lookup timed out. Enter a city instead.") from exc
        except requests.ConnectionError as exc:
            raise WeatherError("Could not connect to the IP location service. Enter a city instead.") from exc
        except requests.HTTPError as exc:
            raise WeatherError(f"Automatic location lookup failed: {exc}") from exc
        except requests.RequestException as exc:
            raise WeatherError(f"Automatic location lookup failed: {exc}") from exc
        except ValueError as exc:
            raise WeatherError("The IP location service returned invalid data.") from exc

        city = str(payload.get("city", "")).strip()
        region = str(payload.get("region", "")).strip()
        country = str(payload.get("country", "")).strip()
        if not city:
            raise WeatherError("Your approximate city could not be detected. Please enter it instead.")
        return ", ".join(part for part in (city, region, country) if part)


class WeatherApp:
    """Responsive desktop interface; network work runs outside the Tk event loop."""

    BG = "#0b1220"
    PANEL = "#131e30"
    PANEL_LIGHT = "#1b2a40"
    TEXT = "#f1f5f9"
    MUTED = "#9aabc0"
    ACCENT = "#72d2ff"
    ERROR = "#ff9898"

    def __init__(self, root: tk.Tk, service: WeatherService | None = None) -> None:
        self.root = root
        self.service = service or WeatherService()
        self.unit = tk.StringVar(value="C")
        self.location_text = tk.StringVar()
        self.status_text = tk.StringVar(value="Enter a city or postal code to see the forecast.")
        self.report: WeatherReport | None = None
        self.request_number = 0
        self.busy = False
        self._configure_window()
        self._build_ui()

    def _configure_window(self) -> None:
        self.root.title("Weather • Forecast")
        self.root.geometry("1020x790")
        self.root.minsize(860, 700)
        self.root.configure(bg=self.BG)
        self.root.option_add("*Font", "{Segoe UI} 10")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Weather.TCombobox", fieldbackground=self.PANEL_LIGHT, background=self.PANEL_LIGHT,
                        foreground=self.TEXT, arrowcolor=self.TEXT, borderwidth=0)
        style.map("Weather.TCombobox", fieldbackground=[("readonly", self.PANEL_LIGHT)],
                  foreground=[("readonly", self.TEXT)])

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=self.BG, padx=28, pady=20)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=self.BG)
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="WEATHER", bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(header, text="Your local forecast", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI Semibold", 25)).pack(anchor="w", pady=(2, 0))

        search = tk.Frame(outer, bg=self.PANEL, padx=14, pady=12)
        search.pack(fill="x", pady=(0, 12))
        self.entry = tk.Entry(
            search, textvariable=self.location_text, bg=self.PANEL_LIGHT, fg=self.TEXT,
            insertbackground=self.TEXT, relief="flat", font=("Segoe UI", 12),
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        self.entry.insert(0, "")
        self.entry.bind("<Return>", lambda _event: self.fetch_weather())

        self.search_button = tk.Button(
            search, text="Get Weather", command=self.fetch_weather,
            bg=self.ACCENT, fg="#082032", activebackground="#a3e4ff",
            relief="flat", padx=15, pady=9, font=("Segoe UI", 10, "bold"), cursor="hand2",
        )
        self.search_button.pack(side="left", padx=(0, 8))
        self.locate_button = tk.Button(
            search, text="⌖  Use My Location", command=self.locate_by_ip,
            bg=self.PANEL_LIGHT, fg=self.TEXT, activebackground="#263852",
            relief="flat", padx=12, pady=9, font=("Segoe UI", 10), cursor="hand2",
        )
        self.locate_button.pack(side="left")

        self.status_label = tk.Label(outer, textvariable=self.status_text, bg=self.BG, fg=self.MUTED,
                                     anchor="w", font=("Segoe UI", 9))
        self.status_label.pack(fill="x", pady=(0, 10))

        self.current_panel = tk.Frame(outer, bg=self.PANEL, padx=22, pady=17)
        self.current_panel.pack(fill="x", pady=(0, 12))

        self.location_label = tk.Label(self.current_panel, text="Ready when you are",
                                       bg=self.PANEL, fg=self.TEXT, font=("Segoe UI Semibold", 16))
        self.location_label.pack(anchor="w")
        current_row = tk.Frame(self.current_panel, bg=self.PANEL)
        current_row.pack(fill="x", pady=(9, 0))

        self.icon_label = tk.Label(current_row, text="☀", bg=self.PANEL, fg=self.ACCENT,
                                   font=("Segoe UI Emoji", 48))
        self.icon_label.pack(side="left", padx=(0, 16))
        temp_block = tk.Frame(current_row, bg=self.PANEL)
        temp_block.pack(side="left", anchor="w")
        temp_line = tk.Frame(temp_block, bg=self.PANEL)
        temp_line.pack(anchor="w")
        self.temperature_label = tk.Label(temp_line, text="--°", bg=self.PANEL, fg=self.TEXT,
                                          font=("Segoe UI Light", 42))
        self.temperature_label.pack(side="left")
        self.secondary_temperature_label = tk.Label(
            temp_line, text="| --°", bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 14)
        )
        self.secondary_temperature_label.pack(side="left", padx=(8, 0), pady=(13, 0))
        self.unit_button = tk.Button(
            temp_line, text="Switch to °F", command=self.toggle_unit, bg=self.PANEL_LIGHT,
            fg=self.ACCENT, activebackground="#263852", relief="flat", padx=10, pady=5,
            font=("Segoe UI", 10, "bold"), cursor="hand2",
        )
        self.unit_button.pack(side="left", padx=(10, 0), pady=(12, 0))
        self.condition_label = tk.Label(temp_block, text="Current conditions", bg=self.PANEL,
                                        fg=self.MUTED, font=("Segoe UI", 12))
        self.condition_label.pack(anchor="w")
        self.details_label = tk.Label(current_row, text="Feels like --    •    Humidity --    •    Wind --",
                                      bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 10))
        self.details_label.pack(side="right", anchor="center", padx=(16, 0))

        self.hourly_cards = self._section(outer, "NEXT 6 HOURS")
        self.daily_cards = self._section(outer, "5-DAY FORECAST")

        footer = tk.Label(
            outer,
            text="Weather data: Open-Meteo  •  Approximate location uses IP-based lookup only when requested",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8),
        )
        footer.pack(anchor="w", pady=(12, 0))

    def _section(self, parent: tk.Widget, title: str) -> tk.Frame:
        section = tk.Frame(parent, bg=self.BG)
        section.pack(fill="x", pady=(0, 9))
        tk.Label(section, text=title, bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        card = tk.Frame(section, bg=self.PANEL, padx=9, pady=9)
        card.pack(fill="x")
        return card

    def _start_request(self, action: str, *args: str) -> None:
        if self.busy:
            return
        self.busy = True
        self.request_number += 1
        request_id = self.request_number
        self.status_label.configure(fg=self.MUTED)
        self.status_text.set("Fetching forecast…")
        self._set_buttons_enabled(False)
        threading.Thread(
            target=self._worker, args=(request_id, action, args), daemon=True
        ).start()

    def _worker(self, request_id: int, action: str, args: tuple[str, ...]) -> None:
        try:
            if action == "lookup":
                report = self.service.lookup(args[0])
            else:
                detected_location = self.service.locate_by_ip()
                self.root.after(0, self.location_text.set, detected_location)
                report = self.service.lookup(detected_location)
            self.root.after(0, self._show_report, request_id, report)
        except WeatherError as exc:
            self.root.after(0, self._show_error, request_id, str(exc))
        except Exception as exc:
            self.root.after(
                0, self._show_error, request_id,
                f"Unexpected error: {type(exc).__name__}: {exc}",
            )

    def fetch_weather(self) -> None:
        if self.busy:
            return
        query = self.location_text.get().strip()
        if not query:
            self._show_error(self.request_number, "Enter a city name or ZIP/postal code.")
            return
        self._start_request("lookup", query)

    def locate_by_ip(self) -> None:
        if not self.busy:
            self._start_request("ip")

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.search_button.configure(state=state)
        self.locate_button.configure(state=state)

    def _show_error(self, request_id: int, message: str) -> None:
        if request_id != self.request_number:
            return
        self.busy = False
        self._set_buttons_enabled(True)
        self.status_label.configure(fg=self.ERROR)
        self.status_text.set(message)

    def _show_report(self, request_id: int, report: WeatherReport) -> None:
        if request_id != self.request_number:
            return
        self.busy = False
        self.report = report
        self._set_buttons_enabled(True)
        self.status_label.configure(fg=self.MUTED)
        self.status_text.set(f"Updated {report.current['time'].replace('T', ' ')}  •  {report.timezone}")
        self.location_label.configure(text=report.location)
        self._render_current()
        self._render_cards()

    def toggle_unit(self) -> None:
        self.unit.set("F" if self.unit.get() == "C" else "C")
        if self.report is not None:
            self._render_current()
            self._render_cards()

    def _temperature(self, celsius: float, unit: str | None = None) -> str:
        selected_unit = unit or self.unit.get()
        value = convert_temperature(float(celsius), selected_unit)
        return f"{round(value)}°{selected_unit}"

    def _render_current(self) -> None:
        if self.report is None:
            return
        current = self.report.current
        description, icon = weather_description(int(current["weather_code"]))
        self.icon_label.configure(text=icon)
        self.temperature_label.configure(text=self._temperature(current["temperature_2m"]))
        alternate_unit = "F" if self.unit.get() == "C" else "C"
        self.secondary_temperature_label.configure(
            text=f"| {self._temperature(current['temperature_2m'], alternate_unit)}"
        )
        self.unit_button.configure(text=f"Switch to °{alternate_unit}")
        self.condition_label.configure(text=description)
        feels_like = self._temperature(current["apparent_temperature"])
        self.details_label.configure(
            text=(
                f"Feels like {feels_like}    •    Humidity "
                f"{current['relative_humidity_2m']}%    •    Wind {current['wind_speed_10m']} km/h"
            )
        )

    @staticmethod
    def _clear_cards(container: tk.Frame) -> None:
        for child in container.winfo_children():
            child.destroy()

    def _render_cards(self) -> None:
        if self.report is None:
            return
        self._clear_cards(self.hourly_cards)
        for index, item in enumerate(self.report.hourly):
            card = tk.Frame(self.hourly_cards, bg=self.PANEL_LIGHT, padx=9, pady=8)
            card.grid(row=0, column=index, sticky="nsew", padx=3)
            self.hourly_cards.grid_columnconfigure(index, weight=1)
            description, icon = weather_description(item["code"])
            tk.Label(card, text=_hour_label(item["time"]), bg=self.PANEL_LIGHT,
                     fg=self.MUTED, font=("Segoe UI", 9)).pack()
            tk.Label(card, text=icon, bg=self.PANEL_LIGHT, fg=self.ACCENT,
                     font=("Segoe UI Emoji", 20)).pack(pady=2)
            tk.Label(card, text=self._temperature(item["temperature"]), bg=self.PANEL_LIGHT,
                     fg=self.TEXT, font=("Segoe UI Semibold", 12)).pack()
            tk.Label(card, text=f"{item['humidity']}% RH", bg=self.PANEL_LIGHT,
                     fg=self.MUTED, font=("Segoe UI", 8)).pack()
            card.bind("<Enter>", lambda _event, tip=description: self.status_text.set(tip))
            card.bind("<Leave>", lambda _event: self.status_text.set(
                f"Updated {self.report.current['time'].replace('T', ' ')}  •  {self.report.timezone}"
            ))

        self._clear_cards(self.daily_cards)
        for index, item in enumerate(self.report.daily):
            card = tk.Frame(self.daily_cards, bg=self.PANEL_LIGHT, padx=11, pady=8)
            card.grid(row=0, column=index, sticky="nsew", padx=3)
            self.daily_cards.grid_columnconfigure(index, weight=1)
            description, icon = weather_description(item["code"])
            tk.Label(card, text=_day_label(item["date"]), bg=self.PANEL_LIGHT,
                     fg=self.MUTED, font=("Segoe UI", 9)).pack()
            tk.Label(card, text=icon, bg=self.PANEL_LIGHT, fg=self.ACCENT,
                     font=("Segoe UI Emoji", 20)).pack(pady=2)
            tk.Label(
                card,
                text=f"{self._temperature(item['high'])} / {self._temperature(item['low'])}",
                bg=self.PANEL_LIGHT, fg=self.TEXT, font=("Segoe UI Semibold", 10),
            ).pack()
            tk.Label(card, text=description, bg=self.PANEL_LIGHT, fg=self.MUTED,
                     font=("Segoe UI", 8), wraplength=115).pack(pady=(3, 0))


def main() -> None:
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
