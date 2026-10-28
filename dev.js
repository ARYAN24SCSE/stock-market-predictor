/**
 * Cross-platform runner for the Stock Market Prediction Dashboard
 * Allows running `npm run dev` or `npm start` directly out of the box.
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const isWindows = process.platform === 'win32';
const rootDir = __dirname;
const isTest = process.argv.includes('--test');

function findExecutable() {
  if (isTest) {
    const venvPython = isWindows
      ? path.join(rootDir, '.venv', 'Scripts', 'python.exe')
      : path.join(rootDir, '.venv', 'bin', 'python');

    if (fs.existsSync(venvPython)) {
      return { command: venvPython, args: ['test_pipeline.py'] };
    }
    return { command: isWindows ? 'python' : 'python3', args: ['test_pipeline.py'] };
  }

  // 1. Check local virtual environment streamlit binary
  const venvStreamlit = isWindows
    ? path.join(rootDir, '.venv', 'Scripts', 'streamlit.exe')
    : path.join(rootDir, '.venv', 'bin', 'streamlit');

  if (fs.existsSync(venvStreamlit)) {
    return { command: venvStreamlit, args: ['run', 'app.py'] };
  }

  // 2. Check local virtual environment python binary
  const venvPython = isWindows
    ? path.join(rootDir, '.venv', 'Scripts', 'python.exe')
    : path.join(rootDir, '.venv', 'bin', 'python');

  if (fs.existsSync(venvPython)) {
    return { command: venvPython, args: ['-m', 'streamlit', 'run', 'app.py'] };
  }

  // 3. Check system streamlit in PATH
  try {
    const checkCmd = isWindows ? 'where streamlit' : 'which streamlit';
    const resolvedPath = execSync(checkCmd, { encoding: 'utf-8' }).trim().split(/\r?\n/)[0];
    if (resolvedPath) {
      return { command: resolvedPath, args: ['run', 'app.py'] };
    }
  } catch (e) {
    // Continue to fallback
  }

  // 4. Check system python
  const pythonCommands = isWindows ? ['python', 'py'] : ['python3', 'python'];
  for (const cmd of pythonCommands) {
    try {
      execSync(`${cmd} -c "import streamlit"`, { stdio: 'ignore' });
      return { command: cmd, args: ['-m', 'streamlit', 'run', 'app.py'] };
    } catch (e) {
      // Continue searching
    }
  }

  return null;
}

const target = findExecutable();

if (!target) {
  console.error('\n❌ Could not find Streamlit or Python environment.');
  console.error('\nPlease ensure your environment is set up:');
  console.error('  1. Create virtual environment: py -3.11 -m venv .venv (or python3 -m venv .venv)');
  console.error('  2. Activate & install packages:  pip install -r requirements.txt\n');
  process.exit(1);
}

// Extract any additional command-line arguments passed to npm run dev (ignoring --test)
const extraArgs = process.argv.slice(2).filter((arg) => arg !== '--test');
const finalArgs = [...target.args, ...extraArgs];

console.log('\n=============================================================');
console.log('📈 Stock Market Price Prediction & Analysis Dashboard');
console.log('=============================================================');
if (!isTest) {
  console.log('🚀 Starting local development server...');
  console.log('🌐 Local URL: http://localhost:8501');
  console.log(`🔧 Executing: ${target.command} ${finalArgs.join(' ')}\n`);
}

// Use shell: false when executing direct absolute binaries to avoid Node DEP0190 warnings
const useShell = isWindows && !path.isAbsolute(target.command);

const child = spawn(target.command, finalArgs, {
  cwd: rootDir,
  stdio: 'inherit',
  shell: useShell,
  env: {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
    PYTHONUTF8: '1',
  },
});

child.on('error', (err) => {
  console.error(`\n❌ Failed to start process: ${err.message}`);
  process.exit(1);
});

child.on('close', (code) => {
  process.exit(code || 0);
});

// Forward termination signals to child process
['SIGINT', 'SIGTERM'].forEach((signal) => {
  process.on(signal, () => {
    if (child && !child.killed) {
      child.kill(signal);
    }
  });
});
