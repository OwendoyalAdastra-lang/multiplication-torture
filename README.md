# Graham's Multiplication Blast

A way to force your kids to memorize multiplication facts — totally not made by kids 😉😉

A Linux pygame app that quietly runs at login, waits 10 minutes, then fullscreen-locks the computer until your kid answers 10 multiplication problems correctly. Built for real whiteboard homework facts — with parent override, cheat-proofing, and progress tracking.

## Features

- **Startup lock** — installs as a login autostart app
- **10-minute grace period** — then math slams on fullscreen
- **10 correct answers to escape** — wrong answers don't count
- **Cheat-proof** — no answer leaks, one try per question, encoded answers
- **Parent panel** — `Ctrl+Shift+P` + PIN (default `2847`, change in code)
  - View stats, set/reset progress, snooze math, force lock, close math (red button)

## Quick start

```bash
# Python 3 + pygame + pyinstaller
pip install pygame pyinstaller numpy

# Run directly
python3 graham_multiplication_game.py

# Build standalone app
python3 build_graham_math_app.py

# Install as login startup app (Linux)
./install_graham_startup.sh
```

## Set your kid's name

1. Press `Ctrl+Shift+P` and enter your parent PIN
2. Click **Set Kid's Name** — the game will use it in every message

Saved in `~/.graham_multiplication/progress.json` as `kid_name`.

## Parent PIN

Edit `PARENT_PIN` near the top of `graham_multiplication_game.py`, then rebuild:

```bash
python3 build_graham_math_app.py
./install_graham_startup.sh
```

## Remove autostart

```bash
./uninstall_graham_startup.sh
```

## Progress saves to

`~/.graham_multiplication/progress.json`

## Made for

Graham. Sorry, Graham.