#!/usr/bin/env python3
"""
Multiplication Torture
A fun pygame game to memorize multiplication facts — whether they want to or not.

Run:
    /home/owendoyaladastra/game-env/bin/python graham_multiplication_game.py

Controls (kid):
    Click one of the 4 answer choices
    M = mute
    Answer 10 questions correctly to unlock and close the game

Parent override:
    Ctrl+Shift+P opens the PIN panel
    Change PARENT_PIN below to your secret code
"""

import json
import math
import os
import random
import sys
import time

os.environ.setdefault("SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS", "0")

import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    import array

WIDTH, HEIGHT = 960, 700
FPS = 60
HIDDEN_WINDOW_POS = "-32000,-32000"
PROGRESS_DIR = os.path.join(os.path.expanduser("~"), ".graham_multiplication")
PROGRESS_FILE = os.path.join(PROGRESS_DIR, "progress.json")

# Colors — bright, kid-friendly space theme
BG = (12, 16, 36)
PANEL = (24, 30, 58)
PANEL_BORDER = (70, 90, 150)
ACCENT = (255, 196, 72)
ACCENT2 = (90, 220, 255)
TEXT = (245, 248, 255)
TEXT_MUTED = (150, 165, 200)
BUTTON = (38, 48, 82)
BUTTON_HOVER = (58, 72, 118)
GOOD = (95, 235, 150)
BAD = (255, 110, 105)
STREAK = (255, 140, 60)
STAR = (255, 230, 90)
ADMIN_BG = (18, 18, 22)
ADMIN_PANEL = (32, 32, 40)
ADMIN_BORDER = (90, 90, 110)
ADMIN_ACCENT = (130, 180, 255)
ADMIN_RED = (200, 45, 50)
ADMIN_RED_HOVER = (235, 65, 70)

# Answers stored encoded so they are not plain text in the app bundle.
_ANSWER_KEY = 0x5A3C


def _enc(value):
    return value ^ _ANSWER_KEY


def _dec(value):
    return value ^ _ANSWER_KEY


# Exact facts from Graham's whiteboard. Listed easiest → hardest.
FACTS = [
    {"display": "8 × 6", "answer": _enc(48), "choices": [_enc(48), _enc(42), _enc(54), _enc(36)]},
    {"display": "16 × 5", "answer": _enc(80), "choices": [_enc(80), _enc(54), _enc(70), _enc(90)]},
    {"display": "27 × 3", "answer": _enc(81), "choices": [_enc(81), _enc(80), _enc(84), _enc(72)]},
    {"display": "21 × 4", "answer": _enc(84), "choices": [_enc(84), _enc(80), _enc(88), _enc(96)]},
    {"display": "12 × 7", "answer": _enc(84), "choices": [_enc(84), _enc(77), _enc(91), _enc(72)]},
    {"display": "15 × 6", "answer": _enc(90), "choices": [_enc(90), _enc(80), _enc(84), _enc(96)]},
    {"display": "13 × 7", "answer": _enc(91), "choices": [_enc(91), _enc(84), _enc(98), _enc(77)]},
    {"display": "23 × 4", "answer": _enc(92), "choices": [_enc(92), _enc(84), _enc(88), _enc(96)]},
    {"display": "25 × 4", "answer": _enc(100), "choices": [_enc(100), _enc(90), _enc(110), _enc(96)]},
    {"display": "48 × 5", "answer": _enc(240), "choices": [_enc(240), _enc(10), _enc(200), _enc(250)]},
]

ROUND_GOAL = 10
MASTERED_NEEDED = 2  # must get a fact right twice before it counts as mastered
GRACE_SECONDS = 10 * 60  # free computer time before math lock appears

# CHANGE THIS to your secret parent PIN (numbers only).
PARENT_PIN = "2847"

def kid_label(name):
    cleaned = (name or "").strip()
    return cleaned if cleaned else "buddy"


def praise_lines(name):
    who = kid_label(name)
    return [
        "BOOM! You crushed it!",
        f"Yes {who}! That's the one!",
        f"Math wizard alert, {who}!",
        f"Nailed it, {who} — keep going!",
        f"Your brain is on fire today, {who}!",
        f"Perfect, {who}! The computer is watching.",
        f"Nice one, {who}! Multiplication doesn't lie.",
    ]


def encourage_lines(name):
    who = kid_label(name)
    return [
        f"Almost, {who}! Break it into smaller steps.",
        f"Not quite, {who} — you've got the next one.",
        f"Good try, {who}! Think: repeated addition.",
        f"Close, {who}! Take a breath and go again.",
        f"Keep going, {who}. No escape without math.",
    ]


def wrong_callouts(name):
    who = kid_label(name)
    return [
        f"Nope, {who}! That wasn't it.",
        f"Wrong answer, {who}! The computer remembers.",
        f"Not today, {who}! Try again on the next one.",
        f"{who}, that pick didn't work.",
        f"Missed it, {who}! Multiplication is undefeated.",
        f"Oof, {who} — wrong button.",
        f"{who}, the math lock is still locked.",
        f"So close, {who}... except not close at all.",
        f"{who}, your computer is waiting for correct answers.",
        f"Negative, {who}! Wrong.",
        f"{who}, you can't guess your way to freedom.",
        f"That answer said no, {who}.",
        f"{who}, the times tables want a rematch.",
        f"Wrong, {who}! But the next question is coming.",
        f"{who}, memorizing beats guessing every time.",
    ]


def wrong_followups(name):
    who = kid_label(name)
    return [
        f"Keep thinking, {who} — no answer shown on purpose.",
        f"Sorry {who}, wrong answers don't count toward escape.",
        f"{who}, use the strategy hint and crush the next one.",
        f"Don't worry {who} — the lock isn't going anywhere.",
        f"{who}, every miss is more multiplication practice.",
        f"Hang in there, {who}. Ten correct answers is the deal.",
        f"{who}, your brain is building muscle right now.",
        f"Next question soon, {who}. Stay sharp.",
    ]


def lock_taunts(name):
    who = kid_label(name)
    return [
        f"Surprise, {who}! Math time!",
        f"{who}, your computer needs 10 multiplication facts first!",
        f"Hey {who} — multiplication before freedom!",
        f"Time's up, {who}! Let's see those times tables!",
    ]

# Strategy hints only — never include the final numeric answer.
HINTS = {
    "8 × 6": "Add 8 six times.",
    "16 × 5": "Add 16 five times, or do 16 × 10 and split it in half.",
    "27 × 3": "Split 27 into 20 and 7, multiply each part by 3, then add.",
    "21 × 4": "Split 21 into 20 and 1, multiply each part by 4, then add.",
    "12 × 7": "Split 12 into 10 and 2, multiply each part by 7, then add.",
    "15 × 6": "Split 15 into 10 and 5, multiply each part by 6, then add.",
    "13 × 7": "Split 13 into 10 and 3, multiply each part by 7, then add.",
    "23 × 4": "Split 23 into 20 and 3, multiply each part by 4, then add.",
    "25 × 4": "Add 25 four times.",
    "48 × 5": "Do 48 × 10 first, then take half.",
}

SAMPLE_RATE = 44100
SOUNDS = {}
SOUND_ENABLED = True


def load_progress():
    try:
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    mastered = set(data.get("mastered", []))
    misses = data.get("misses", {})
    correct_counts = data.get("correct_counts", {})
    kid_name = str(data.get("kid_name", "")).strip()
    return mastered, {k: int(v) for k, v in misses.items()}, {k: int(v) for k, v in correct_counts.items()}, kid_name


def save_progress(mastered, misses, correct_counts, kid_name):
    os.makedirs(PROGRESS_DIR, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(
            {
                "kid_name": kid_name.strip(),
                "mastered": sorted(mastered),
                "misses": misses,
                "correct_counts": correct_counts,
            },
            f,
            indent=2,
        )


def fact_answer(fact):
    return _dec(fact["answer"])


def record_correct(mastered, correct_counts, display):
    correct_counts[display] = correct_counts.get(display, 0) + 1
    if correct_counts[display] >= MASTERED_NEEDED:
        mastered.add(display)
    return display in mastered


def pick_question(mastered, misses, mode, practice_index=0):
    if mode == "step":
        idx = practice_index % len(FACTS)
        return FACTS[idx]

    pool = list(FACTS)
    if mode == "focus":
        weak = [
            fact for fact in pool
            if fact["display"] not in mastered or misses.get(fact["display"], 0) > 0
        ]
        if weak:
            pool = weak
    elif mode == "new":
        unseen = [fact for fact in pool if fact["display"] not in mastered]
        if unseen:
            pool = unseen
    else:
        pool = FACTS[:6] if len(mastered) < 4 else list(FACTS)

    weights = []
    for fact in pool:
        weight = 6 - min(5, FACTS.index(fact))
        if fact["display"] not in mastered:
            weight += 3
        weight += misses.get(fact["display"], 0)
        weights.append(weight)
    return random.choices(pool, weights=weights, k=1)[0]


def choices_for_fact(fact):
    """Return decoded answer buttons for this fact (shuffled each time)."""
    options = [_dec(value) for value in fact["choices"]]
    random.shuffle(options)
    return options


def generate_tone(freq, duration, wave="sine", volume=0.5):
    n = max(1, int(SAMPLE_RATE * duration))
    if HAS_NUMPY:
        t = np.linspace(0, duration, n, endpoint=False)
        if wave == "square":
            w = np.sign(np.sin(2 * np.pi * freq * t))
        else:
            w = np.sin(2 * np.pi * freq * t)
        env = np.ones(n, dtype=np.float32)
        attack = max(1, int(0.01 * SAMPLE_RATE))
        decay = max(1, int(0.15 * SAMPLE_RATE))
        if attack < n:
            env[:attack] = np.linspace(0.0, 1.0, attack)
        if decay < n:
            env[-decay:] = np.linspace(1.0, 0.05, decay)
        return (w * env * volume * 32767).astype(np.int16)
    frames = []
    for i in range(n):
        tt = i / SAMPLE_RATE
        val = math.sin(2 * math.pi * freq * tt)
        env = max(0.0, 1.0 - tt / max(duration, 0.001))
        frames.append(int(val * env * volume * 24000))
    return array.array("h", frames)


def make_sound(freq, dur=0.2, vol=0.45, wave="sine"):
    try:
        snd = pygame.mixer.Sound(buffer=generate_tone(freq, dur, wave, vol))
        snd.set_volume(0.85)
        return snd
    except Exception:
        return None


def make_chord(freqs, dur=0.55, vol=0.35):
    if not HAS_NUMPY:
        return make_sound(freqs[0], dur, vol)
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    wave = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
    env = np.linspace(1.0, 0.05, n)
    audio = (wave * env * vol * 32767).astype(np.int16)
    try:
        snd = pygame.mixer.Sound(buffer=audio)
        snd.set_volume(0.9)
        return snd
    except Exception:
        return None


def init_sounds():
    SOUNDS.clear()
    SOUNDS["click"] = make_sound(900, 0.04, 0.25, "square")
    SOUNDS["key"] = make_sound(760, 0.03, 0.18)
    SOUNDS["good"] = make_chord([523, 659, 784], 0.55, 0.38)
    SOUNDS["bad"] = make_chord([280, 340, 420], 0.45, 0.3)
    SOUNDS["streak"] = make_chord([660, 880, 1100], 0.35, 0.4)
    SOUNDS["win"] = make_chord([440, 554, 659, 880], 0.9, 0.36)


def play_sound(name):
    if not SOUND_ENABLED:
        return
    snd = SOUNDS.get(name)
    if snd:
        try:
            snd.play()
        except Exception:
            pass


def draw_rounded_rect(surf, rect, color, radius=10, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    if center:
        surf.blit(img, img.get_rect(center=(x, y)))
    else:
        surf.blit(img, (x, y))


def draw_stars(surf, count, x, y, size=18):
    for i in range(3):
        col = STAR if i < count else (70, 75, 95)
        cx = x + i * (size + 8)
        points = []
        for p in range(10):
            angle = math.pi / 2 + p * math.pi / 5
            radius = size * 0.45 if p % 2 else size
            points.append((cx + math.cos(angle) * radius, y + math.sin(angle) * radius))
        pygame.draw.polygon(surf, col, points)


class Button:
    def __init__(self, rect, label, action, color=None, danger=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.color = color or ACCENT2
        self.danger = danger
        self.hover = False
        self.enabled = True

    def handle(self, event):
        if not self.enabled:
            return None
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                play_sound("click")
                return self.action
        return None

    def draw(self, surf, font):
        if not self.enabled:
            bg, border, txt = (32, 38, 55), (55, 60, 75), (110, 118, 130)
        elif self.danger:
            bg = ADMIN_RED_HOVER if self.hover else ADMIN_RED
            border = (255, 120, 115)
            txt = TEXT
        elif self.hover:
            bg, border, txt = BUTTON_HOVER, self.color, TEXT
        else:
            bg, border, txt = BUTTON, self.color, TEXT
        draw_rounded_rect(surf, self.rect, bg, 10, 2, border)
        draw_text(surf, self.label, font, txt, self.rect.centerx, self.rect.centery, center=True)


def build_choice_buttons(values):
    buttons = []
    x0, y0, w, h, gap = 120, 400, 350, 68, 16
    for i, value in enumerate(values):
        row, col = divmod(i, 2)
        rect = (x0 + col * (w + gap), y0 + row * (h + gap), w, h)
        buttons.append(Button(rect, str(value), f"pick_{i}", ACCENT2))
    return buttons


def build_pin_keypad():
    buttons = []
    labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "C", "0", "⌫"]
    x0, y0, w, h, gap = 330, 300, 72, 52, 10
    for i, label in enumerate(labels):
        row, col = divmod(i, 3)
        rect = (x0 + col * (w + gap), y0 + row * (h + gap), w, h)
        buttons.append(Button(rect, label, f"pin_{label}", ADMIN_ACCENT))
    buttons.append(Button((330, y0 + 4 * (h + gap), w * 3 + gap * 2, 52), "ENTER", "pin_enter", GOOD))
    return buttons


def build_parent_buttons(kid_name=""):
    who = kid_label(kid_name)
    stats_label = f"View {who}'s Stats" if kid_name else "View Stats"
    x, w, h, gap = 150, 660, 44, 8
    y0 = 188
    return [
        Button((x, y0 + 0 * (h + gap), w, h), "Set Kid's Name", "parent_set_name", GOOD),
        Button((x, y0 + 1 * (h + gap), w, h), stats_label, "parent_stats", ADMIN_ACCENT),
        Button((x, y0 + 2 * (h + gap), w, h), "Set Stats", "parent_set_stats", ACCENT),
        Button((x, y0 + 3 * (h + gap), w, h), "Snooze Math (10 More Minutes)", "parent_snooze", ACCENT2),
        Button((x, y0 + 4 * (h + gap), w, h), "Force Torture Now", "parent_force_lock", STREAK),
        Button((x, y0 + 5 * (h + gap), w, h), "Close Torture", "parent_close_math", danger=True),
        Button((x, y0 + 6 * (h + gap), w, h), "Back to Torture", "parent_close", TEXT_MUTED),
    ]


def setup_hidden_grace_screen():
    """Keep the app alive during grace without showing a visible window."""
    os.environ["SDL_VIDEO_WINDOW_POS"] = HIDDEN_WINDOW_POS
    return pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)


def setup_fullscreen_lock():
    """Fullscreen math lock — reinit display to avoid broken 1x1 scaling."""
    os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
    pygame.display.quit()
    pygame.display.init()
    for flags in (pygame.FULLSCREEN | pygame.SCALED, pygame.FULLSCREEN, (0,)):
        try:
            return pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except pygame.error:
            continue
    return pygame.display.set_mode((WIDTH, HEIGHT))


def setup_windowed():
    os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
    return pygame.display.set_mode((WIDTH, HEIGHT))


def build_name_buttons():
    return [
        Button((330, 360, 300, 52), "Save Name", "name_save", GOOD),
        Button((330, 422, 300, 52), "Back to Parent Panel", "name_back", ADMIN_ACCENT),
    ]


def build_set_stats_buttons():
    x, w, h, gap = 180, 600, 50, 12
    y0 = 220
    return [
        Button((x, y0 + 0 * (h + gap), w, h), "Reset All Progress", "stats_reset_all", BAD),
        Button((x, y0 + 1 * (h + gap), w, h), "Clear Miss Counts", "stats_clear_misses", STREAK),
        Button((x, y0 + 2 * (h + gap), w, h), "Give Free Escape (This Session)", "stats_free_escape", GOOD),
        Button((x, y0 + 3 * (h + gap), w, h), "Back to Parent Panel", "stats_back", ADMIN_ACCENT),
    ]


def main():
    pygame.init()
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
    screen = setup_hidden_grace_screen()
    pygame.display.set_caption("Multiplication Torture")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("DejaVu Sans", 16)
    font_med = pygame.font.SysFont("DejaVu Sans", 20)
    font_big = pygame.font.SysFont("DejaVu Sans", 28)
    font_huge = pygame.font.SysFont("DejaVu Sans", 54)
    font_title = pygame.font.SysFont("DejaVu Sans", 42, bold=True)

    init_sounds()

    state = "grace"
    mode = "practice"
    math_lock_active = False
    escape_unlocked = False
    lock_message = ""
    lock_message_until = 0.0
    grace_deadline = time.time() + GRACE_SECONDS
    pin_input = ""
    pin_message = ""
    pin_message_until = 0.0
    parent_view = "main"
    return_state = "grace"
    pin_keypad = build_pin_keypad()
    set_stats_buttons = build_set_stats_buttons()
    parent_notice = ""
    parent_notice_until = 0.0
    mastered, misses, correct_counts, kid_name = load_progress()
    parent_buttons = build_parent_buttons(kid_name)
    name_buttons = build_name_buttons()
    name_input = kid_name
    name_message = ""
    name_message_until = 0.0
    lock_taunt = ""
    lock_taunt_until = 0.0
    score = 0
    streak = 0
    best_streak = 0
    questions_done = 0
    practice_index = 0
    current_display = ""
    current_answer = 0
    current_choices = []
    choice_buttons = []
    feedback = ""
    feedback_good = False
    show_feedback = False
    feedback_until = 0.0
    session_correct = 0
    stars_earned = 0
    particles = []
    wrong_pick = None
    wrong_subtext = ""

    def grace_remaining():
        return max(0, int(grace_deadline - time.time()))

    def can_escape():
        return state == "parent_panel" or (escape_unlocked and state == "results")

    def block_escape():
        nonlocal lock_message, lock_message_until
        if state == "grace":
            remaining = grace_remaining()
            mins, secs = divmod(remaining, 60)
            lock_message = f"Math lock starts in {mins}:{secs:02d}. Finish your 10 free minutes first."
        else:
            remaining = max(0, ROUND_GOAL - questions_done)
            who = kid_label(kid_name)
            lock_message = f"Sorry {who}! Get {remaining} more correct answer{'s' if remaining != 1 else ''} to escape."
        lock_message_until = time.time() + 2.0
        play_sound("bad")

    def refresh_parent_buttons():
        nonlocal parent_buttons
        parent_buttons = build_parent_buttons(kid_name)

    def update_window_title():
        who = kid_label(kid_name)
        if math_lock_active:
            pygame.display.set_caption(f"Multiplication Torture — {who} needs 10 correct")
        else:
            pygame.display.set_caption("Multiplication Torture")

    update_window_title()

    def activate_math_lock():
        nonlocal state, screen, math_lock_active, return_state, lock_taunt, lock_taunt_until
        screen = setup_fullscreen_lock()
        update_window_title()
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(True)
        math_lock_active = True
        return_state = "play"
        lock_taunt = random.choice(lock_taunts(kid_name))
        lock_taunt_until = time.time() + 4.5
        start_round("practice")

    def open_pin_entry():
        nonlocal state, pin_input, pin_message, return_state, screen
        if state in ("parent_panel", "parent_stats", "pin_entry"):
            return
        return_state = state
        state = "pin_entry"
        pin_input = ""
        pin_message = ""
        screen = setup_windowed()
        pygame.mouse.set_visible(True)

    def close_pin_entry():
        nonlocal state, pin_input, screen
        state = return_state
        pin_input = ""
        if state == "grace" and not math_lock_active:
            screen = setup_hidden_grace_screen()
            pygame.mouse.set_visible(False)
        elif state == "play":
            screen = setup_fullscreen_lock()
            pygame.mouse.set_visible(True)

    def submit_pin():
        nonlocal state, pin_input, pin_message, pin_message_until, parent_view, screen, name_input
        if pin_input == PARENT_PIN:
            play_sound("good")
            screen = setup_windowed()
            pygame.mouse.set_visible(True)
            pin_input = ""
            pin_message = ""
            pygame.event.set_grab(False)
            if kid_name:
                state = "parent_panel"
                parent_view = "main"
            else:
                state = "parent_set_name"
                name_input = ""
                name_message = "Enter your kid's name so the math lock can use it."
                name_message_until = time.time() + 4.0
        else:
            play_sound("bad")
            pin_message = "Wrong PIN."
            pin_message_until = time.time() + 1.5
            pin_input = ""

    def close_parent_panel():
        nonlocal state, parent_view, screen
        parent_view = "main"
        if math_lock_active and not escape_unlocked:
            state = "play"
            screen = setup_fullscreen_lock()
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(True)
        elif escape_unlocked:
            state = "results"
            screen = setup_fullscreen_lock()
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            state = "grace"
            screen = setup_hidden_grace_screen()
            pygame.mouse.set_visible(False)

    def show_parent_notice(message):
        nonlocal parent_notice, parent_notice_until
        parent_notice = message
        parent_notice_until = time.time() + 2.5

    def snooze_math():
        nonlocal state, grace_deadline, math_lock_active, escape_unlocked, screen
        grace_deadline = time.time() + GRACE_SECONDS
        math_lock_active = False
        escape_unlocked = False
        state = "grace"
        screen = setup_hidden_grace_screen()
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(False)
        show_parent_notice("Math snoozed for 10 more minutes.")

    def force_math_lock_now():
        if not math_lock_active:
            activate_math_lock()
        close_parent_panel()

    def reset_all_stats():
        nonlocal mastered, misses, correct_counts
        mastered, misses, correct_counts = set(), {}, {}
        save_progress(mastered, misses, correct_counts, kid_name)
        show_parent_notice("All progress reset.")

    def clear_miss_counts():
        nonlocal misses
        misses = {}
        save_progress(mastered, misses, correct_counts, kid_name)
        show_parent_notice("Miss counts cleared.")

    def grant_free_escape():
        nonlocal escape_unlocked, state, screen
        escape_unlocked = True
        state = "results"
        screen = setup_fullscreen_lock()
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        show_parent_notice(f"{kid_label(kid_name)} can close the math lock now.")

    def save_kid_name():
        nonlocal kid_name, name_input, state, name_message, name_message_until
        cleaned = name_input.strip()
        if not cleaned:
            name_message = "Type a name first."
            name_message_until = time.time() + 2.0
            play_sound("bad")
            return
        kid_name = cleaned[:20]
        name_input = kid_name
        save_progress(mastered, misses, correct_counts, kid_name)
        refresh_parent_buttons()
        update_window_title()
        show_parent_notice(f"Saved! The game will now call them {kid_name}.")
        state = "parent_panel"
        play_sound("good")

    def new_question():
        nonlocal current_display, current_answer, current_choices, choice_buttons, wrong_pick
        fact = pick_question(mastered, misses, mode, practice_index)
        current_display = fact["display"]
        current_answer = fact_answer(fact)
        current_choices = choices_for_fact(fact)
        choice_buttons = build_choice_buttons(current_choices)
        wrong_pick = None

    def start_round(selected_mode):
        nonlocal state, mode, score, streak, best_streak, questions_done
        nonlocal show_feedback, session_correct, stars_earned, practice_index, wrong_pick
        mode = selected_mode
        score = 0
        streak = 0
        best_streak = 0
        questions_done = 0
        practice_index = 0
        session_correct = 0
        stars_earned = 0
        show_feedback = False
        wrong_pick = None
        state = "play"
        new_question()

    def submit_answer(guess):
        nonlocal show_feedback, feedback, feedback_good, feedback_until, wrong_subtext
        nonlocal score, streak, best_streak, questions_done, session_correct, stars_earned
        nonlocal mastered, misses, correct_counts, state, practice_index, wrong_pick, escape_unlocked
        if show_feedback:
            return

        correct = guess == current_answer
        show_feedback = True
        feedback_good = correct
        feedback_until = time.time() + (1.2 if correct else 2.0)
        practice_index += 1

        if correct:
            play_sound("streak" if streak >= 2 else "good")
            questions_done += 1
            score += 1
            streak += 1
            best_streak = max(best_streak, streak)
            session_correct += 1
            feedback = random.choice(praise_lines(kid_name))
            wrong_subtext = ""
            was_mastered = current_display in mastered
            if record_correct(mastered, correct_counts, current_display):
                if not was_mastered:
                    stars_earned += 1
            misses[current_display] = max(0, misses.get(current_display, 0) - 1)
            for _ in range(12):
                particles.append(
                    {
                        "x": WIDTH // 2 + random.randint(-120, 120),
                        "y": 220,
                        "vx": random.uniform(-2.5, 2.5),
                        "vy": random.uniform(-4.5, -1.5),
                        "life": random.uniform(0.5, 1.0),
                        "color": random.choice([GOOD, ACCENT, STAR, ACCENT2]),
                    }
                )
        else:
            play_sound("bad")
            streak = 0
            wrong_pick = guess
            misses[current_display] = misses.get(current_display, 0) + 1
            callout = random.choice(wrong_callouts(kid_name))
            encourage = random.choice(encourage_lines(kid_name))
            feedback = f"{callout} {encourage}"
            wrong_subtext = random.choice(wrong_followups(kid_name))

        save_progress(mastered, misses, correct_counts, kid_name)

        if correct and questions_done >= ROUND_GOAL:
            play_sound("win")
            state = "results"
            escape_unlocked = True
            pygame.event.set_grab(False)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        if state == "grace" and not math_lock_active and time.time() >= grace_deadline:
            activate_math_lock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if can_escape():
                    running = False
                elif state == "parent_panel":
                    close_parent_panel()
                else:
                    block_escape()
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if (
                    event.key == pygame.K_p
                    and (mods & pygame.KMOD_CTRL)
                    and (mods & pygame.KMOD_SHIFT)
                ):
                    open_pin_entry()
                elif event.key == pygame.K_ESCAPE:
                    if state in ("pin_entry", "parent_stats", "parent_set_stats", "parent_set_name"):
                        if state == "parent_stats":
                            state = "parent_panel"
                            parent_view = "main"
                        elif state == "parent_set_stats":
                            state = "parent_panel"
                        elif state == "parent_set_name":
                            state = "parent_panel"
                            name_input = kid_name
                        else:
                            close_pin_entry()
                    elif state == "parent_panel":
                        close_parent_panel()
                    elif can_escape():
                        running = False
                    else:
                        block_escape()
                elif event.key == pygame.K_m and state in ("play", "results", "grace"):
                    global SOUND_ENABLED
                    SOUND_ENABLED = not SOUND_ENABLED
                elif state == "pin_entry":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        submit_pin()
                    elif event.key == pygame.K_BACKSPACE:
                        pin_input = pin_input[:-1]
                    elif event.unicode.isdigit() and len(pin_input) < len(PARENT_PIN):
                        pin_input += event.unicode
                elif state == "parent_set_name":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        save_kid_name()
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    elif event.unicode.isalpha() or event.unicode in (" ", "-", "'"):
                        if len(name_input) < 20:
                            name_input += event.unicode
                elif show_feedback and state == "play" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    show_feedback = False
                    if questions_done >= ROUND_GOAL:
                        play_sound("win")
                        state = "results"
                    else:
                        new_question()

            if state == "pin_entry":
                for btn in pin_keypad:
                    action = btn.handle(event)
                    if not action:
                        continue
                    if action == "pin_enter":
                        submit_pin()
                    elif action == "pin_C":
                        pin_input = ""
                    elif action == "pin_⌫":
                        pin_input = pin_input[:-1]
                    elif action.startswith("pin_"):
                        pin_input += action.split("_", 1)[1]
                        if len(pin_input) > len(PARENT_PIN):
                            pin_input = pin_input[: len(PARENT_PIN)]

            elif state == "parent_panel":
                for btn in parent_buttons:
                    action = btn.handle(event)
                    if action == "parent_set_name":
                        state = "parent_set_name"
                        name_input = kid_name
                    elif action == "parent_stats":
                        state = "parent_stats"
                    elif action == "parent_set_stats":
                        state = "parent_set_stats"
                    elif action == "parent_snooze":
                        snooze_math()
                        state = "parent_panel"
                    elif action == "parent_force_lock":
                        force_math_lock_now()
                    elif action == "parent_close_math":
                        running = False
                    elif action == "parent_close":
                        close_parent_panel()

            elif state == "parent_set_name":
                for btn in name_buttons:
                    action = btn.handle(event)
                    if action == "name_save":
                        save_kid_name()
                    elif action == "name_back":
                        state = "parent_panel"
                        name_input = kid_name

            elif state == "parent_set_stats":
                for btn in set_stats_buttons:
                    action = btn.handle(event)
                    if action == "stats_reset_all":
                        reset_all_stats()
                    elif action == "stats_clear_misses":
                        clear_miss_counts()
                    elif action == "stats_free_escape":
                        grant_free_escape()
                    elif action == "stats_back":
                        state = "parent_panel"

            elif state == "parent_stats" and event.type == pygame.MOUSEBUTTONDOWN:
                state = "parent_panel"
                parent_view = "main"

            elif state == "play":
                for btn in choice_buttons:
                    action = btn.handle(event)
                    if not action:
                        continue
                    if action.startswith("pick_"):
                        if show_feedback:
                            continue
                        idx = int(action.split("_", 1)[1])
                        submit_answer(current_choices[idx])

                if event.type == pygame.MOUSEBUTTONDOWN and show_feedback:
                    show_feedback = False
                    if state == "play":
                        if questions_done >= ROUND_GOAL:
                            play_sound("win")
                            state = "results"
                        else:
                            new_question()

        if state == "play" and show_feedback and time.time() >= feedback_until:
            show_feedback = False
            if questions_done >= ROUND_GOAL:
                play_sound("win")
                state = "results"
            else:
                new_question()

        particles = [
            {**p, "x": p["x"] + p["vx"], "y": p["y"] + p["vy"], "vy": p["vy"] + 0.12, "life": p["life"] - dt}
            for p in particles
            if p["life"] > 0
        ]

        if state == "pin_entry":
            screen.fill(ADMIN_BG)
            draw_rounded_rect(screen, pygame.Rect(180, 80, WIDTH - 360, 520), ADMIN_PANEL, 14, 2, ADMIN_BORDER)
            draw_text(screen, "PARENT PIN", font_title, ADMIN_ACCENT, WIDTH // 2, 130, center=True)
            draw_text(screen, "Enter your override code", font_med, TEXT_MUTED, WIDTH // 2, 175, center=True)
            masked = "•" * len(pin_input) + "○" * (len(PARENT_PIN) - len(pin_input))
            draw_rounded_rect(screen, pygame.Rect(300, 220, 360, 52), (20, 20, 28), 10, 2, ADMIN_ACCENT)
            draw_text(screen, masked, font_big, TEXT, WIDTH // 2, 246, center=True)
            if pin_message and time.time() < pin_message_until:
                draw_text(screen, pin_message, font_med, BAD, WIDTH // 2, 280, center=True)
            for btn in pin_keypad:
                btn.draw(screen, font_med)
            draw_text(screen, "ESC = cancel", font, TEXT_MUTED, WIDTH // 2, 560, center=True)

        elif state == "parent_panel":
            screen.fill(ADMIN_BG)
            draw_rounded_rect(screen, pygame.Rect(100, 55, WIDTH - 200, 580), ADMIN_PANEL, 14, 2, ADMIN_BORDER)
            draw_text(screen, "PARENT CONTROL PANEL", font_title, ADMIN_ACCENT, WIDTH // 2, 100, center=True)
            draw_text(screen, "Outside the math game — parents only", font_med, TEXT_MUTED, WIDTH // 2, 140, center=True)
            if kid_name:
                draw_text(screen, f"Kid's name: {kid_name}", font_med, GOOD, WIDTH // 2, 160, center=True)
            else:
                draw_text(screen, "Kid's name not set yet", font_med, BAD, WIDTH // 2, 160, center=True)
            if math_lock_active:
                status = f"Math lock active — {questions_done}/{ROUND_GOAL} correct"
            else:
                mins, secs = divmod(grace_remaining(), 60)
                status = f"Grace period — math starts in {mins}:{secs:02d}"
            draw_text(screen, status, font_med, ACCENT2, WIDTH // 2, 182, center=True)
            draw_text(screen, f"Mastered facts: {len(mastered)}/{len(FACTS)}", font, TEXT_MUTED, WIDTH // 2, 202, center=True)
            for btn in parent_buttons:
                btn.draw(screen, font_med)
            if parent_notice and time.time() < parent_notice_until:
                draw_text(screen, parent_notice, font_med, GOOD, WIDTH // 2, 548, center=True)
            draw_text(screen, "Ctrl+Shift+P opens this panel anytime", font, TEXT_MUTED, WIDTH // 2, 620, center=True)

        elif state == "parent_set_stats":
            screen.fill(ADMIN_BG)
            draw_rounded_rect(screen, pygame.Rect(120, 70, WIDTH - 240, 500), ADMIN_PANEL, 14, 2, ADMIN_BORDER)
            draw_text(screen, "SET STATS", font_title, ACCENT, WIDTH // 2, 120, center=True)
            draw_text(screen, f"Parent-only tools for {kid_label(kid_name)}'s progress", font_med, TEXT_MUTED, WIDTH // 2, 165, center=True)
            draw_text(screen, f"{kid_label(kid_name)} cannot see or access this screen", font, BAD, WIDTH // 2, 195, center=True)
            for btn in set_stats_buttons:
                btn.draw(screen, font_med)
            if parent_notice and time.time() < parent_notice_until:
                draw_text(screen, parent_notice, font_med, GOOD, WIDTH // 2, 470, center=True)

        elif state == "parent_set_name":
            screen.fill(ADMIN_BG)
            draw_rounded_rect(screen, pygame.Rect(160, 90, WIDTH - 320, 420), ADMIN_PANEL, 14, 2, ADMIN_BORDER)
            draw_text(screen, "SET KID'S NAME", font_title, GOOD, WIDTH // 2, 140, center=True)
            draw_text(screen, "The math lock will say this name out loud in messages", font_med, TEXT_MUTED, WIDTH // 2, 185, center=True)
            draw_rounded_rect(screen, pygame.Rect(220, 250, 520, 56), (20, 20, 28), 10, 2, GOOD)
            draw_text(screen, name_input or "Type a name...", font_big, TEXT if name_input else TEXT_MUTED, WIDTH // 2, 278, center=True)
            if name_message and time.time() < name_message_until:
                draw_text(screen, name_message, font_med, ACCENT2, WIDTH // 2, 320, center=True)
            for btn in name_buttons:
                btn.draw(screen, font_med)
            draw_text(screen, "Letters, spaces, and apostrophes only", font, TEXT_MUTED, WIDTH // 2, 500, center=True)

        elif state == "parent_stats":
            screen.fill(ADMIN_BG)
            draw_text(screen, f"{kid_label(kid_name)}'s Stats (Parent Only)", font_title, ADMIN_ACCENT, WIDTH // 2, 42, center=True)
            draw_text(screen, "Full answers shown here only — not in the kid's game", font, TEXT_MUTED, WIDTH // 2, 78, center=True)
            y = 110
            for fact in FACTS:
                display = fact["display"]
                answer = fact_answer(fact)
                done = display in mastered
                rect = pygame.Rect(80, y, WIDTH - 160, 38)
                draw_rounded_rect(screen, rect, (28, 28, 36), 8, 1, GOOD if done else ADMIN_BORDER)
                progress = correct_counts.get(display, 0)
                miss = misses.get(display, 0)
                label = f"{display} = {answer if done else '???'}"
                if not done and progress:
                    label += f"  ({progress}/{MASTERED_NEEDED})"
                draw_text(screen, label, font, TEXT, 95, y + 10)
                if done:
                    draw_text(screen, "★", font_big, STAR, rect.right - 30, y + 6)
                if miss:
                    draw_text(screen, f"missed {miss}×", font, BAD, rect.right - 110, y + 12)
                y += 44
            draw_rounded_rect(screen, pygame.Rect(300, HEIGHT - 70, 360, 42), BUTTON, 8, 2, ADMIN_ACCENT)
            draw_text(screen, "Back to Parent Panel (click or ESC)", font_med, TEXT, WIDTH // 2, HEIGHT - 49, center=True)

        elif state == "play":
            screen.fill(BG)
            pygame.draw.circle(screen, (40, 55, 110), (820, 90), 48)
            pygame.draw.circle(screen, (70, 90, 150), (790, 78), 14)
            pygame.draw.circle(screen, (255, 170, 90), (120, 110), 22)
            for i in range(40):
                pygame.draw.circle(screen, (255, 255, 255), (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
            draw_rounded_rect(screen, pygame.Rect(220, 12, WIDTH - 440, 34), (48, 20, 28), 8, 2, BAD)
            if lock_taunt and time.time() < lock_taunt_until:
                draw_rounded_rect(screen, pygame.Rect(120, 8, WIDTH - 240, 40), (70, 20, 28), 8, 2, BAD)
                draw_text(screen, lock_taunt, font_med, BAD, WIDTH // 2, 28, center=True)
            draw_text(
                screen,
                f"{kid_label(kid_name).upper()}, answer {ROUND_GOAL} correctly to escape  ({questions_done}/{ROUND_GOAL})",
                font_med,
                BAD,
                WIDTH // 2,
                58,
                center=True,
            )
            draw_text(screen, f"Score: {score}", font_med, GOOD, 50, 62)
            draw_text(screen, f"Streak: {streak}", font_med, STREAK, 180, 62)
            draw_text(
                screen,
                f"Question {min(questions_done + (0 if show_feedback and feedback_good else 1), ROUND_GOAL)}/{ROUND_GOAL}",
                font_med,
                TEXT,
                340,
                62,
            )
            card = pygame.Rect(80, 110, WIDTH - 160, 200)
            draw_rounded_rect(screen, card, PANEL, 14, 2, ACCENT2)
            draw_text(screen, "What is", font_med, TEXT_MUTED, card.centerx, 145, center=True)
            draw_text(screen, current_display + " ?", font_huge, ACCENT, card.centerx, 205, center=True)

            hint = HINTS.get(current_display, "")
            draw_rounded_rect(screen, pygame.Rect(110, 255, WIDTH - 220, 42), (18, 24, 42), 8, 1, PANEL_BORDER)
            draw_text(screen, "Strategy: " + hint, font_med, ACCENT, WIDTH // 2, 276, center=True)

            if show_feedback:
                fb_color = GOOD if feedback_good else BAD
                fb_h = 52 if not feedback_good else 36
                draw_rounded_rect(
                    screen,
                    pygame.Rect(110, 310, WIDTH - 220, fb_h),
                    (20, 30, 28) if feedback_good else (35, 20, 24),
                    8,
                    1,
                    fb_color,
                )
                if feedback_good:
                    draw_text(screen, feedback[:85], font, fb_color, 120, 322)
                    subtext = "Next question coming up..."
                else:
                    draw_text(screen, feedback[:90], font, fb_color, 120, 320)
                    if len(feedback) > 90:
                        draw_text(screen, feedback[90:180], font, fb_color, 120, 338)
                    subtext = wrong_subtext
                draw_text(screen, subtext, font, TEXT_MUTED if feedback_good else BAD, WIDTH // 2, 368, center=True)

            label_y = 332 if not show_feedback else 358
            draw_text(screen, "Pick the answer:", font_med, TEXT, WIDTH // 2, label_y, center=True)
            for i, btn in enumerate(choice_buttons):
                btn.enabled = not show_feedback
                if show_feedback and not feedback_good and wrong_pick is not None and current_choices[i] == wrong_pick:
                    btn.color = BAD
                else:
                    btn.color = ACCENT2
                btn.draw(screen, font_big)

            if lock_message and time.time() < lock_message_until:
                draw_rounded_rect(screen, pygame.Rect(180, 56, WIDTH - 360, 30), (55, 18, 24), 6, 1, BAD)
                draw_text(screen, lock_message, font, BAD, WIDTH // 2, 71, center=True)

            for p in particles:
                pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 4)

            draw_text(screen, "ESC and close button are disabled until you finish", font, TEXT_MUTED, WIDTH // 2, HEIGHT - 24, center=True)

        elif state == "results":
            screen.fill(BG)
            draw_text(screen, f"You Escaped, {kid_label(kid_name)}!", font_title, GOOD, WIDTH // 2, 120, center=True)
            draw_text(screen, f"Nice work, {kid_label(kid_name)}!", font_big, ACCENT, WIDTH // 2, 180, center=True)
            draw_rounded_rect(screen, pygame.Rect(280, 260, 400, 48), BUTTON, 10, 2, GOOD)
            draw_text(screen, "Press ESC to use your computer", font_med, TEXT, WIDTH // 2, 284, center=True)

        if state == "grace":
            pygame.event.pump()
        else:
            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()