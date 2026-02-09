#!/usr/bin/env node
// Dependency checker for animator skill

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const checks = [];

function check(name, fn) {
  try {
    const result = fn();
    checks.push({ name, ok: true, detail: result });
  } catch (e) {
    checks.push({ name, ok: false, detail: e.message });
  }
}

function run(cmd) {
  return execSync(cmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
}

// Node.js
check('Node.js', () => {
  const v = run('node --version');
  const major = parseInt(v.replace('v', ''));
  if (major < 18) throw new Error(`${v} (need v18+)`);
  return v;
});

// npm
check('npm', () => run('npm --version'));

// ffmpeg
check('ffmpeg', () => {
  try {
    const out = run('ffmpeg -version 2>&1');
    const match = out.match(/ffmpeg version (\S+)/);
    return match ? match[1] : 'installed';
  } catch {
    throw new Error('not found - install with: brew install ffmpeg');
  }
});

// Playwright
check('Playwright', () => {
  const skillDir = path.resolve(__dirname, '..');
  const playwrightPath = path.join(skillDir, 'node_modules', 'playwright');
  if (!fs.existsSync(playwrightPath)) {
    throw new Error('not installed - run: npm install (in skills/animator/)');
  }
  const pkg = JSON.parse(fs.readFileSync(path.join(playwrightPath, 'package.json'), 'utf-8'));
  return pkg.version;
});

// Playwright browsers
check('Chromium (Playwright)', () => {
  const skillDir = path.resolve(__dirname, '..');
  try {
    const { chromium } = require(path.join(skillDir, 'node_modules', 'playwright'));
    const browserPath = chromium.executablePath();
    if (!fs.existsSync(browserPath)) {
      throw new Error('not downloaded - run: npx playwright install chromium (in skills/animator/)');
    }
    return 'installed';
  } catch (e) {
    if (e.message.includes('not downloaded') || e.message.includes('not installed')) throw e;
    throw new Error('not available - run: npm install && npx playwright install chromium');
  }
});

// Print results
console.log('\nanimator doctor\n');

const maxLen = Math.max(...checks.map(c => c.name.length));
let allOk = true;

for (const c of checks) {
  const icon = c.ok ? '\x1b[32m✓\x1b[0m' : '\x1b[31m✗\x1b[0m';
  const detail = c.ok ? `\x1b[2m${c.detail}\x1b[0m` : `\x1b[31m${c.detail}\x1b[0m`;
  console.log(`  ${icon} ${c.name.padEnd(maxLen + 2)}${detail}`);
  if (!c.ok) allOk = false;
}

console.log('');
if (allOk) {
  console.log('  All good. Ready to record.\n');
} else {
  console.log('  Fix the issues above, then run doctor again.\n');
  process.exit(1);
}
