const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      nodeIntegration: false
    }
  });

win.loadFile(path.join(__dirname, 'public', 'dist', 'index.html'));

  // 👇 Path to backend executable
  const backendPath = path.join(process.resourcesPath, 'bin', 'run_backend.exe');
  const backend = spawn(backendPath);

  win.webContents.openDevTools();
  backend.stdout.on('data', data => {
    console.log(`[BACKEND]: ${data}`);
  });

  backend.stderr.on('data', data => {
    console.error(`[BACKEND ERROR]: ${data}`);
  });

  app.on('before-quit', () => {
    backend.kill();
  });
}

app.whenReady().then(createWindow);
