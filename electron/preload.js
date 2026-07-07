const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("tortureAPI", {
  loadProgress: () => ipcRenderer.invoke("load-progress"),
  saveProgress: (data) => ipcRenderer.invoke("save-progress", data),
  notifyEscaped: () => ipcRenderer.invoke("escaped"),
  parentQuit: () => ipcRenderer.invoke("parent-quit"),
  parentSnooze: () => ipcRenderer.invoke("parent-snooze"),
  parentBackToLock: () => ipcRenderer.invoke("parent-back-to-lock"),
  onLockState: (cb) => ipcRenderer.on("lock-state", (_e, data) => cb(data)),
  onOpenParentPin: (cb) => ipcRenderer.on("open-parent-pin", () => cb()),
});