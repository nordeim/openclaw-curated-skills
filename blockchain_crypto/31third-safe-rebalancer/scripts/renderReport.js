function esc(value) {
  return String(value ?? '-')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderPostTradeTemplate(data) {
  const rows = (data.trades || [])
    .map(
      (t) =>
        `<tr><td>${esc(t.sequence)}</td><td>${esc(t.fromToken)}</td><td>${esc(t.toToken)}</td><td>${esc(t.venue)}</td><td>${esc(t.volumeOut)}</td><td>${esc(t.avgPrice)}</td><td>${esc(t.priceImpact)}</td></tr>`
    )
    .join('');

  return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>31Third Trade Report</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 24px; color: #222; }
      h1 { margin-bottom: 8px; }
      h2 { margin-top: 24px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
      table { width: 100%; border-collapse: collapse; margin-top: 8px; }
      th, td { border: 1px solid #ddd; padding: 8px; font-size: 12px; text-align: left; }
      .muted { color: #666; font-size: 12px; }
    </style>
  </head>
  <body>
    <h1>31Third Post-Trade Report</h1>
    <p class="muted">Ref: ${esc(data.refId)} | Time: ${esc(data.executionTime)}</p>

    <h2>Vault</h2>
    <p>Vault: ${esc(data.vaultName)} (${esc(data.vaultAddress)})</p>
    <p>Manager: ${esc(data.managerAddress)}</p>

    <h2>Performance</h2>
    <p>Pre-Trade Value: ${esc(data.preTradeValue)}</p>
    <p>Post-Trade Value: ${esc(data.postTradeValue)}</p>
    <p>Friction (bps): ${esc(data.frictionBps)}</p>

    <h2>Trades</h2>
    <table>
      <thead>
        <tr>
          <th>#</th><th>From</th><th>To</th><th>Venue</th><th>Out</th><th>Avg Price</th><th>Impact</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>

    <h2>Costs</h2>
    <p>Service Fee: ${esc(data.serviceFee)}</p>
    <p>Network Fee: ${esc(data.networkFee)}</p>
    <p>Total Costs: ${esc(data.totalCosts)}</p>
    <p>Max Slippage: ${esc(data.maxSlippage)}</p>
    <p>Realized Variance: ${esc(data.realizedVariance)}</p>
    <p>Tx Hash: ${esc(data.txHash)}</p>
  </body>
</html>`;
}

module.exports = { renderPostTradeTemplate, esc };
