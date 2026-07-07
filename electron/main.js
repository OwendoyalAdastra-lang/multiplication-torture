const { app, BrowserWindow, globalShortcut, ipcMain, screen } = require("electron");
const path = require("path");
const fs = require("fs");
const os = require("os");

const GRACE_MS = 10 * 60 * 1000;
const PROGRESS_DIR = path.join(os.homedir(), ".graham_multiplication");
const PROGRESS_FILE = path.join(PROGRESS_DIR, "progress.json");

let mainWindow = null;
let locked = false;
let escaped = false;
let graceTimer = null;

app.commandLine.appendSwitch("disable-gpu");
app.commandLine.appendSwitch("disable-software-rasterizer");
app.commandLine.appendSwitch("disable-gpu-compositing");

function loadProgressFile() {
  try {
    return JSON.parse(fs.readFileSync(PROGRESS_FILE, "utf8"));
  } catch {
    return {
      kid_name: "",
      mastered: [],
      misses: {},
      correct_counts: {},
    };
  }
}

function saveProgressFile(data) {
  fs.mkdirSync(PROGRESS_DIR, { recursive: true });
  fs.writeFileSync(PROGRESS_FILE, JSON.stringify(data, null, 2));
}

function createWindow(openPin = false) {
  if (graceTimer) {
    clearTimeout(graceTimer);
    graceTimer = null;
  }
  if (mainWindow) {
    mainWindow.focus();
    if (openPin) mainWindow.webContents.send("open-parent-pin");
    return;
  }

  const { width, height } = screen.getPrimaryDisplay().bounds;

  mainWindow = new BrowserWindow({
    x: 0,
    y: 0,
    width,
    height,
    show: false,
    frame: false,
    fullscreen: true,
    kiosk: true,
    autoHideMenuBar: true,
    backgroundColor: "#0c1024",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.setMenu(null);
  locked = true;
  escaped = false;

  mainWindow.once("ready-to-show", () => {
    mainWindow.setFullScreen(true);
    mainWindow.setKiosk(true);
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.loadFile(path.join(__dirname, "..", "app", "index.html"));

  mainWindow.webContents.on("did-finish-load", () => {
    mainWindow.webContents.send("lock-state", { locked: true, escaped: false });
    if (openPin) mainWindow.webContents.send("open-parent-pin");
  });

  mainWindow.on("close", (event) => {
    if (locked && !escaped) {
      event.preventDefault();
      mainWindow.webContents.send("lock-state", { blocked: true });
    }
  });
}

function startGraceTimer() {
  if (graceTimer) clearTimeout(graceTimer);
  graceTimer = setTimeout(() => createWindow(false), GRACE_MS);
}

app.whenReady().then(() => {
  // Skip grace if launched with --now for testing
  if (process.argv.includes("--now")) {
    createWindow(false);
  } else {
    startGraceTimer();
  }

  globalShortcut.register("Control+Shift+P", () => {
    createWindow(true);
  });

  ipcMain.handle("load-progress", () => loadProgressFile());
  ipcMain.handle("save-progress", (_e, data) => {
    saveProgressFile(data);
    return true;
  });
  ipcMain.handle("escaped", () => {
    escaped = true;
    locked = false;
    if (mainWindow) mainWindow.setKiosk(false);
    return true;
  });
  ipcMain.handle("parent-quit", () => {
    escaped = true;
    locked = false;
    app.quit();
  });
  ipcMain.handle("parent-back-to-lock", () => {
    if (!mainWindow) createWindow(false);
    else mainWindow.focus();
    locked = true;
    escaped = false;
    if (mainWindow) {
      mainWindow.setKiosk(true);
      mainWindow.setFullScreen(true);
    }
    return true;
  });
  ipcMain.handle("parent-snooze", () => {
    escaped = true;
    locked = false;
    if (mainWindow) {
      mainWindow.destroy();
      mainWindow = null;
    }
    startGraceTimer();
    return true;
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
  if (graceTimer) clearTimeout(graceTimer);
});

app.on("before-quit", (event) => {
  if (locked && !escaped) {
    event.preventDefault();
    if (mainWindow) mainWindow.webContents.send("lock-state", { blocked: true });
  }
});