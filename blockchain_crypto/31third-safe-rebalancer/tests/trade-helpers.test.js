const test = require('node:test');
const assert = require('node:assert/strict');
const {
  parseTargetsArg,
  validateTargets,
  validateSwapInputs,
  buildPayload,
  parseChainId
} = require('../scripts/trade.js');

test('parseTargetsArg rejects invalid JSON', () => {
  assert.throws(() => parseTargetsArg('{bad'), /Invalid --targets JSON/);
});

test('validateTargets enforces sum to 1.0', () => {
  assert.throws(
    () =>
      validateTargets({
        '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa': 0.3,
        '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb': 0.3
      }),
    /sum to 1.0/
  );
});

test('validateSwapInputs rejects malformed addresses', () => {
  assert.throws(() => validateSwapInputs('0x123', '0x456', '1'), /Invalid --from token address format/);
});

test('buildPayload builds rebalance entries', () => {
  const payload = buildPayload({
    action: 'rebalance',
    safeAddress: '0x1111111111111111111111111111111111111111',
    signerAddress: '0x2222222222222222222222222222222222222222',
    chainId: 8453,
    minTradeValue: 1,
    targets: {
      '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa': 0.5,
      '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb': 0.5
    }
  });

  assert.equal(payload.targetEntries.length, 2);
  assert.equal(payload.chainId, 8453);
});

test('parseChainId maps chain aliases', () => {
  assert.equal(parseChainId(['--chain', 'base']), 8453);
  assert.equal(parseChainId(['--chain-id', '137']), 137);
});
