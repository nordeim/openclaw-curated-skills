const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');

test('skill manifest includes expected entrypoint', () => {
  const yaml = fs.readFileSync(path.join(root, 'skill.yaml'), 'utf8');
  assert.match(yaml, /name:\s*safe-rebalancer/);
  assert.match(yaml, /scope:\s*31third/);
  assert.match(yaml, /entrypoint:\s*scripts\/trade\.js/);
});

test('SKILL.md uses canonical published name', () => {
  const skill = fs.readFileSync(path.join(root, 'SKILL.md'), 'utf8');
  assert.match(skill, /name:\s*safe-rebalancer/);
  assert.match(skill, /metadata:\s*\{.*"openclaw".*"skillKey":"31third-safe-rebalancer".*\}/);
  assert.match(skill, /"requires":\{"env":\["RPC_URL","CHAIN_ID","TOT_API_KEY","SAFE_ADDRESS","EXECUTOR_MODULE_ADDRESS","EXECUTOR_WALLET_PRIVATE_KEY"\],"bins":\["node"\]\}/);
});
