# MCP Server Setup (Human Operator Only)

This file is for the **human operator** to set up the MCP server on their infrastructure. AI agents should NOT execute these steps.

## Source

Repository: https://github.com/Arven-Digital/sigil-public
Package path: `packages/mcp`

## Setup Steps

1. Clone the repository
2. Navigate to `packages/mcp`
3. Install dependencies with your package manager
4. Build the project
5. Set environment variables: `SIGIL_API_KEY` and `SIGIL_ACCOUNT_ADDRESS`
6. Run the built server

## Available MCP Tools

- `get_account_info` — Check wallet status, balance, policy
- `evaluate_transaction` — Submit transaction for Guardian evaluation
- `create_session_key` — Create time-limited session key
- `freeze_account` — Emergency freeze
- `unfreeze_account` — Unfreeze after review
- `update_policy` — Update spending limits/whitelists
- `get_transaction_history` — View past transactions
- `rotate_agent_key` — Rotate the agent key
- `get_protection_status` — Check Guardian and circuit breaker status
