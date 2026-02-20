const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');

test('package name is @31third/safe-rebalancer', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  assert.equal(pkg.name, '@31third/safe-rebalancer');
});

test('required skill files exist', () => {
  const required = [
    'README.md',
    'SKILL.md',
    'INTEGRATION.md',
    'skill.yaml',
    'scripts/trade.js',
    'scripts/inspect_policies_advanced.js',
    'scripts/check_target_executor.js',
    'scripts/error_decoder.js',
    'scripts/generatePdf.js',
    'references/SDK.md',
    'references/abi/StrategyExecutor.json',
    'references/abi/AssetUniversePolicy.json',
    'references/abi/StaticAllocationPolicy.json',
    'references/abi/SlippagePolicy.json'
  ];

  for (const rel of required) {
    const full = path.join(root, rel);
    assert.equal(fs.existsSync(full), true, `missing: ${rel}`);
  }
});
