const test = require('node:test');
const assert = require('node:assert/strict');
const { renderPostTradeTemplate } = require('../scripts/renderReport.js');

test('renderPostTradeTemplate escapes HTML-sensitive input', () => {
  const html = renderPostTradeTemplate({
    refId: '<script>alert(1)</script>',
    trades: [{ sequence: '1', fromToken: '<b>x</b>' }]
  });

  assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.doesNotMatch(html, /<script>alert\(1\)<\/script>/);
  assert.match(html, /&lt;b&gt;x&lt;\/b&gt;/);
});
