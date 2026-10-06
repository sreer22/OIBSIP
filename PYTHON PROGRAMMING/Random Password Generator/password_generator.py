"""Generate strong passwords with secrets and a small Tkinter interface."""

from __future__ import annotations

import secrets
import string
import tkinter as tk
from collections import deque
from tkinter import ttk


MIN_LENGTH = 8
MAX_LENGTH = 128
AMBIGUOUS_CHARACTERS = frozenset("0Ool1I|")

CHARACTER_GROUPS = {
    "uppercase": string.ascii_uppercase,
    "lowercase": string.ascii_lowercase,
    "numbers": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.?/<>~",
}


def password_strength(length: int, selected_type_count: int) -> str:
    """Return a simple user-facing strength category from length and diversity."""
    if length < MIN_LENGTH or selected_type_count < 2:
        return "Weak"
    if length >= 16 and selected_type_count >= 3:
        return "Strong"
    if length >= 12 and selected_type_count >= 2:
        return "Medium"
    return "Weak"


def generate_password(
    length: int,
    selected_types: list[str] | tuple[str, ...] | set[str],
    *,
    exclude_ambiguous: bool = False,
) -> str:
    """Generate a cryptographically secure password meeting all chosen classes."""
    if isinstance(length, bool) or not isinstance(length, int):
        raise ValueError("Password length must be a whole number.")
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(f"Password length must be between {MIN_LENGTH} and {MAX_LENGTH}.")

    selected = list(dict.fromkeys(selected_types))
    if len(selected) < 2:
        raise ValueError("Select at least two character types.")
    unknown = set(selected) - CHARACTER_GROUPS.keys()
    if unknown:
        raise ValueError(f"Unknown character type(s): {', '.join(sorted(unknown))}.")
    if len(selected) > length:
        raise ValueError("Password length must be at least the number of selected character types.")

    pools: dict[str, str] = {}
    for name in selected:
        pool = CHARACTER_GROUPS[name]
        if exclude_ambiguous:
            pool = "".join(character for character in pool if character not in AMBIGUOUS_CHARACTERS)
        if not pool:
            raise ValueError(f"No available characters remain for {name}.")
        pools[name] = pool

    all_characters = "".join(pools.values())
    password_characters = [secrets.choice(pools[name]) for name in selected]
    password_characters.extend(
        secrets.choice(all_characters) for _ in range(length - len(password_characters))
    )
    secrets.SystemRandom().shuffle(password_characters)
    return "".join(password_characters)


class PasswordGeneratorApp:
    """Desktop interface for generating, copying, and viewing session history."""

    BG = "#0b1220"
    PANEL = "#131e30"
    PANEL_LIGHT = "#1b2a40"
    TEXT = "#f1f5f9"
    MUTED = "#9aabc0"
    ACCENT = "#72d2ff"
    ERROR = "#ff9898"
    SUCCESS = "#83e0b0"
    AMBER = "#ffd166"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.length = tk.IntVar(value=20)
        self.type_vars = {
            name: tk.BooleanVar(value=True)
            for name in CHARACTER_GROUPS
        }
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.password = tk.StringVar()
        self.status = tk.StringVar(value="Choose your options and generate a password.")
        self.strength = tk.StringVar(value="Strength: —")
        self.history: deque[str] = deque(maxlen=5)
        self._configure()
        self._build_ui()

    def _configure(self) -> None:
        self.root.title("Secure Password Generator")
        self.root.geometry("580x700")
        self.root.minsize(520, 650)
        self.root.configure(bg=self.BG)
        self.root.option_add("*Font", "{Segoe UI} 10")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Password.Horizontal.TProgressbar",
            troughcolor=self.PANEL_LIGHT,
            background=self.SUCCESS,
            bordercolor=self.PANEL_LIGHT,
            lightcolor=self.SUCCESS,
            darkcolor=self.SUCCESS,
        )

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=self.BG, padx=28, pady=20)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="SECURITY TOOL", bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(outer, text="Password Generator", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI Semibold", 24)).pack(anchor="w", pady=(2, 4))
        tk.Label(
            outer, text="Create a strong password. Nothing is saved to disk.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 17))

        options = tk.Frame(outer, bg=self.PANEL, padx=18, pady=15)
        options.pack(fill="x")
        tk.Label(options, text="PASSWORD LENGTH", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        length_row = tk.Frame(options, bg=self.PANEL)
        length_row.pack(fill="x", pady=(7, 13))
        self.length_scale = tk.Scale(
            length_row, from_=MIN_LENGTH, to=MAX_LENGTH, orient="horizontal",
            variable=self.length, showvalue=False, resolution=1, bg=self.PANEL,
            fg=self.TEXT, troughcolor=self.PANEL_LIGHT, activebackground=self.ACCENT,
            highlightthickness=0, relief="flat", command=self._on_length_changed,
        )
        self.length_scale.pack(side="left", fill="x", expand=True)
        self.length_value = tk.Label(length_row, text=str(self.length.get()), width=4,
                                     bg=self.PANEL_LIGHT, fg=self.TEXT,
                                     font=("Segoe UI Semibold", 13), pady=5)
        self.length_value.pack(side="left", padx=(10, 0))

        tk.Label(options, text="INCLUDE CHARACTER TYPES", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        type_row = tk.Frame(options, bg=self.PANEL)
        type_row.pack(fill="x")
        labels = [
            ("uppercase", "A–Z"),
            ("lowercase", "a–z"),
            ("numbers", "0–9"),
            ("symbols", "Symbols"),
        ]
        for name, label in labels:
            checkbox = tk.Checkbutton(
                type_row, text=label, variable=self.type_vars[name],
                bg=self.PANEL, fg=self.TEXT, activebackground=self.PANEL,
                activeforeground=self.TEXT, selectcolor=self.PANEL_LIGHT,
                highlightthickness=0, relief="flat", cursor="hand2",
            )
            checkbox.pack(side="left", padx=(0, 8))

        self.ambiguous_checkbox = tk.Checkbutton(
            options, text="Exclude ambiguous characters (0, O, o, l, 1, I, |)",
            variable=self.exclude_ambiguous, bg=self.PANEL, fg=self.MUTED,
            activebackground=self.PANEL, activeforeground=self.TEXT,
            selectcolor=self.PANEL_LIGHT, highlightthickness=0,
            relief="flat", cursor="hand2",
        )
        self.ambiguous_checkbox.pack(anchor="w", pady=(8, 0))

        output = tk.Frame(outer, bg=self.PANEL, padx=18, pady=16)
        output.pack(fill="x", pady=(14, 12))
        tk.Label(output, text="YOUR PASSWORD", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        password_row = tk.Frame(output, bg=self.PANEL)
        password_row.pack(fill="x", pady=(9, 10))
        self.password_entry = tk.Entry(
            password_row, textvariable=self.password, state="readonly",
            readonlybackground=self.PANEL_LIGHT, fg=self.TEXT,
            insertbackground=self.TEXT, relief="flat", font=("Consolas", 14),
            justify="center",
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 9))
        self.copy_button = tk.Button(
            password_row, text="Copy", command=self.copy_password,
            bg=self.PANEL_LIGHT, fg=self.TEXT, activebackground="#263852",
            relief="flat", padx=14, pady=8, cursor="hand2",
        )
        self.copy_button.pack(side="left")

        strength_row = tk.Frame(output, bg=self.PANEL)
        strength_row.pack(fill="x")
        self.strength_label = tk.Label(strength_row, textvariable=self.strength,
                                       bg=self.PANEL, fg=self.MUTED,
                                       font=("Segoe UI Semibold", 10))
        self.strength_label.pack(side="left")
        self.strength_bar = ttk.Progressbar(
            strength_row, maximum=3, value=0,
            style="Password.Horizontal.TProgressbar",
        )
        self.strength_bar.pack(side="right", fill="x", expand=True, padx=(14, 0))

        self.generate_button = tk.Button(
            outer, text="Generate Password", command=self.generate,
            bg=self.ACCENT, fg="#082032", activebackground="#a3e4ff",
            relief="flat", pady=11, font=("Segoe UI", 11, "bold"), cursor="hand2",
        )
        self.generate_button.pack(fill="x")
        self.status_label = tk.Label(outer, textvariable=self.status, bg=self.BG,
                                     fg=self.MUTED, anchor="w", font=("Segoe UI", 9))
        self.status_label.pack(fill="x", pady=(8, 12))

        history_panel = tk.Frame(outer, bg=self.PANEL, padx=18, pady=13)
        history_panel.pack(fill="both", expand=True)
        tk.Label(history_panel, text="RECENT PASSWORDS", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(history_panel, text="Only held in memory until you close the app.",
                 bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 7))
        self.history_list = tk.Listbox(
            history_panel, height=5, bg=self.PANEL_LIGHT, fg=self.TEXT,
            selectbackground="#285474", selectforeground=self.TEXT,
            highlightthickness=0, borderwidth=0, relief="flat",
            font=("Consolas", 10), activestyle="none",
        )
        self.history_list.pack(fill="both", expand=True)

    def _on_length_changed(self, value: str) -> None:
        self.length_value.configure(text=str(int(float(value))))

    def _selected_types(self) -> list[str]:
        return [name for name, variable in self.type_vars.items() if variable.get()]

    def _set_strength(self, category: str) -> None:
        values = {"Weak": 1, "Medium": 2, "Strong": 3}
        colors = {"Weak": self.ERROR, "Medium": self.AMBER, "Strong": self.SUCCESS}
        self.strength.set(f"Strength: {category}")
        self.strength_label.configure(fg=colors[category])
        self.strength_bar.configure(value=values[category])
        self.strength_bar.configure(style="Password.Horizontal.TProgressbar")
        style = ttk.Style(self.root)
        style.configure(
            "Password.Horizontal.TProgressbar",
            background=colors[category],
            lightcolor=colors[category],
            darkcolor=colors[category],
        )

    def generate(self) -> None:
        selected = self._selected_types()
        try:
            password = generate_password(
                self.length.get(),
                selected,
                exclude_ambiguous=self.exclude_ambiguous.get(),
            )
        except ValueError as exc:
            self.status_label.configure(fg=self.ERROR)
            self.status.set(str(exc))
            return

        self.password.set(password)
        self.history.appendleft(password)
        self._refresh_history()
        self._set_strength(password_strength(len(password), len(selected)))
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update_idletasks()
        except tk.TclError as exc:
            self.status_label.configure(fg=self.ERROR)
            self.status.set(f"Password generated, but clipboard copy failed: {exc}")
            return
        self.status_label.configure(fg=self.SUCCESS)
        self.status.set("Generated securely and copied to clipboard.")

    def copy_password(self) -> None:
        password = self.password.get()
        if not password:
            self.status_label.configure(fg=self.ERROR)
            self.status.set("Generate a password before copying.")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update_idletasks()
        except tk.TclError as exc:
            self.status_label.configure(fg=self.ERROR)
            self.status.set(f"Clipboard copy failed: {exc}")
            return
        self.status_label.configure(fg=self.SUCCESS)
        self.status.set("Password copied to clipboard.")

    def _refresh_history(self) -> None:
        self.history_list.delete(0, tk.END)
        for password in self.history:
            self.history_list.insert(tk.END, password)


def main() -> None:
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
