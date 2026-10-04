// Start the local-only model and Vite together; stop only our own children.
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const python = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
if (!existsSync(python)) {
  console.error('Missing project Python environment. Follow the Build 03 setup in README.md.');
  process.exit(1);
}
const children = [];
let stopped = false;
function stop(code = 0) {
  if (stopped) return;
  stopped = true;
  for (const child of children) child.kill();
  process.exitCode = code;
}
function start(command, args) {
  const child = spawn(command, args, { cwd: root, stdio: 'inherit', windowsHide: true });
  children.push(child);
  child.on('error', error => { console.error(error.message); stop(1); });
  child.on('exit', code => stop(code ?? 0));
  return child;
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
start(python, ['scripts/discover_service.py']);
start(process.execPath, ['node_modules/vite/bin/vite.js']);
