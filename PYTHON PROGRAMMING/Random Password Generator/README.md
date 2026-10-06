# Random Password Generator

A Tkinter password generator using Python's cryptographically secure `secrets` module (not `random`). Choose a length from 8 to 128 and at least two character types. Every generated password contains at least one character from each selected type. The optional ambiguous-character filter excludes `0`, `O`, `o`, `l`, `1`, `I`, and `|`.

## Run

```powershell
cd "C:\Users\Sreeyakeshrajan_T\OneDrive\Desktop\OIBSIP\PYTHON PROGRAMMING\Random Password Generator"
python password_generator.py
```

No third-party packages are needed. Tkinter is included with most standard Python for Windows installations.

Click **Generate Password** to generate a new password and copy it to the clipboard automatically. The app also keeps the last five generated passwords in a session-only history, provides a strength indicator, and includes a separate **Copy** button. The history is not written to disk. Clear the clipboard after use, particularly on shared computers; other processes running as the same user may be able to read it.

The strength label is a simple heuristic based on length and how many types were selected. It is not a guarantee against guessing or a password audit.

## Tests

```powershell
python -m unittest discover -s tests -v
```
