const ANSWER_KEY = 0x5a3c;
const ROUND_GOAL = 10;
const MASTERED_NEEDED = 2;
const PARENT_PIN = "2847";

const FACTS = [
  { display: "8 × 6", answer: enc(48), choices: [enc(48), enc(42), enc(54), enc(36)] },
  { display: "16 × 5", answer: enc(80), choices: [enc(80), enc(54), enc(70), enc(90)] },
  { display: "27 × 3", answer: enc(81), choices: [enc(81), enc(80), enc(84), enc(72)] },
  { display: "21 × 4", answer: enc(84), choices: [enc(84), enc(80), enc(88), enc(96)] },
  { display: "12 × 7", answer: enc(84), choices: [enc(84), enc(77), enc(91), enc(72)] },
  { display: "15 × 6", answer: enc(90), choices: [enc(90), enc(80), enc(84), enc(96)] },
  { display: "13 × 7", answer: enc(91), choices: [enc(91), enc(84), enc(98), enc(77)] },
  { display: "23 × 4", answer: enc(92), choices: [enc(92), enc(84), enc(88), enc(96)] },
  { display: "25 × 4", answer: enc(100), choices: [enc(100), enc(90), enc(110), enc(96)] },
  { display: "48 × 5", answer: enc(240), choices: [enc(240), enc(10), enc(200), enc(250)] },
];

const HINTS = {
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
};

function enc(v) { return v ^ ANSWER_KEY; }
function dec(v) { return v ^ ANSWER_KEY; }
function kidLabel(name) { return (name || "").trim() || "buddy"; }
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const praiseLines = (n) => {
  const w = kidLabel(n);
  return [
    "BOOM! You crushed it!",
    `Yes ${w}! That's the one!`,
    `Math wizard alert, ${w}!`,
    `Nailed it, ${w} — keep going!`,
    `Your brain is on fire today, ${w}!`,
    `Perfect, ${w}! The computer is watching.`,
    `Nice one, ${w}! Multiplication doesn't lie.`,
  ];
};

const encourageLines = (n) => {
  const w = kidLabel(n);
  return [
    `Almost, ${w}! Break it into smaller steps.`,
    `Not quite, ${w} — you've got the next one.`,
    `Good try, ${w}! Think: repeated addition.`,
    `Close, ${w}! Take a breath and go again.`,
    `Keep going, ${w}. No escape without math.`,
  ];
};

const wrongCallouts = (n) => {
  const w = kidLabel(n);
  return [
    `Nope, ${w}! That wasn't it.`,
    `Wrong answer, ${w}! The computer remembers.`,
    `Not today, ${w}! Try again on the next one.`,
    `${w}, that pick didn't work.`,
    `Missed it, ${w}! Multiplication is undefeated.`,
    `Oof, ${w} — wrong button.`,
    `${w}, the math lock is still locked.`,
    `So close, ${w}... except not close at all.`,
    `${w}, your computer is waiting for correct answers.`,
    `Negative, ${w}! Wrong.`,
    `${w}, you can't guess your way to freedom.`,
    `That answer said no, ${w}.`,
    `${w}, the times tables want a rematch.`,
    `Wrong, ${w}! But the next question is coming.`,
    `${w}, memorizing beats guessing every time.`,
  ];
};

const wrongFollowups = (n) => {
  const w = kidLabel(n);
  return [
    `Keep thinking, ${w} — no answer shown on purpose.`,
    `Sorry ${w}, wrong answers don't count toward escape.`,
    `${w}, use the strategy hint and crush the next one.`,
    `Don't worry ${w} — the lock isn't going anywhere.`,
    `${w}, every miss is more multiplication practice.`,
    `Hang in there, ${w}. Ten correct answers is the deal.`,
    `${w}, your brain is building muscle right now.`,
    `Next question soon, ${w}. Stay sharp.`,
  ];
};

const lockTaunts = (n) => {
  const w = kidLabel(n);
  return [
    `Surprise, ${w}! Math time!`,
    `${w}, your computer needs 10 multiplication facts first!`,
    `Hey ${w} — multiplication before freedom!`,
    `Time's up, ${w}! Let's see those times tables!`,
  ];
};

const state = {
  view: "play",
  kidName: "",
  mastered: new Set(),
  misses: {},
  correctCounts: {},
  score: 0,
  streak: 0,
  bestStreak: 0,
  questionsDone: 0,
  sessionCorrect: 0,
  starsEarned: 0,
  currentFact: null,
  currentChoices: [],
  showFeedback: false,
  feedbackGood: false,
  feedback: "",
  feedbackSub: "",
  wrongPick: null,
  lockTaunt: "",
  lockTauntUntil: 0,
  pinInput: "",
  pinMessage: "",
  nameInput: "",
  parentNotice: "",
  parentNoticeUntil: 0,
  escaped: false,
};

const root = document.getElementById("app");

async function loadAll() {
  const data = await window.tortureAPI.loadProgress();
  state.kidName = data.kid_name || "";
  state.mastered = new Set(data.mastered || []);
  state.misses = data.misses || {};
  state.correctCounts = data.correct_counts || {};
}

async function saveAll() {
  await window.tortureAPI.saveProgress({
    kid_name: state.kidName,
    mastered: [...state.mastered],
    misses: state.misses,
    correct_counts: state.correctCounts,
  });
}

function pickQuestion() {
  const pool = state.mastered.size < 4 ? FACTS.slice(0, 6) : [...FACTS];
  const weights = pool.map((fact) => {
    let w = 6 - Math.min(5, FACTS.indexOf(fact));
    if (!state.mastered.has(fact.display)) w += 3;
    w += state.misses[fact.display] || 0;
    return w;
  });
  const total = weights.reduce((a, b) => a + b, 0);
  let r = Math.random() * total;
  for (let i = 0; i < pool.length; i++) {
    r -= weights[i];
    if (r <= 0) return pool[i];
  }
  return pool[0];
}

function newQuestion() {
  state.currentFact = pickQuestion();
  state.currentChoices = shuffle(state.currentFact.choices.map(dec));
  state.showFeedback = false;
  state.wrongPick = null;
  render();
}

function recordCorrect(display) {
  state.correctCounts[display] = (state.correctCounts[display] || 0) + 1;
  if (state.correctCounts[display] >= MASTERED_NEEDED) state.mastered.add(display);
  state.misses[display] = Math.max(0, (state.misses[display] || 0) - 1);
}

function submitAnswer(guess) {
  if (state.showFeedback) return;
  const answer = dec(state.currentFact.answer);
  const correct = guess === answer;
  state.showFeedback = true;
  state.feedbackGood = correct;

  if (correct) {
    state.questionsDone += 1;
    state.score += 1;
    state.streak += 1;
    state.bestStreak = Math.max(state.bestStreak, state.streak);
    state.sessionCorrect += 1;
    state.feedback = pick(praiseLines(state.kidName));
    state.feedbackSub = "Next question coming up...";
    const wasMastered = state.mastered.has(state.currentFact.display);
    recordCorrect(state.currentFact.display);
    if (!wasMastered && state.mastered.has(state.currentFact.display)) state.starsEarned += 1;
    setTimeout(() => {
      if (state.questionsDone >= ROUND_GOAL) {
        state.view = "results";
        state.escaped = true;
        window.tortureAPI.notifyEscaped();
        render();
      } else {
        newQuestion();
      }
    }, 1200);
  } else {
    state.streak = 0;
    state.wrongPick = guess;
    state.misses[state.currentFact.display] = (state.misses[state.currentFact.display] || 0) + 1;
    state.feedback = `${pick(wrongCallouts(state.kidName))} ${pick(encourageLines(state.kidName))}`;
    state.feedbackSub = pick(wrongFollowups(state.kidName));
    setTimeout(newQuestion, 2000);
  }
  saveAll();
  render();
}

function showParentNotice(msg) {
  state.parentNotice = msg;
  state.parentNoticeUntil = Date.now() + 2500;
  render();
}

function startPlay() {
  state.view = "play";
  state.score = 0;
  state.streak = 0;
  state.bestStreak = 0;
  state.questionsDone = 0;
  state.sessionCorrect = 0;
  state.starsEarned = 0;
  state.escaped = false;
  state.lockTaunt = pick(lockTaunts(state.kidName));
  state.lockTauntUntil = Date.now() + 4500;
  newQuestion();
}

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

function renderPlay() {
  const wrap = el("div", "space-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  wrap.style.display = "flex";
  wrap.style.flexDirection = "column";
  wrap.style.alignItems = "center";
  wrap.style.padding = "16px";

  if (Date.now() < state.lockTauntUntil) {
    wrap.appendChild(el("div", "taunt-banner", state.lockTaunt));
  }
  wrap.appendChild(el(
    "div",
    "lock-banner",
    `${kidLabel(state.kidName).toUpperCase()}, answer ${ROUND_GOAL} correctly to escape (${state.questionsDone}/${ROUND_GOAL})`
  ));

  const stats = el("div", "stats-row");
  stats.appendChild(el("span", null, `Score: ${state.score}`));
  stats.appendChild(el("span", null, `Streak: ${state.streak}`));
  stats.appendChild(el("span", null, `Question ${Math.min(state.questionsDone + (state.showFeedback && state.feedbackGood ? 0 : 1), ROUND_GOAL)}/${ROUND_GOAL}`));
  wrap.appendChild(stats);

  const card = el("div", "card");
  card.appendChild(el("div", "question-label", "What is"));
  card.appendChild(el("div", "question", `${state.currentFact.display} ?`));
  wrap.appendChild(card);

  wrap.appendChild(el("div", "hint-box", `Strategy: ${HINTS[state.currentFact.display] || ""}`));

  if (state.showFeedback) {
    const fb = el("div", `feedback ${state.feedbackGood ? "good" : "bad"}`, state.feedback);
    wrap.appendChild(fb);
    wrap.appendChild(el("div", "hint-box", state.feedbackSub));
  }

  wrap.appendChild(el("div", "question-label", "Pick the answer:"));
  const choices = el("div", "choices");
  state.currentChoices.forEach((value) => {
    const btn = el("button", "choice-btn", String(value));
    btn.disabled = state.showFeedback;
    if (state.showFeedback && !state.feedbackGood && state.wrongPick === value) btn.classList.add("wrong-pick");
    btn.onclick = () => submitAnswer(value);
    choices.appendChild(btn);
  });
  wrap.appendChild(choices);
  wrap.appendChild(el("div", "footer-note", "ESC and close button are disabled until you finish"));
  return wrap;
}

function adminBtn(label, cls, action) {
  const b = el("button", `admin-btn ${cls || ""}`, label);
  b.onclick = action;
  return b;
}

function renderParentPanel() {
  const wrap = el("div", "admin-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  const panel = el("div", "admin-panel");
  panel.appendChild(el("h1", "admin-title", "PARENT CONTROL PANEL"));
  panel.appendChild(el("p", "admin-sub", "Outside the math game — parents only"));
  panel.appendChild(el("p", "admin-sub", state.kidName ? `Kid's name: ${state.kidName}` : "Kid's name not set yet"));
  panel.appendChild(el("p", "admin-sub", `Mastered facts: ${state.mastered.size}/${FACTS.length}`));

  panel.appendChild(adminBtn("Set Kid's Name", "good", () => { state.view = "set-name"; state.nameInput = state.kidName; render(); }));
  panel.appendChild(adminBtn(state.kidName ? `View ${kidLabel(state.kidName)}'s Stats` : "View Stats", "accent", () => { state.view = "stats"; render(); }));
  panel.appendChild(adminBtn("Set Stats", "warn", () => { state.view = "set-stats"; render(); }));
  panel.appendChild(adminBtn("Snooze Math (10 More Minutes)", "accent", async () => {
    await window.tortureAPI.parentSnooze();
  }));
  panel.appendChild(adminBtn("Force Torture Now", "warn", () => { startPlay(); window.tortureAPI.parentBackToLock(); }));
  panel.appendChild(adminBtn("Close Torture", "danger", () => window.tortureAPI.parentQuit()));
  panel.appendChild(adminBtn("Back to Torture", "muted", async () => {
    state.view = "play";
    await window.tortureAPI.parentBackToLock();
    render();
  }));

  const notice = el("div", "notice");
  if (Date.now() < state.parentNoticeUntil) notice.textContent = state.parentNotice;
  panel.appendChild(notice);
  panel.appendChild(el("p", "admin-sub", "Ctrl+Shift+P opens this panel anytime"));
  wrap.appendChild(panel);
  return wrap;
}

function renderSetStats() {
  const wrap = el("div", "admin-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  const panel = el("div", "admin-panel");
  panel.appendChild(el("h1", "admin-title", "SET STATS"));
  panel.appendChild(el("p", "admin-sub", `Parent-only tools for ${kidLabel(state.kidName)}'s progress`));
  panel.appendChild(adminBtn("Reset All Progress", "danger", async () => {
    state.mastered = new Set();
    state.misses = {};
    state.correctCounts = {};
    await saveAll();
    showParentNotice("All progress reset.");
    state.view = "parent";
    render();
  }));
  panel.appendChild(adminBtn("Clear Miss Counts", "warn", async () => {
    state.misses = {};
    await saveAll();
    showParentNotice("Miss counts cleared.");
    state.view = "parent";
    render();
  }));
  panel.appendChild(adminBtn("Give Free Escape (This Session)", "good", async () => {
    state.view = "results";
    state.escaped = true;
    await window.tortureAPI.notifyEscaped();
    render();
  }));
  panel.appendChild(adminBtn("Back to Parent Panel", "accent", () => { state.view = "parent"; render(); }));
  wrap.appendChild(panel);
  return wrap;
}

function renderStats() {
  const wrap = el("div", "admin-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  wrap.appendChild(el("h1", "admin-title", `${kidLabel(state.kidName)}'s Stats (Parent Only)`));
  const list = el("div", "stats-list");
  FACTS.forEach((fact) => {
    const done = state.mastered.has(fact.display);
    const row = el("div", `stat-row${done ? " mastered" : ""}`);
    let label = `${fact.display} = ${done ? dec(fact.answer) : "???"}`;
    const prog = state.correctCounts[fact.display] || 0;
    if (!done && prog) label += ` (${prog}/${MASTERED_NEEDED})`;
    row.appendChild(el("span", null, label + (done ? " ★" : "")));
    const miss = state.misses[fact.display] || 0;
    if (miss) row.appendChild(el("span", "stat-miss", `missed ${miss}×`));
    list.appendChild(row);
  });
  wrap.appendChild(list);
  wrap.appendChild(adminBtn("Back to Parent Panel", "accent", () => { state.view = "parent"; render(); }));
  return wrap;
}

function renderPin() {
  const wrap = el("div", "admin-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  const panel = el("div", "admin-panel");
  panel.appendChild(el("h1", "admin-title", "PARENT PIN"));
  panel.appendChild(el("p", "admin-sub", "Enter your override code"));
  const dots = "•".repeat(state.pinInput.length) + "○".repeat(PARENT_PIN.length - state.pinInput.length);
  panel.appendChild(el("div", "pin-dots", dots));
  if (state.pinMessage) panel.appendChild(el("p", "admin-sub", state.pinMessage));

  const keypad = el("div", "keypad");
  "123456789".split("").forEach((d) => {
    const b = el("button", null, d);
    b.onclick = () => { if (state.pinInput.length < PARENT_PIN.length) { state.pinInput += d; render(); } };
    keypad.appendChild(b);
  });
  const row = el("div");
  row.style.display = "contents";
  ["C", "0", "⌫"].forEach((d) => {
    const b = el("button", null, d);
    b.onclick = () => {
      if (d === "C") state.pinInput = "";
      else if (d === "⌫") state.pinInput = state.pinInput.slice(0, -1);
      else if (state.pinInput.length < PARENT_PIN.length) state.pinInput += d;
      render();
    };
    keypad.appendChild(b);
  });
  const enter = el("button", "wide", "ENTER");
  enter.onclick = () => {
    if (state.pinInput === PARENT_PIN) {
      state.pinInput = "";
      state.pinMessage = "";
      if (state.kidName) state.view = "parent";
      else { state.view = "set-name"; state.nameInput = ""; }
      render();
    } else {
      state.pinMessage = "Wrong PIN.";
      state.pinInput = "";
      render();
    }
  };
  keypad.appendChild(enter);
  panel.appendChild(keypad);
  wrap.appendChild(panel);
  return wrap;
}

function renderSetName() {
  const wrap = el("div", "admin-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  const panel = el("div", "admin-panel");
  panel.appendChild(el("h1", "admin-title", "SET KID'S NAME"));
  panel.appendChild(el("p", "admin-sub", "The math lock will say this name in every message"));
  const input = el("input", "name-input");
  input.value = state.nameInput;
  input.placeholder = "Type a name...";
  input.maxLength = 20;
  input.oninput = () => { state.nameInput = input.value; };
  panel.appendChild(input);
  panel.appendChild(adminBtn("Save Name", "good", async () => {
    const cleaned = state.nameInput.trim();
    if (!cleaned) return;
    state.kidName = cleaned.slice(0, 20);
    await saveAll();
    state.view = "parent";
    showParentNotice(`Saved! The game will now call them ${state.kidName}.`);
    render();
  }));
  panel.appendChild(adminBtn("Back to Parent Panel", "accent", () => { state.view = "parent"; render(); }));
  wrap.appendChild(panel);
  return wrap;
}

function renderResults() {
  const wrap = el("div", "space-bg");
  wrap.style.width = "100%";
  wrap.style.minHeight = "100vh";
  wrap.appendChild(el("h1", "results-title", `You Escaped, ${kidLabel(state.kidName)}!`));
  wrap.appendChild(el("p", "results-sub", `Nice work, ${kidLabel(state.kidName)}!`));
  wrap.appendChild(el("p", "admin-sub", "Press ESC or close the window to use your computer"));
  return wrap;
}

function render() {
  root.innerHTML = "";
  let node;
  switch (state.view) {
    case "pin": node = renderPin(); break;
    case "parent": node = renderParentPanel(); break;
    case "set-stats": node = renderSetStats(); break;
    case "stats": node = renderStats(); break;
    case "set-name": node = renderSetName(); break;
    case "results": node = renderResults(); break;
    default: node = renderPlay(); break;
  }
  root.appendChild(node);
}

function showBlockedToast(msg) {
  const t = el("div", "blocked-toast", msg);
  root.appendChild(t);
  setTimeout(() => t.remove(), 2000);
}

async function init() {
  await loadAll();
  startPlay();

  window.tortureAPI.onLockState((data) => {
    if (data.blocked) {
      const remaining = Math.max(0, ROUND_GOAL - state.questionsDone);
      showBlockedToast(`Locked! Get ${remaining} more correct answer${remaining === 1 ? "" : "s"} to escape.`);
    }
  });

  window.tortureAPI.onOpenParentPin(() => {
    state.view = "pin";
    state.pinInput = "";
    state.pinMessage = "";
    render();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.escaped) window.tortureAPI.parentQuit();
  });
}

init();