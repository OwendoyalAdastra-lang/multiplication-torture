# Multiplication Torture

A way to force your kids to memorize multiplication facts — totally not made by kids 😉😉

## What This SUPER COOL PROGRAM Is Supposed To Do :DDDDDD

Imagine your kid logs into their computer, vibes for **10 glorious minutes**, thinks they're free… and then **BAM** — fullscreen math prison.

This **EXTREMELY LEGIT** and **DEFINITELY NOT EVIL** educational software:

1. **Sneaks onto the computer at startup** like a multiplication ninja 🥷
2. **Hides in the shadows** for 10 minutes so your kid lowers their guard
3. **ERUPTS onto the screen in fullscreen** and says their name like a game show host who hates fun
4. **Refuses to let them leave** until they get **10 multiplication questions RIGHT** (guessing all 4 buttons doesn't work — we thought of that)
5. **Calls them out by name when they're wrong** — *"Nope, Graham! The computer remembers."*
6. **Does NOT give away answers** because that would defeat the whole beautiful suffering
7. **Lets parents cheat** with a secret PIN panel because adults deserve shortcuts

**The goal?** Your kid memorizes times tables so they can use their computer faster.

**The reality?** Your kid stares at `48 × 5` like it's written in ancient alien script while you sip your drink knowing you built a startup app that launches at login.

**Is it fair?** Debatable.

**Is it effective?** Terrifyingly yes.

**Was it made by kids?** Totally not. 😉😉

---

A Linux pygame app built for real whiteboard homework facts — with parent override, cheat-proofing, personalized name taunts, and progress tracking.

## Features

- **Startup lock** — installs as a login autostart app
- **10-minute grace period** — then math slams on fullscreen
- **10 correct answers to escape** — wrong answers don't count
- **Cheat-proof** — no answer leaks, one try per question, encoded answers
- **Parent panel** — `Ctrl+Shift+P` + PIN (default `2847`, change in code)
  - View stats, set kid's name, set/reset progress, snooze torture, force lock, close torture (red button)

## Quick start (Electron — recommended, no Python needed)

```bash
cd multiplication-torture   # or graham-multiplication-blast clone folder
chmod +x launch-torture.sh install_graham_startup.sh
./launch-torture.sh         # installs npm deps on first run, then launches

# Install as login startup app (Linux)
./install_graham_startup.sh
```

Uses **Electron** (Chromium) instead of Python/pygame — fixes display glitches like the white-line bug.

### Legacy Python version

```bash
pip install pygame pyinstaller numpy
python3 graham_multiplication_game.py
python3 build_graham_math_app.py
```

## Set your kid's name

1. Press `Ctrl+Shift+P` and enter your parent PIN
2. Click **Set Kid's Name** — the game will use it in every message

Saved in `~/.graham_multiplication/progress.json` as `kid_name`.

## Parent PIN

Edit `PARENT_PIN` in `app/app.js` (Electron) or `graham_multiplication_game.py` (Python legacy), then restart:

```bash
python3 build_graham_math_app.py
./install_graham_startup.sh
```

## ChromeOS / shelf toolbar note

If Graham can still reach the bottom toolbar, the app will **yank focus back** every fraction of a second while locked. For maximum lockdown on a Chromebook, also set the shelf to **Always hide** in ChromeOS settings.

## Remove autostart

```bash
./uninstall_graham_startup.sh
```

## Progress saves to

`~/.graham_multiplication/progress.json`

## Made for

Graham. Sorry, Graham.