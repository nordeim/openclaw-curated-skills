---
name: riskofficer
description: Risk management and portfolio analytics — VaR, Monte Carlo, stress tests, Risk Parity and Calmar optimization. Assess risk, run scenarios, and optimize allocations on virtual portfolios (no real orders).
metadata: {"openclaw":{"requires":{"env":["RISK_OFFICER_TOKEN"]},"primaryEnv":"RISK_OFFICER_TOKEN","emoji":"📊","homepage":"https://riskofficer.tech"}}
---

## RiskOfficer Portfolio Management

Connects to the RiskOfficer API to manage investment portfolios and calculate financial risk metrics.

### Scope: analysis and research only (virtual portfolios)

**All portfolio data and operations in this skill take place inside RiskOfficer’s own environment.** Portfolios you create, edit, or optimize here are **virtual** — they are used for analysis and research only. The agent can:

- **Read** your portfolios (including those synced from brokers) to show positions, history, and risk metrics  
- **Create and change** virtual/manual portfolios and run optimizations **inside RiskOfficer**  
- **Run calculations** (VaR, Monte Carlo, stress tests) on these portfolios  

**Nothing in this skill places or executes real orders** in your broker account. Broker sync is read-only for analysis; any rebalancing or trading in the real account is done by you in your broker’s app or in RiskOfficer’s own flows, not by the assistant. The token is used only to access RiskOfficer’s API for this analytical and research use.

### Setup

1. Open RiskOfficer app → Settings → API Keys
2. Create a new token named "OpenClaw"
3. Set environment variable: `RISK_OFFICER_TOKEN=ro_pat_...`

Or configure in `~/.openclaw/openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "riskofficer": {
        "enabled": true,
        "apiKey": "ro_pat_..."
      }
    }
  }
}
```

### API Base URL

```
https://api.riskofficer.tech/api/v1
```

All requests require: `Authorization: Bearer ${RISK_OFFICER_TOKEN}`

---

## Available Commands

### Ticker Search

#### Search Tickers
Use this **before creating or editing any portfolio** to validate ticker symbols and get their currency/exchange info. Also use when the user mentions a company name instead of a ticker.

```bash
curl -s "https://api.riskofficer.tech/api/v1/tickers/search?q=Apple&limit=10&locale=en" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**Query params:**
- `q` (optional): search query — by ticker, name, or full name (case-insensitive). Omit to get popular tickers sorted by popularity.
- `limit` (optional, default 20, max 50): number of results
- `include_prices` (optional, default `false`): include `current_price`, `price_change_percent`, `price_change_absolute`, `price_date`
- `locale` (optional, default `ru`): `en` for English names, `ru` for Russian names
- `exchange` (optional): filter by exchange — `MOEX`, `NYSE`, `NASDAQ`, `CRYPTO`

**Response:** `tickers` array, each with: `ticker`, `name`, `full_name`, `instrument_type`, `currency`, `exchange`, `popularity_score`, `isin`.

**Instrument types:** `share`, `bond`, `etf`, `futures`, `futures_continuous` (e.g. BR, SI on MOEX), `currency`, `crypto`

**Key rules:**
- Always use ticker search to resolve company names → ticker symbols (e.g. "Apple" → "AAPL", "Sberbank" → "SBER")
- Use `currency` field from the result to check same-currency constraint before adding to a portfolio
- MOEX futures: searching "BR" or "SI" returns the continuous contract, not individual contracts (BRF6, SIM5)
- Use `include_prices=true` to show current price when user asks "how much is X worth?"

```bash
# Search by company name (English)
curl -s "https://api.riskofficer.tech/api/v1/tickers/search?q=Gazprom&locale=en&limit=5" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"

# Search by Russian name
curl -s "https://api.riskofficer.tech/api/v1/tickers/search?q=%D0%93%D0%B0%D0%B7%D0%BF%D1%80%D0%BE%D0%BC&locale=ru&limit=5" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"

# Get current price for a ticker
curl -s "https://api.riskofficer.tech/api/v1/tickers/search?q=AAPL&include_prices=true" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"

# Get popular tickers (no query param)
curl -s "https://api.riskofficer.tech/api/v1/tickers/search?limit=10&include_prices=true" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"

# Filter by exchange
curl -s "https://api.riskofficer.tech/api/v1/tickers/search?q=SBER&exchange=MOEX" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

#### Get Historical Ticker Prices
When the user asks about price history, chart data, or trends for specific assets:

```bash
curl -s "https://api.riskofficer.tech/api/v1/tickers/historical?tickers=SBER,GAZP,AAPL&days=30" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**Query params:** `tickers` (required, comma-separated, max 50), `days` (optional, default 7, max 252 trading days).

**Response:** `data` object keyed by ticker symbol, each with:
- `prices`: array of `{date, close}` objects
- `current_price`, `price_change_percent`, `price_change_absolute`

---

### Portfolio Management

#### List Portfolios
When the user asks to see their portfolios or wants an overview:

```bash
curl -s "https://api.riskofficer.tech/api/v1/portfolios/list" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**Query params:** `portfolio_type` (optional): `"production"` (manual + live brokers), `"sandbox"` (broker sandbox only), `"all"` (default).

Response: array of portfolios with `snapshot_id`, `name`, `total_value`, `currency`, `positions_count`, `broker`, `sandbox`, `active_snapshot_id` (UUID or null — if set, risk calculations use this historical snapshot instead of the latest).

#### Get Portfolio Details
When the user wants to see positions in a specific portfolio:

```bash
curl -s "https://api.riskofficer.tech/api/v1/portfolio/snapshot/{snapshot_id}" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

Response: `name`, `total_value`, `currency`, `positions` (array with `ticker`, `quantity`, `current_price`, `value`, `weight`, `avg_price`).

#### Get Portfolio History
When the user asks how their portfolio changed over time or wants to browse past snapshots:

```bash
curl -s "https://api.riskofficer.tech/api/v1/portfolio/history?days=30" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**Query params:** `days` (optional, default 30, range 1–365).

Response: `snapshots` array with `snapshot_id`, `timestamp`, `total_value`, `positions_count`, `sync_source`, `type` (`aggregated`/`manual`/`broker`), `name`, `broker`, `sandbox`.

#### Get Snapshot Diff (compare two portfolio versions)
When the user wants to compare two portfolio states (e.g. before/after rebalancing, or two dates):

```bash
curl -s "https://api.riskofficer.tech/api/v1/portfolio/snapshot/{snapshot_id}/diff?compare_to={other_snapshot_id}" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

Response: `added`/`removed`/`modified` positions, `total_value_delta`. Both snapshots must belong to the user.

#### Get Aggregated Portfolio
When the user asks for their total or combined portfolio across all accounts:

```bash
curl -s "https://api.riskofficer.tech/api/v1/portfolio/aggregated?type=all" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**Query params:**
- `type=production` — manual + broker live accounts
- `type=sandbox` — broker sandbox only
- `type=all` — everything (default)

**Response:**
- `portfolio.positions` — all positions merged across portfolios
- `portfolio.total_value` — total in base currency
- `portfolio.currency` — base currency (`RUB` or `USD`)
- `portfolio.sources_count` — number of portfolios aggregated

**Example response:**
```json
{
  "portfolio": {
    "positions": [
      {"ticker": "SBER", "quantity": 150, "value": 42795, "sources": ["T-Bank", "Manual"]},
      {"ticker": "AAPL", "quantity": 10, "value": 189500, "original_currency": "USD"}
    ],
    "total_value": 1500000,
    "currency": "RUB",
    "sources_count": 3
  },
  "snapshot_id": "uuid-of-aggregated"
}
```

Positions in different currencies are automatically converted using current CBR exchange rates.

#### Change Base Currency (Aggregated Portfolio)
When the user wants to see the aggregated portfolio in a different currency:

```bash
curl -s -X PATCH "https://api.riskofficer.tech/api/v1/portfolio/{aggregated_snapshot_id}/settings" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"base_currency": "USD"}'
```

**Supported currencies:** `RUB`, `USD`. The aggregated portfolio recalculates automatically after change.

**User prompt examples:**
- "Show everything in dollars" / "Покажи всё в долларах" → `base_currency: "USD"`
- "Switch to rubles" / "Переведи в рубли" → `base_currency: "RUB"`

#### Include/Exclude Portfolio from Aggregated
When the user wants to exclude a specific portfolio from total calculations:

```bash
curl -s -X PATCH "https://api.riskofficer.tech/api/v1/portfolio/{snapshot_id}/settings" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"include_in_aggregated": false}'
```

**User prompt examples:**
- "Exclude sandbox from total" / "Не учитывай песочницу в общем портфеле"
- "Remove demo portfolio from calculations" / "Убери демо-портфель из расчёта"

#### Create Manual Portfolio
When the user wants to create a new portfolio with specific positions:

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/portfolio/manual" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Portfolio",
    "positions": [
      {"ticker": "SBER", "quantity": 100},
      {"ticker": "GAZP", "quantity": 50, "avg_price": 148.0},
      {"ticker": "YNDX", "quantity": -20}
    ]
  }'
```

**Fields:**
- `ticker` (required): ticker symbol. **Always use `/tickers/search` first** to validate and check currency.
- `quantity` (required): number of shares. **Negative = short position** (e.g. `-20` = short 20 shares).
- `avg_price` (optional): average purchase/entry price for P&L tracking. If omitted on new portfolio → uses current market price. If omitted on edit → inherits from previous snapshot.

**Query params:** `locale` (optional, default `ru`) — affects asset name resolution.

**IMPORTANT — Single Currency Rule:**
All assets in one portfolio must be in the **same currency**.
- RUB assets (MOEX): SBER, GAZP, LKOH, YNDX, etc.
- USD assets (NYSE/NASDAQ): AAPL, MSFT, GOOGL, TSLA, etc.
Cannot mix currencies in a single portfolio! Suggest creating separate portfolios.

**Short positions:**
- Use negative `quantity` for shorts (e.g. `{"ticker": "GAZP", "quantity": -50}`)
- Long + short in the same portfolio is supported (long-short portfolio)
- When optimizing a long-short portfolio, use `optimization_mode: "preserve_directions"` to keep shorts

#### Update Portfolio (Add/Remove Positions)
When the user wants to modify an existing portfolio:

1. Get current positions:
```bash
curl -s "https://api.riskofficer.tech/api/v1/portfolio/snapshot/{snapshot_id}" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

2. Repost with the same name and updated full positions list:
```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/portfolio/manual" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "<same name>", "positions": [<complete updated list>]}'
```

**IMPORTANT:** Always show the user what will change and ask for confirmation before updating. `avg_price` is preserved from previous snapshot unless explicitly specified.

#### Delete Manual Portfolio
When the user wants to delete/remove a manual portfolio entirely:

```bash
curl -s -X DELETE "https://api.riskofficer.tech/api/v1/portfolio/manual/My%20Portfolio" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

- Portfolio name must be URL-encoded
- Archives **all** snapshots for that portfolio — **irreversible**
- **ALWAYS confirm with the user before deleting** — cannot be undone
- Response: `archived_snapshots` count, `portfolio_name`, `message`

#### Delete Broker Portfolio Snapshots
When the user wants to clear broker portfolio history without disconnecting the broker:

```bash
curl -s -X DELETE "https://api.riskofficer.tech/api/v1/portfolio/broker/tinkoff?sandbox=false" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

- `sandbox=true` for sandbox portfolio, `sandbox=false` for live/production
- Archives snapshots only; broker connection stays active
- Next sync will create a new snapshot
- **ALWAYS confirm before deleting**

---

### Broker Integration

#### List Connected Brokers
When the user asks about their broker connections:

```bash
curl -s "https://api.riskofficer.tech/api/v1/brokers/connections" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

#### List Available Broker Providers
When the user asks what brokers are supported:

```bash
curl -s "https://api.riskofficer.tech/api/v1/brokers/available" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

#### Sync Portfolio from Broker
When the user wants to refresh/update their portfolio from a connected broker:

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/portfolio/proxy/broker/{broker}/portfolio" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"sandbox": false}'
```

- `{broker}`: `tinkoff` or `alfa`
- `sandbox`: `false` for live account, `true` for Tinkoff sandbox

If response is `400` with `missing_api_key`, the broker is not connected. Guide the user:
1. Get API token from https://www.tbank.ru/invest/settings/api/
2. Open RiskOfficer app → Settings → Brokers → Connect Tinkoff
3. Paste token and connect

#### Disconnect Broker
When the user wants to remove a broker connection:

```bash
curl -s -X DELETE "https://api.riskofficer.tech/api/v1/brokers/connections/tinkoff?sandbox=false" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

- `sandbox=false` for live connection, `sandbox=true` for sandbox
- Removes the connection and its saved API key; portfolio snapshot **history is preserved**
- To also delete snapshot history, first use `DELETE /portfolio/broker/{broker}?sandbox=false`
- **ALWAYS confirm before disconnecting** — reconnection requires the mobile app

**Difference between the two delete endpoints:**

| Action | DELETE /portfolio/broker/{id} | DELETE /brokers/connections/{id} |
|--------|-------------------------------|----------------------------------|
| Deletes snapshots | ✅ Yes (archives history) | ❌ No (history kept) |
| Deletes connection | ❌ No | ✅ Yes |
| Can sync again without re-connecting | ✅ Yes | ❌ No |

---

### Active Snapshot Selection

By default, all risk calculations use the **latest** snapshot. You can pin a historical snapshot to run calculations on a past portfolio state — useful for backtesting risk or comparing "before vs after" rebalancing.

#### Set Active Snapshot
When the user wants to run risk calculations on a historical version of their portfolio:

```bash
curl -s -X PATCH "https://api.riskofficer.tech/api/v1/portfolio/active-snapshot" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"portfolio_key": "manual:My Portfolio", "snapshot_id": "{historical_snapshot_id}"}'
```

**`portfolio_key` format:**
| Portfolio type | Format | Example |
|---|---|---|
| Aggregated | `aggregated` | `"aggregated"` |
| Manual | `manual:{name}` | `"manual:My Portfolio"` |
| Broker live | `broker:{broker_id}:false` | `"broker:tinkoff:false"` |
| Broker sandbox | `broker:{broker_id}:true` | `"broker:tinkoff:true"` |

**Workflow:**
1. `GET /portfolio/history?days=90` → pick snapshot by date
2. `PATCH /portfolio/active-snapshot` with chosen `snapshot_id` + `portfolio_key`
3. Run VaR / Monte Carlo — uses selected historical snapshot
4. Reset when done (see below)

**In `/portfolios/list`:** `active_snapshot_id` field shows the pinned snapshot (null = using latest).

#### Reset Active Snapshot to Latest

```bash
curl -s -X DELETE "https://api.riskofficer.tech/api/v1/portfolio/active-snapshot?portfolio_key=manual:My%20Portfolio" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**User prompt examples:**
- "Calculate risk for my portfolio as it was a month ago" / "Посчитай риски как было месяц назад" → set active snapshot
- "Go back to current portfolio" / "Сбрось на текущий портфель" → DELETE active-snapshot

---

### Risk Calculations

#### Calculate VaR (FREE)
When the user asks to calculate risk, VaR, or risk metrics:

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/risk/calculate-var" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_snapshot_id": "{snapshot_id}",
    "method": "historical",
    "confidence": 0.95,
    "horizon_days": 1,
    "force_recalc": false
  }'
```

**Parameters:**
- `method`: `"historical"` (default, recommended), `"parametric"`, or `"garch"`
- `confidence`: confidence level, default `0.95` (range 0.01–0.99)
- `horizon_days`: forecast horizon, default `1` (range 1–30 days)
- `force_recalc` (optional, default `false`): set `true` to bypass cache and force a fresh calculation (use when user says "recalculate" or "refresh")

**Response:**
- If `reused_existing: true` and `status: "done"` → result is already in response (`var_95`, `cvar_95`, `sharpe_ratio`), no polling needed
- Otherwise → returns `calculation_id`, poll for result:

```bash
curl -s "https://api.riskofficer.tech/api/v1/risk/calculation/{calculation_id}" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

Wait until `status: "done"`, then present results.

#### Get VaR / Risk Calculation History
When the user asks for past risk calculations:

```bash
curl -s "https://api.riskofficer.tech/api/v1/risk/history?limit=50" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

**Query params:** `limit` (optional, default 50, max 100).

Response: `calculations` array with `calculation_id`, `portfolio_snapshot_id`, `status`, `method`, `var_95`, `cvar_95`, `sharpe_ratio`, `created_at`, `completed_at`.

#### Run Monte Carlo (QUANT — currently free for all users)
When the user asks for a Monte Carlo simulation:

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/risk/monte-carlo" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_snapshot_id": "{snapshot_id}",
    "simulations": 1000,
    "horizon_days": 365,
    "model": "gbm",
    "force_recalc": false
  }'
```

**Parameters:**
- `simulations`: number of paths, default `1000` (range 100–10000)
- `horizon_days`: forecast horizon, default `365` (range 1–365)
- `model`: `"gbm"` (Geometric Brownian Motion, recommended) or `"garch"`
- `confidence_levels` (optional): array of percentiles, default `[0.05, 0.50, 0.95]`
- `force_recalc` (optional, default `false`): bypass cache

Poll: `GET /api/v1/risk/monte-carlo/{simulation_id}`

#### Run Stress Test (QUANT — currently free for all users)
When the user asks for a stress test against historical crises:

First, get available crises:
```bash
curl -s "https://api.riskofficer.tech/api/v1/risk/stress-test/crises" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

Then run:
```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/risk/stress-test" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_snapshot_id": "{snapshot_id}",
    "crisis": "covid_19",
    "force_recalc": false
  }'
```

**Parameters:**
- `crisis`: crisis scenario ID from `/stress-test/crises` (e.g. `covid_19`, `2008_crisis`)
- `force_recalc` (optional, default `false`): bypass cache

Poll: `GET /api/v1/risk/stress-test/{stress_test_id}`

---

### Portfolio Optimization (QUANT — currently free for all users)

#### Risk Parity Optimization
When the user asks to optimize their portfolio or balance risks:

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/portfolio/{snapshot_id}/optimize" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "optimization_mode": "preserve_directions",
    "constraints": {
      "max_weight": 0.30,
      "min_weight": 0.02
    }
  }'
```

**`optimization_mode`:**
- `"long_only"`: all weights ≥ 0 (shorts are flipped to long before optimization)
- `"preserve_directions"`: keeps long/short directions as-is (default)
- `"unconstrained"`: weights can change sign freely

Poll: `GET /api/v1/portfolio/optimizations/{optimization_id}`
Result: `GET /api/v1/portfolio/optimizations/{optimization_id}/result`

**IMPORTANT:** For optimization, use `active_snapshot_id || snapshot_id` from the portfolio list entry (respects the user's selected historical snapshot if set).

#### Calmar Ratio Optimization
When the user asks to maximize Calmar Ratio (CAGR / |Max Drawdown|):

**Requires 200+ trading days of price history per ticker** (backend requests 252 days). If the portfolio has short history, suggest Risk Parity instead.

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/portfolio/{snapshot_id}/optimize-calmar" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "optimization_mode": "long_only",
    "constraints": {
      "max_weight": 0.50,
      "min_weight": 0.05,
      "min_expected_return": 0.0,
      "max_drawdown_limit": 0.15,
      "min_calmar_target": 0.5
    }
  }'
```

Poll: `GET /api/v1/portfolio/optimizations/{optimization_id}` (check `optimization_type === "calmar_ratio"`).
Result: `GET /api/v1/portfolio/optimizations/{optimization_id}/result` — includes `current_metrics` and `optimized_metrics` (CAGR, max drawdown, Calmar ratio, recovery time in days).
Apply: same as Risk Parity → `POST /api/v1/portfolio/optimizations/{optimization_id}/apply`.

**Error `INSUFFICIENT_HISTORY`:** not enough price history → explain the 200+ days requirement and suggest Risk Parity as alternative.

#### Apply Optimization
**IMPORTANT:** Always show the full rebalancing plan and ask for explicit user confirmation before applying!

```bash
curl -s -X POST "https://api.riskofficer.tech/api/v1/portfolio/optimizations/{optimization_id}/apply" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

Response: `new_snapshot_id`. Can only be applied once per optimization.

---

### Subscription Status

> **Note:** Quant subscription is currently **FREE for all users**. All features work without payment.

```bash
curl -s "https://api.riskofficer.tech/api/v1/subscription/status" \
  -H "Authorization: Bearer ${RISK_OFFICER_TOKEN}"
```

Currently all users return `has_subscription: true`.

---

## Async Operations

VaR, Monte Carlo, Stress Test, and Optimization are **asynchronous**.

**Polling pattern:**
1. POST endpoint → get `calculation_id` / `simulation_id` / `optimization_id`
2. Poll GET endpoint every 2–3 seconds
3. Check `status`:
   - `pending` or `processing` → keep polling
   - `done` → present results
   - `failed` → show error

**Typical times:**
| Operation | Typical time |
|-----------|-------------|
| VaR | 3–10 seconds |
| Monte Carlo | 10–30 seconds |
| Stress Test | 5–15 seconds |
| Optimization | 10–30 seconds |

**User communication:**
- Show "Calculating..." immediately after starting
- If polling takes > 10 seconds: "Still calculating, please wait..."
- Always show the final result or error

---

## Important Rules

0. **Virtual / analytical scope:** Portfolios and all operations (create, optimize, delete, sync) exist only inside RiskOfficer. This skill is for analysis and research; it does not place or execute real broker orders.

1. **Single Currency Rule (manual/broker portfolios):** Each portfolio must contain same-currency assets. Cannot mix SBER (RUB) with AAPL (USD). Aggregated portfolio is the exception — it auto-converts using CBR rates.

2. **Short Positions:** Negative `quantity` creates a short. For long-short portfolios, use `optimization_mode: "preserve_directions"` to keep short positions when optimizing.

3. **Always search tickers first:** Before creating or editing portfolios, use `/tickers/search` to validate ticker symbols and check their currency.

4. **Confirmations:** Always show what will change and ask for confirmation before: updating/deleting portfolios, applying optimizations, disconnecting brokers. These actions can be irreversible.

5. **Async:** VaR, Monte Carlo, Stress Test, and Optimization are async. Poll for results.

6. **Subscription:** Monte Carlo, Stress Test, and Optimization are Quant features (currently free). VaR is always free.

7. **Broker Integration:** Users must connect brokers via the RiskOfficer mobile app first. Cannot connect via chat (security).

8. **Error Handling:**
   - `401 Unauthorized` → Token invalid or expired; user needs to recreate it
   - `403 subscription_required` → Need Quant subscription (currently free for all)
   - `400 missing_api_key` → Broker not connected via app
   - `400 currency_mismatch` → Mixed currencies in a single portfolio
   - `400 INSUFFICIENT_HISTORY` → Not enough price history for Calmar (200+ trading days needed); suggest Risk Parity
   - `404 Not Found` → Portfolio or snapshot not found (may have been deleted)
   - `429 Too Many Requests` → Optimization rate limit reached

9. **Active Snapshot:** `active_snapshot_id` from `/portfolios/list` takes priority over `snapshot_id` when running calculations. Use `active_snapshot_id || snapshot_id` for optimization calls.

---

## Example Conversations

### User wants to see their portfolios
"Show my portfolios" / "Покажи мои портфели"
→ `GET /portfolios/list`
→ Format nicely: name, total value, positions count, currency, last updated

### User wants the combined total across all accounts
"Show total portfolio" / "Total across all accounts" / "Сколько у меня всего?"
→ `GET /portfolio/aggregated?type=all`
→ Show total value, merged positions, number of sources
→ Note positions converted from other currencies

### User wants to change display currency
"Show everything in dollars" / "Покажи в долларах"
→ `PATCH /portfolio/{aggregated_id}/settings` with `{"base_currency": "USD"}`
→ `GET /portfolio/aggregated` again
→ Show portfolio in new currency

### User asks about a company by name (not ticker)
"Add Sberbank to my portfolio" / "What's the ticker for Gazprom?" / "Добавь Газпром"
→ `GET /tickers/search?q=Sberbank&locale=en`
→ Found: ticker `SBER`, currency `RUB`, exchange `MOEX`
→ Confirm with user, then proceed to create/update portfolio

### User asks for a current price
"How much is Tesla?" / "Сколько стоит Газпром?"
→ `GET /tickers/search?q=TSLA&include_prices=true`
→ Show `current_price`, `price_change_percent`, exchange

### User wants to create a long-short portfolio
"Create portfolio: long SBER 100 shares, short YNDX 50 shares"
→ `GET /tickers/search` for both tickers → confirm both are RUB/MOEX
→ `POST /portfolio/manual` with `[{"ticker":"SBER","quantity":100},{"ticker":"YNDX","quantity":-50}]`
→ Show created portfolio with positions

### User wants to analyze portfolio risk
"What are the risks of my portfolio?" / "Analyze the risk"
→ `GET /portfolios/list` → find portfolio
→ `POST /risk/calculate-var` with `method: "historical"`
→ Poll until done
→ Present VaR, CVaR, volatility, risk contributions per ticker
→ Offer optimization if risks are concentrated

### User wants Calmar optimization
"Optimize by Calmar ratio" / "Maximize return per drawdown" / "Оптимизируй по Калмару"
→ Get `snapshot_id` from portfolios list
→ `POST /portfolio/{snapshot_id}/optimize-calmar`
→ If `INSUFFICIENT_HISTORY`: explain 200+ trading days needed, suggest Risk Parity
→ Poll until done
→ Show `current_metrics` vs `optimized_metrics` (Calmar ratio, CAGR, max drawdown)
→ Show rebalancing plan and ask for confirmation before apply

### User wants Monte Carlo simulation
"Run Monte Carlo for 1 year" / "Запусти Монте-Карло"
→ `POST /risk/monte-carlo` with `simulations: 1000, horizon_days: 365, model: "gbm"`
→ Poll until done
→ Present percentile projections (5th, 50th, 95th)

### User wants a stress test
"Run stress test" / "How would my portfolio survive 2008 crisis?"
→ `GET /risk/stress-test/crises` → show available scenarios
→ User picks crisis (or default to most relevant)
→ `POST /risk/stress-test`
→ Poll, then present results

### User wants to calculate risk for a historical portfolio
"Calculate risk for my portfolio as it was last month" / "Посчитай риски как было месяц назад"
→ `GET /portfolio/history?days=45` → find snapshot from ~30 days ago
→ `PATCH /portfolio/active-snapshot` with that `snapshot_id` and `portfolio_key`
→ `POST /risk/calculate-var` → poll → present results
→ Offer to reset: `DELETE /portfolio/active-snapshot`

### User tries to mix currencies
"Add Apple to my RUB portfolio"
→ `GET /tickers/search?q=AAPL` → currency: USD, exchange: NASDAQ
→ Portfolio is RUB → cannot mix
→ Explain the single-currency rule, suggest creating a separate USD portfolio

### User wants to compare two portfolio snapshots
"What changed in my portfolio?" / "Compare to last week" / "Что изменилось в портфеле?"
→ `GET /portfolio/history` → get two snapshot IDs
→ `GET /portfolio/snapshot/{id}/diff?compare_to={other_id}`
→ Present added/removed/modified positions, total value delta

### User wants to delete a portfolio
"Delete my test portfolio" / "Удали портфель 'Тест'"
→ Confirm: "This will permanently delete all N snapshots for 'Test'. Cannot be undone. Continue?"
→ On confirmation: `DELETE /portfolio/manual/Test`
→ Report `archived_snapshots` count

### User wants to disconnect a broker
"Disconnect Tinkoff" / "Отключи Тинькофф"
→ Confirm: "This will remove the Tinkoff connection. Portfolio history will be kept. Continue?"
→ On confirmation: `DELETE /brokers/connections/tinkoff?sandbox=false`
→ Inform that reconnection requires the mobile app
