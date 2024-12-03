export const quitApp = () => {
  window.electron.ipcRenderer.send('app-quit')
}
export const minimizeApp = () => {
  window.electron.ipcRenderer.send('app-minimize')
}
export const maximizeApp = () => {
  window.electron.ipcRenderer.send('app-maximize')
}

export const unmaximizeApp = () => {
  window.electron.ipcRenderer.send('app-unmaximize')
}
