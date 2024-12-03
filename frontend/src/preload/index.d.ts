import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: unknown
    platform: 'darwin' | 'win32' | 'linux'
  }
}
