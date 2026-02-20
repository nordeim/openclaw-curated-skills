# fiscal CLI Command Reference

Complete reference for every fiscal command, flag, type, and default.

## Global Options

All commands accept these flags:

| Flag | Type | Default | Description |
|---|---|---|---|
| `--data-dir <path>` | string | from config | Path to Actual data directory |
| `--budget <id>` | string | from config | Active budget ID |
| `--server-url <url>` | string | from config/env | Actual server URL for sync mode |
| `--password <password>` | string | from config/env | Actual server password |
| `--format <format>` | `record` \| `table` | `record` | Output format |
| `-h, --help` | | | Show help |

## budgets

### `fiscal budgets list`

List all local budgets.

Output columns: `id`, `name`

### `fiscal budgets create <name>`

Create a new budget.

| Argument | Required | Description |
|---|---|---|
| `name` | Yes | Budget name |

### `fiscal budgets use <id>`

Set the active budget in config.

| Argument | Required | Description |
|---|---|---|
| `id` | Yes | Budget ID from `budgets list` |

### `fiscal budgets pull <syncId>`

Download a budget from an Actual server. Requires server credentials.

| Argument | Required | Description |
|---|---|---|
| `syncId` | Yes | Sync ID of the remote budget |

### `fiscal budgets push`

Upload a local budget to an Actual server. Requires server credentials.

## sync

### `fiscal sync`

Push/pull changes with the configured Actual server. Requires server credentials.

## accounts

### `fiscal accounts list`

List all accounts.

Output columns: `id`, `name`, `type`, `offbudget`, `closed`, `balance`

### `fiscal accounts create <name>`

Create an account.

| Flag | Type | Default | Description |
|---|---|---|---|
| `--type <type>` | `checking` \| `savings` \| `credit` \| `investment` \| `mortgage` \| `debt` \| `other` | `checking` | Account type |
| `--offbudget` | boolean | false | Mark as off-budget |
| `--balance <amount>` | decimal | 0 | Initial balance (e.g. `1500.00`, `-1200.00`) |

### `fiscal accounts update <id>`

Update an account.

| Flag | Type | Description |
|---|---|---|
| `--name <name>` | string | New account name |

### `fiscal accounts close <id>`

Close an account.

| Flag | Type | Description |
|---|---|---|
| `--transfer-to <accountId>` | string | Transfer remaining balance to this account |
| `--transfer-category <categoryId>` | string | Category for the transfer transaction |

### `fiscal accounts reopen <id>`

Reopen a closed account.

### `fiscal accounts delete <id>`

Permanently delete an account and all its transactions.

### `fiscal accounts balance <id>`

Get account balance.

| Flag | Type | Default | Description |
|---|---|---|---|
| `--cutoff <date>` | `YYYY-MM-DD` | today | Balance as of this date |

## transactions

### `fiscal transactions list <accountId>`

List transactions for an account within a date range.

| Flag | Type | Required | Description |
|---|---|---|---|
| `--start <date>` | `YYYY-MM-DD` | Yes | Start date (inclusive) |
| `--end <date>` | `YYYY-MM-DD` | Yes | End date (inclusive) |

Output columns: `id`, `date`, `account`, `account_name`, `amount`, `payee`, `payee_name`, `category`, `category_name`, `notes`, `cleared`, `reconciled`, `transfer_id`, `imported_id`

### `fiscal transactions uncategorized`

List uncategorized transactions across all accounts.

| Flag | Type | Description |
|---|---|---|
| `--account <id>` | string | Filter to one account |
| `--start <date>` | `YYYY-MM-DD` | Start date filter |
| `--end <date>` | `YYYY-MM-DD` | End date filter |

### `fiscal transactions triage`

List uncategorized transactions with rule-based suggestions.

| Flag | Type | Description |
|---|---|---|
| `--account <id>` | string | Filter to one account |
| `--start <date>` | `YYYY-MM-DD` | Start date filter |
| `--end <date>` | `YYYY-MM-DD` | End date filter |
| `--limit <n>` | integer | Max rows to return |

### `fiscal transactions categorize`

Assign categories to transactions. Two modes:

**Single-update mode:**

| Flag | Type | Description |
|---|---|---|
| `--id <txnId>` | string | Transaction ID |
| `--category <categoryId>` | string | Category ID to assign |

**Batch mode:**

| Flag | Type | Description |
|---|---|---|
| `--map <mappings>` | string | Comma/newline/semicolon-separated `txnId=categoryId` pairs |
| `--dry-run` | boolean | Preview only, don't apply |

### `fiscal transactions add <accountId>`

Add a single transaction.

| Flag | Type | Required | Description |
|---|---|---|---|
| `--date <date>` | `YYYY-MM-DD` | Yes | Transaction date |
| `--amount <amount>` | decimal | Yes | Amount (e.g. `-45.99` for expense, `1500.00` for income) |
| `--payee <name>` | string | No | Payee name |
| `--category <id>` | string | No | Category ID |
| `--notes <text>` | string | No | Notes |
| `--cleared` | boolean | No | Mark as cleared |

### `fiscal transactions update <id>`

Update a transaction.

| Flag | Type | Description |
|---|---|---|
| `--date <date>` | `YYYY-MM-DD` | New date |
| `--amount <amount>` | decimal | New amount |
| `--notes <text>` | string | New notes |
| `--cleared` | boolean | Set cleared status |
| `--category <id>` | string | New category ID |

### `fiscal transactions batch-update <json>`

Batch update transactions from a JSON array. Each object must include `id` and the fields to update.

### `fiscal transactions delete <id>`

Delete a transaction.

### `fiscal transactions import <accountId> <file>`

Import transactions from a bank file. See [import-guide.md](import-guide.md) for full details.

| Flag | Type | Default | Description |
|---|---|---|---|
| `--no-reconcile` | boolean | false | Disable reconciliation/rule processing |
| `--dry-run` | boolean | false | Preview without committing |
| `--show-rows` | boolean | false | Print individual imported rows |
| `--report` | boolean | false | Print compact import summary |
| `--no-clear` | boolean | false | Don't set cleared=true by default |
| `--no-import-notes` | boolean | false | Skip memo/notes field |
| `--date-format <fmt>` | string | auto | Date format (e.g. `MM/dd/yyyy`) |
| `--fallback-payee-to-memo` | boolean | false | OFX: use memo when payee missing |
| `--multiplier <n>` | number | 1 | Multiply parsed amounts |
| `--flip-amount` | boolean | false | Negate all amounts |

CSV-specific flags:

| Flag | Type | Description |
|---|---|---|
| `--no-csv-header` | boolean | CSV has no header row |
| `--csv-delimiter <char>` | string | Delimiter (default: `,`) |
| `--csv-date-col <name\|index>` | string | Date column |
| `--csv-amount-col <name\|index>` | string | Signed amount column |
| `--csv-payee-col <name\|index>` | string | Payee column |
| `--csv-notes-col <name\|index>` | string | Notes column |
| `--csv-category-col <name\|index>` | string | Category column |
| `--csv-inflow-col <name\|index>` | string | Inflow column (alt. to amount) |
| `--csv-outflow-col <name\|index>` | string | Outflow column (alt. to amount) |
| `--csv-inout-col <name\|index>` | string | In/out marker column |
| `--csv-out-value <value>` | string | Value treated as outflow |
| `--csv-skip-start <n>` | integer | Skip N lines at start |
| `--csv-skip-end <n>` | integer | Skip N lines at end |

## categories

### `fiscal categories list`

List category groups with their categories.

Output columns: `id`, `name`, `group_id`, `group_name`, `is_income`, `hidden`

### `fiscal categories create <name>`

| Flag | Type | Required | Description |
|---|---|---|---|
| `--group <groupId>` | string | Yes | Parent category group ID |
| `--income` | boolean | No | Mark as income category |

### `fiscal categories update <id>`

| Flag | Type | Description |
|---|---|---|
| `--name <name>` | string | New name |

### `fiscal categories delete <id>`

| Flag | Type | Description |
|---|---|---|
| `--transfer-to <categoryId>` | string | Reassign transactions to another category |

### `fiscal categories create-group <name>`

| Flag | Type | Description |
|---|---|---|
| `--income` | boolean | Mark as income group |

### `fiscal categories update-group <id>`

| Flag | Type | Description |
|---|---|---|
| `--name <name>` | string | New name |

### `fiscal categories delete-group <id>`

| Flag | Type | Description |
|---|---|---|
| `--transfer-to <categoryId>` | string | Reassign transactions to another category |

## payees

### `fiscal payees list`

List all payees.

Output columns: `id`, `name`

### `fiscal payees stats`

Show per-payee transaction statistics.

| Flag | Type | Description |
|---|---|---|
| `--since <date>` | `YYYY-MM-DD` | Include transactions on/after date |
| `--min-count <n>` | integer | Minimum number of transactions |
| `--extended` | boolean | Include `avg_amount` and `last_amount` |

### `fiscal payees create <name>`

Create a payee.

### `fiscal payees update <id>`

| Flag | Type | Required | Description |
|---|---|---|---|
| `--name <name>` | string | Yes | New name |

### `fiscal payees delete <id>`

Delete a payee.

### `fiscal payees merge <targetId> <mergeIds...>`

Merge one or more payees into the target payee. All transactions from merged payees are reassigned.

## budget

### `fiscal budget list-months`

List months that have budget data.

### `fiscal budget show <month>`

Show budget for a month.

| Argument | Format | Description |
|---|---|---|
| `month` | `YYYY-MM` | Target month |

### `fiscal budget status`

Show computed budget status fields (budgeted, spent, balance).

| Flag | Type | Default | Description |
|---|---|---|---|
| `--month <month>` | `YYYY-MM` | current | Target month |
| `--compare <n>` | integer | | Compare spent against previous N months |
| `--only <filter>` | `over` \| `under` \| `on` | | Filter by spending status |

### `fiscal budget set <month> <categoryId> <amount>`

Set the budgeted amount for a category in a month.

| Argument | Format | Description |
|---|---|---|
| `month` | `YYYY-MM` | Target month |
| `categoryId` | string | Category ID |
| `amount` | decimal | Budget amount (e.g. `500.00`) |

### `fiscal budget set-carryover <month> <categoryId> <true|false>`

Toggle carryover (rollover overspending) for a category in a month.

## rules

### `fiscal rules list`

List all rules.

Output columns: `id`, `stage`, `conditionsOp`, `conditions` (JSON), `actions` (JSON)

### `fiscal rules preview <ruleJson>`

Preview which existing transactions match a rule's conditions without creating it.

### `fiscal rules apply`

Apply rules retroactively to uncategorized transactions.

| Flag | Type | Description |
|---|---|---|
| `--rule <id>` | string | Apply only this rule (default: all) |
| `--dry-run` | boolean | Preview changes without applying |

### `fiscal rules create <ruleJson>`

Create a rule from JSON. See [rules.md](rules.md) for the JSON schema.

### `fiscal rules update <ruleJsonWithId>`

Update a rule. The entire rule object must be provided (not just changed fields). Must include `id`.

### `fiscal rules delete <id>`

Delete a rule.

## schedules

### `fiscal schedules list`

List all schedules.

### `fiscal schedules create <json>`

Create a schedule from JSON.

### `fiscal schedules update <id> <json>`

Update a schedule.

### `fiscal schedules delete <id>`

Delete a schedule.

## tags

### `fiscal tags list`

List all tags.

Output columns: `id`, `name`, `color`, `description`

### `fiscal tags create <name>`

| Flag | Type | Description |
|---|---|---|
| `--color <hex>` | string | Color (e.g. `#ff0000`) |
| `--description <text>` | string | Description |

### `fiscal tags update <id>`

| Flag | Type | Description |
|---|---|---|
| `--name <name>` | string | New name |
| `--color <hex>` | string | New color |
| `--description <text>` | string | New description |

### `fiscal tags delete <id>`

Delete a tag.

## query

### `fiscal query --module <path>`

Run an ActualQL query from an ESM/CJS module. The module exports a default function receiving `q` and returning a query:

```javascript
// food-transactions.mjs
export default (q) =>
  q('transactions')
    .filter({ 'category.name': 'Food' })
    .select(['date', 'amount', 'payee.name']);
```

```bash
fiscal query --module ./food-transactions.mjs
```

### `fiscal query --inline <expr>`

Run an inline ActualQL expression. Use exactly one of `--module` or `--inline`.
