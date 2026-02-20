const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');

const scriptFiles = [
  'scripts/trade.js',
  'scripts/inspect_policies_advanced.js',
  'scripts/check_target_executor.js'
];

test('no THIRD_* env vars are used in scripts', () => {
  for (const rel of scriptFiles) {
    const text = fs.readFileSync(path.join(root, rel), 'utf8');
    assert.doesNotMatch(text, /THIRD_[A-Z0-9_]+/, `legacy THIRD_* env var found in ${rel}`);
  }
});

test('trade script uses CHAIN_ID env variable', () => {
  const trade = fs.readFileSync(path.join(root, 'scripts/trade.js'), 'utf8');
  assert.match(trade, /process\.env\.CHAIN_ID/);
});
