const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const rootDir = path.resolve(__dirname, '..');

function getPythonCommand() {
  const isWindows = process.platform === 'win32';
  
  // 1. Check local virtual environment (.venv)
  const venvPythonWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  const venvPythonPosix = path.join(rootDir, '.venv', 'bin', 'python');
  
  if (isWindows && fs.existsSync(venvPythonWin)) {
    return { cmd: venvPythonWin, args: ['-m', 'streamlit', 'run', path.join('app', 'main.py')] };
  }
  if (!isWindows && fs.existsSync(venvPythonPosix)) {
    return { cmd: venvPythonPosix, args: ['-m', 'streamlit', 'run', path.join('app', 'main.py')] };
  }
  
  // 2. Check if VIRTUAL_ENV environment variable is active
  if (process.env.VIRTUAL_ENV) {
    const envPython = isWindows 
      ? path.join(process.env.VIRTUAL_ENV, 'Scripts', 'python.exe')
      : path.join(process.env.VIRTUAL_ENV, 'bin', 'python');
    if (fs.existsSync(envPython)) {
      return { cmd: envPython, args: ['-m', 'streamlit', 'run', path.join('app', 'main.py')] };
    }
  }

  // 3. Fallback to system python
  const fallbackCmd = isWindows ? 'python' : 'python3';
  return { cmd: fallbackCmd, args: ['-m', 'streamlit', 'run', path.join('app', 'main.py')] };
}

const { cmd, args } = getPythonCommand();
const extraArgs = process.argv.slice(2);
const finalArgs = [...args, ...extraArgs];

console.log(`Starting CustomerInsight AI UI...`);
console.log(`> ${cmd} ${finalArgs.join(' ')}\n`);

const child = spawn(cmd, finalArgs, {
  cwd: rootDir,
  stdio: 'inherit',
  shell: false
});

child.on('error', (err) => {
  console.error('Failed to start UI process:', err.message);
  process.exit(1);
});

child.on('close', (code) => {
  process.exit(code ?? 0);
});
