// start-ui.js – launches the Streamlit UI using the project's virtual environment
const { spawn } = require('child_process');
const path = require('path');

console.log('Starting CustomerInsight AI UI...');

// Resolve the python interpreter inside the .venv (Windows layout)
const pythonExe = path.resolve(__dirname, '..', '.venv', 'Scripts', 'python.exe');
// Arguments to run the Streamlit app
const args = ['-m', 'streamlit', 'run', 'app/main.py'];

const child = spawn(pythonExe, args, { stdio: 'inherit' });

child.on('close', (code) => {
  console.log(`Streamlit process exited with code ${code}`);
  process.exit(code);
});

