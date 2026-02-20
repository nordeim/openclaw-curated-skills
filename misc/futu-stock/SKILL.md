---
name: futu-stock
description: Access Futu stock market data via MCP server - real-time quotes, K-lines, options, account info for HK/US/CN markets
metadata: {"openclaw": {"emoji": "📈", "requires": {"bins": ["python3", "futu-mcp-server"], "env": ["FUTU_HOST", "FUTU_PORT"]}, "primaryEnv": "FUTU_HOST"}}
version: 1.0.0
---

# futu-stock Skill

This skill provides dynamic access to the Futu stock market data MCP server, supporting real-time quotes, historical K-lines, options data, and account information for Hong Kong, US, and China stock markets.

## Prerequisites

Before using this skill, you need to set up two components:

### 1. Install futu-stock-mcp-server

Install the MCP server package:

```bash
pip install futu-stock-mcp-server
```

**Repository**: https://github.com/shuizhengqi1/futu-stock-mcp-server

After installation, verify the command is available:

```bash
which futu-mcp-server
# or
futu-mcp-server --help
```

### 2. Install and Configure Futu OpenD

Futu OpenD is the gateway service that connects to Futu's trading platform. You must install and run it before using this skill.

**Installation Guide**: https://openapi.futunn.com/futu-api-doc/opend/opend-cmd.html

**Quick Setup Steps**:

1. **Download OpenD** for your platform (Windows/MacOS/CentOS/Ubuntu)
2. **Extract** the package and locate:
   - `FutuOpenD.xml` (or `OpenD.xml`) - Configuration file
   - `Appdata.dat` - Required data file
3. **Configure** `FutuOpenD.xml`:
   - Set `login_account`: Your Futu account (platform ID, email, or phone)
   - Set `login_pwd`: Your login password (or use `login_pwd_md5` for MD5 hash)
   - Set `api_port`: API port (default: 11111)
   - Set `ip`: Listen address (default: 127.0.0.1)
4. **Test Run**: Start OpenD once to verify configuration:
   ```bash
   # Windows
   FutuOpenD.exe
   
   # Linux
   ./FutuOpenD
   
   # MacOS
   ./FutuOpenD.app/Contents/MacOS/FutuOpenD
   ```
5. **Background Start**: Once verified, start OpenD in background using `nohup`:
   ```bash
   # Linux/MacOS
   nohup ./FutuOpenD > opend.log 2>&1 &
   
   # Or with specific config file
   nohup ./FutuOpenD -cfg_file=/path/to/FutuOpenD.xml > opend.log 2>&1 &
   ```

**Important Notes**:
- OpenD must be running before using this skill
- Default API port is `11111` (configure in `FutuOpenD.xml`)
- Ensure OpenD is accessible at the configured `FUTU_HOST` and `FUTU_PORT`
- For production use, consider using a process manager (systemd, supervisor, etc.) instead of `nohup`

### 3. Verify Setup

After both components are installed:

1. **Check OpenD is running**:
   ```bash
   # Check if port is listening
   netstat -an | grep 11111
   # or
   lsof -i :11111
   ```

2. **Test MCP server connection**:
   ```bash
   # Set environment variables
   export FUTU_HOST=127.0.0.1
   export FUTU_PORT=11111
   
   # Test MCP server
   futu-mcp-server
   ```

If everything is configured correctly, you can now use this skill.

## Complete Setup Workflow

**Summary of the complete setup process**:

1. **Install futu-stock-mcp-server**:
   ```bash
   pip install futu-stock-mcp-server
   ```

2. **Install and configure Futu OpenD**:
   - Download OpenD from Futu's official site
   - Extract and configure `FutuOpenD.xml` with your account credentials
   - Test run OpenD once to ensure configuration is correct
   - Start OpenD in background using `nohup`:
     ```bash
     nohup ./FutuOpenD > opend.log 2>&1 &
     ```

3. **Configure environment variables**:
   - Set `FUTU_HOST` (default: `127.0.0.1`)
   - Set `FUTU_PORT` (default: `11111`)

4. **Use the skill**: Once OpenD is running and environment variables are set, you can use this skill to access Futu stock market data.

**Important**: OpenD must be running before using this skill. If OpenD stops, the skill will not be able to connect to Futu's services.

## Context Efficiency

Traditional MCP approach:
- All 20+ tools loaded at startup
- Estimated context: 500+ tokens

This skill approach:
- Metadata only: ~100 tokens
- Full instructions (when used): ~5k tokens
- Tool execution: 0 tokens (runs externally)

## How This Works

Instead of loading all MCP tool definitions upfront, this skill:
1. Tells you what tools are available (just names and brief descriptions)
2. You decide which tool to call based on the user's request
3. Generate a JSON command to invoke the tool
4. The executor handles the actual MCP communication

## Available Tools

### Market Data Query
- `get_stock_quote`: Get stock quote data for given symbols (price, volume, turnover, etc.)
- `get_market_snapshot`: Get market snapshot with bid/ask data for given symbols
- `get_cur_kline`: Get current K-line data (requires subscription first)
- `get_history_kline`: Get historical K-line data (limited to 30 stocks per 30 days)
- `get_rt_data`: Get real-time data (requires RT_DATA subscription)
- `get_ticker`: Get ticker data (requires TICKER subscription)
- `get_order_book`: Get order book data (requires ORDER_BOOK subscription)
- `get_broker_queue`: Get broker queue data (requires BROKER subscription)

### Subscription Management
- `subscribe`: Subscribe to real-time data (QUOTE, ORDER_BOOK, TICKER, RT_DATA, BROKER, K-lines)
- `unsubscribe`: Unsubscribe from real-time data

### Options Data
- `get_option_chain`: Get option chain data with Greeks
- `get_option_expiration_date`: Get option expiration dates
- `get_option_condor`: Get option condor strategy data
- `get_option_butterfly`: Get option butterfly strategy data

### Account Information
- `get_account_list`: Get account list
- `get_funds`: Get account funds information
- `get_positions`: Get account positions
- `get_max_power`: Get maximum trading power
- `get_margin_ratio`: Get margin ratio for a security

### Market Status
- `get_market_state`: Get market state

**Supported Markets:**
- HK: Hong Kong stocks (e.g., `HK.00700`)
- US: US stocks (e.g., `US.AAPL`)
- SH: Shanghai stocks (e.g., `SH.600519`)
- SZ: Shenzhen stocks (e.g., `SZ.000001`)

## Usage Pattern

When the user's request matches this skill's capabilities:

**Step 1: Identify the right tool** from the list above

**Step 2: Generate a tool call** in this JSON format:

```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Step 3: Execute via bash:**

```bash
cd {baseDir}
python3 executor.py --call 'YOUR_JSON_HERE'
```

IMPORTANT: Use `{baseDir}` to reference the skill folder path.

## Getting Tool Details

If you need detailed information about a specific tool's parameters:

```bash
cd {baseDir}
python3 executor.py --describe tool_name
```

This loads ONLY that tool's schema, not all tools.

## Examples

### Example 1: Get stock quote

User: "查询 HK.03690 的最新价"

Your workflow:
1. Identify tool: `get_stock_quote` or `get_market_snapshot`
2. Generate call JSON
3. Execute:

```bash
cd {baseDir}
python3 executor.py --call '{"tool": "get_market_snapshot", "arguments": {"symbols": ["HK.03690"]}}'
```

### Example 2: Subscribe and get real-time data

For tools requiring subscription (like `get_cur_kline`, `get_rt_data`):

1. First subscribe:
```bash
cd {baseDir}
python3 executor.py --call '{"tool": "subscribe", "arguments": {"symbols": ["HK.03690"], "sub_types": ["QUOTE", "K_DAY"]}}'
```

2. Then query:
```bash
cd {baseDir}
python3 executor.py --call '{"tool": "get_cur_kline", "arguments": {"symbol": "HK.03690", "ktype": "K_DAY", "count": 100}}'
```

### Example 3: Get historical K-line data

```bash
cd {baseDir}
python3 executor.py --call '{"tool": "get_history_kline", "arguments": {"symbol": "HK.03690", "ktype": "K_DAY", "start": "2026-01-01", "end": "2026-02-13", "count": 100}}'
```

## Error Handling

If the executor returns an error:
- Check the tool name is correct
- Verify required arguments are provided
- Ensure the MCP server is accessible

## Performance Notes

Context usage comparison for this skill:

| Scenario | MCP (preload) | Skill (dynamic) |
|----------|---------------|-----------------|
| Idle | 500+ tokens | ~100 tokens |
| Active | 500+ tokens | ~5k tokens |
| Executing | 500+ tokens | 0 tokens |

Savings: Significant reduction in context usage for typical workflows.

## Configuration

This skill requires:
- **Python 3** (`python3` must be available on PATH)
- **futu-stock-mcp-server**: Installed via `pip install futu-stock-mcp-server`
- **Futu OpenD**: Installed and running (see Prerequisites above)
- **Environment variables**:
  - `FUTU_HOST`: Futu OpenD host address (default: `127.0.0.1`)
  - `FUTU_PORT`: Futu OpenD API port (default: `11111`)

### OpenClaw Configuration

Configure in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "futu-stock": {
        enabled: true,
        env: {
          FUTU_HOST: "your-futu-host",
          FUTU_PORT: "your-futu-port",
        },
      },
    },
  },
}
```

## Notes

- Stock code format: `{market}.{code}` (e.g., `HK.00700`, `US.AAPL`, `SH.600519`)
- Some tools require subscription before querying (see tool descriptions)
- Historical K-line data is limited to 30 stocks per 30 days
- Maximum 100 symbols per subscription request
- Maximum 500 symbols per socket connection

---

*This skill provides dynamic access to Futu stock market data via MCP server.*
