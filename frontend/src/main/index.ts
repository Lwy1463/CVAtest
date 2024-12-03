import * as electron from 'electron'
import { app, BrowserWindow, dialog, ipcMain, shell, systemPreferences } from 'electron'
import path, { join } from 'path'
import fs from 'fs'
import { electronApp, is, optimizer } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import log from 'electron-log'
import { spawn } from 'child_process'
const { exec } = require('child_process');
log.transports.file.resolvePath = () => path.join(__dirname, 'logs', 'app.log');
console.log(__dirname);

function showAlert(message) {
  const alertWindow = new BrowserWindow({
    width: 400,
    height: 200,
    modal: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  alertWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(`
    <html>
      <head>
        <title>Alert</title>
        <style>
          body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
          }
          .message {
            padding: 20px;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="message">
          <p>${message}</p>
          <button onclick="window.close()">OK</button>
        </div>
      </body>
    </html>
  `)}`);
}

let isMannualStop = false;
function createWindow(): void {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    // minWidth: 1440,
    // minHeight: 900,
    show: false,
    center: true,
    title: '西部创源',
    frame: false,
    titleBarStyle: 'hidden',
    trafficLightPosition: { x: 10, y: 20 },
    // windows os title bar 样式
    titleBarOverlay: false,
    icon: path.join(__dirname, '../../resources/icon.png'),
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      nodeIntegration: true,
      sandbox: false
      // webSecurity: false
    }
  })
  if (process.platform === 'darwin') {
    app.dock.setIcon(path.join(__dirname, '../../resources/desk-icon.png'))
  }
  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })
  // 当窗口大小改变时触发
  mainWindow.on('resize', () => {
    // 获取窗口的尺寸
    const [width, height] = mainWindow.getContentSize()
    // 发送消息到渲染进程，通知尺寸变化
    mainWindow.webContents.send('window-resize', { width, height })
  })

  // ipcMain.on('direction', (_, dirPath: string, kind) => {
  //   try {
  //     const directories = fs
  //       .readdirSync(path.join(LOCAL_PATH, dirPath), { withFileTypes: true })
  //       .filter((dirent) => dirent.isDirectory() && path.basename(dirent.name).charAt(0) !== '.')
  //       .map((dirent) => dirent.name)
  //     console.log('direction', dirPath, directories, path.join(LOCAL_PATH))
  //     mainWindow.webContents.send('direction', directories, kind)
  //   } catch (error) {
  //     console.error(`Error reading directories in path: ${error}`)
  //     mainWindow.webContents.send('direction', 'error')
  //   }
  // })
  //修改titleBarOverlay
  // ipcMain.on('set-titleBarOverlay', (_, visible: boolean) => {
  //   mainWindow.setTitleBarOverlay(visible)
  // })
  ipcMain.on('open-directory', (_, kind) => {
    dialog
      .showOpenDialog({
        properties: ['openDirectory']
      })
      .then((result) => {
        mainWindow.webContents.send('open-directory', result.filePaths[0], kind)
      })
      .catch((error) => {
        console.error('打开文件夹失败：', error)
      })
  })

  // 保存文件对话框
  ipcMain.on('save-dialog', async (_, buffer, fileName = 'example.text') => {
    const { filePath, canceled } = await dialog.showSaveDialog(mainWindow, {
      defaultPath: path.join(app.getPath('downloads'), fileName)
    })
    if (!canceled) {
      fs.writeFileSync(filePath as string, Buffer.from(buffer))
    } else {
      console.log('取消保存')
    }
  })

  ipcMain.on('set-window-size', (_, width, height) => {
    if (!mainWindow.isDestroyed()) {
      // mainWindow.setMaximumSize(width, height)
      // mainWindow.setMinimumSize(width, height)
      mainWindow.setSize(width, height)
      // mainWindow.setContentSize(width, height)
      // mainWindow.center();
    }
  })

  ipcMain.on('download_file', async (_, base64String: string) => {
    try {
      // 弹出文件保存对话框
      const { filePath } = await dialog.showSaveDialog({
        defaultPath: 'results.xlsx',
      });
  
      if (filePath) {
        // 将Base64字符串转换为Buffer
        const buffer = Buffer.from(base64String.split(',')[1], 'base64');
  
        // 将Buffer写入文件
        fs.writeFile(filePath, buffer, (error) => {
          if (error) {
            console.error('保存文件出错：', error);
          } else {
            console.log('文件已保存到：', filePath);
  
            // 弹出文件下载的目录
            dialog.showMessageBox({
              type: 'info',
              title: '文件已保存',
              message: `文件已保存到：${filePath}`,
            });
          }
        });
      }
    } catch (e: any) {
      dialog.showErrorBox('下载失败', e.message);
    }
  });

  ipcMain.on(
    'start-download',
    async (
      _,
      base64String: string,
      savePath: string,
      filename: string,
      tab = 'default',
      project_id: string
    ) => {
      try {
        const dir = savePath
        fs.mkdirSync(dir, { recursive: true })
        // 将Base64字符串转换为Buffer
        const buffer = Buffer.from(base64String.split(',')[1], 'base64')
        // 将Buffer写入文件
        fs.writeFile(dir + `/${filename}`, buffer, (error) => {
          if (error) {
            console.error('保存文件出错：', error)
          } else {
            console.log('文件已保存到：', savePath, project_id)
            mainWindow.webContents.send(
              'finish-download',
              `${savePath}/${filename}`,
              tab,
              project_id
            )
          }
        })
      } catch (e: any) {
        electron.dialog.showErrorBox('下载失败', e.message)
      }
    }
  )
  ipcMain.on('getImage', (event, filePath) => {
    console.log(filePath);

    // 如果是 macOS 平台，将反斜杠替换为正斜杠
    if (process.platform === 'darwin') {
      filePath = filePath.replace(/\\/g, '/');
    }

    fs.readFile(filePath, (err, data) => {
      console.log(err);
      console.log(data);
      event.sender.send('showpic', { data });
    });
  });

  ipcMain.on('open-path', async (_, savePath) => {
    fs.mkdirSync(savePath, { recursive: true })
    shell
      .openPath(savePath)
      .then(() => {
        console.log('打开文件夹成功', savePath)
      })
      .catch((error) => {
        console.error('打开文件夹失败：', error)
      })
  })
  // 退出应用程序
  ipcMain.on('app-quit', () => {
    app.quit()
  })
  // 最小化
  ipcMain.on('app-minimize', () => {
    mainWindow.minimize()
  })
  // 最大化
  ipcMain.on('app-maximize', () => {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize()
    } else {
      mainWindow.maximize()
    }
  })
  // 退出最大化
  ipcMain.on('app-unmaximize', () => {
    mainWindow.unmaximize()
  })

  ipcMain.on('select-save-path', async (event) => {
    const { filePaths } = await dialog.showOpenDialog(mainWindow, {
        title: '选择保存路径',
        properties: ['openDirectory']
    });

    if (filePaths && filePaths.length > 0) {
        event.reply('save-path-selected', filePaths[0]);
    }
});

let recordingProcess;

ipcMain.on('start-recording', (event, savePath) => {
  // 检查麦克风权限
  if (systemPreferences.getMediaAccessStatus('microphone') !== 'granted') {
    event.reply('recording-error');
    return;
  }
  
  let soxPath;
  if (process.platform !== 'darwin') {
    ipcMain.emit('debug-info', path.join(__dirname));
    
    if (!is.dev) {
      soxPath = path.join(__dirname, '..', '..', '..', 'resources', 'sox_14', 'sox.exe');
    } else {
      soxPath = path.join(__dirname, '..', '..', 'resources', 'sox_14', 'sox.exe');
    }
    
    // 使用 spawn 来启动 sox 进程
    recordingProcess = spawn(soxPath, ['-t', 'waveaudio', '-d', savePath]);
  } else {
    recordingProcess = spawn('sox', ['-d', savePath]);
  }
  
  // 监听进程关闭事件
  recordingProcess.on('close', (code) => {
    if (isMannualStop) {
      console.log(`complete record: ${savePath}`);
      isMannualStop = false;
      event.reply('recording-completed');
      return;
    }
    if (code !== 0) {
      console.error(`record failed with code: ${code}`);
      event.reply('recording-error');
    } else {
      console.log(`record completed: ${savePath}`);
      event.reply('recording-completed');
    }
  });
  
  recordingProcess.on('error', (error) => {
    console.error(`record fail: ${error.message}`);
    event.reply('recording-error');
  });
});

ipcMain.on('stop-recording', () => {
  if (recordingProcess) {
    isMannualStop = true;
    recordingProcess.kill('SIGTERM'); // 或者使用 'SIGKILL' 如果需要更强制的终止。
    recordingProcess = null;
    console.log('record stopped');
  }
});

ipcMain.on('show-save-dialog', async (event) => {
  const { filePath, canceled } = await dialog.showSaveDialog(mainWindow, {
      title: '输入文件名',
      defaultPath: 'recording.wav',
      filters: [
          { name: '音频文件', extensions: ['wav'] },
      ],
  });

  if (!canceled) {
      const fileName = path.basename(filePath);
      event.reply('start-recording', fileName);
  }
});

ipcMain.on('show-save-dialog-download', async (event) => {
  const { filePath, canceled } = await dialog.showSaveDialog(mainWindow, {
      title: '输入文件名',
      defaultPath: 'download.xlsx',
      filters: [
          { name: 'Excel 文件', extensions: ['xlsx'] },
      ],
  });

  if (!canceled) {
      const fileName = path.basename(filePath);
      event.reply('download-template-selected', fileName);
  }
})

ipcMain.on('list-wav-files', async (event, dirPath) => {
  if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
  }

  const files = fs.readdirSync(dirPath).filter(file => file.endsWith('.wav'));
  console.log(files);
  event.reply('wav-files-listed', files);
});

ipcMain.on('open-system-preferences', () => {
  if (process.platform === 'darwin') {
      shell.openExternal('x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone');
  }
});

  mainWindow.on('closed', () => {})

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'), { hash: '/' })
  }
}

ipcMain.on('show_path', (event, filePath) => {
  const dirPath = path.dirname(filePath);
  let command = process.platform === 'darwin' ? 'open' : 'explorer';
  exec(`${command} "${dirPath}"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error opening directory: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Error opening directory: ${stderr}`);
      return;
    }
    console.log(`Directory opened: ${dirPath}`);
  });
});

ipcMain.on('open-demo-xlsx', (event, fileName) => {
  console.log(fileName);
  let excelPath;
  if (!is.dev) {
    excelPath = path.join(__dirname, '..', '..', '..', 'resources', fileName);
  } else {
    excelPath = path.join(__dirname, '..', '..', 'resources', fileName);
  }
  shell.openPath(excelPath).then((error) => {
    if (error) {
      console.error(`Error opening file: ${error}`);
      event.reply('open-demo-xlsx-error', error);
    } else {
      console.log(`File opened: ${excelPath}`);
      event.reply('open-demo-xlsx-success');
    }
  });
});

ipcMain.handle('save-audio-file', async (event, audioBlob) => {
  const result = await dialog.showSaveDialog({
      title: '保存录音文件',
      defaultPath: 'recording.wav',
      filters: [
          { name: 'MP3 Files', extensions: ['wav'] }
      ]
  });

  if (!result.canceled && result.filePath) {
      return new Promise((resolve, reject) => {
          const buffer = Buffer.from(audioBlob);
          console.log(buffer)
          fs.writeFile(result.filePath, buffer, (err, res) => {
              console.log(res);
              if (err) {
                  console.error('保存音频文件失败', err);
                  reject(err);
              } else {
                  console.log('音频文件保存成功', result.filePath);
                  resolve(result.filePath);
              }
          });
      });
  } else {
      return undefined;
  }
});

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// In this file you can include the rest of your app"s specific main process
// code. You can also put them in separate files and require them here.
// 示例：在某个事件触发时动态设置窗口大小
