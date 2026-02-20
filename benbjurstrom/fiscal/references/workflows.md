# Workflows

End-to-end task recipes with exact fiscal commands.

## 1. New budget from scratch

Set up a complete budget for someone starting fresh.

```bash
# Create the budget
fiscal budgets create "Personal Budget"
fiscal budgets list
fiscal budgets use <budget-id>

# Create accounts with starting balances
fiscal accounts create "Checking" --type checking --balance 3500.00
fiscal accounts create "Savings" --type savings --balance 12000.00
fiscal accounts create "Credit Card" --type credit --balance -450.00

# Get the account list to confirm IDs
fiscal accounts list

# Create category groups
fiscal categories create-group "Fixed Expenses"
fiscal categories create-group "Variable Expenses"
fiscal categories create-group "Savings & Goals"
# Note: an Income group exists by default

# Create categories (use group IDs from categories list)
fiscal categories list

fiscal categories create "Rent" --group <fixed-group-id>
fiscal categories create "Utilities" --group <fixed-group-id>
fiscal categories create "Internet" --group <fixed-group-id>
fiscal categories create "Insurance" --group <fixed-group-id>
fiscal categories create "Subscriptions" --group <fixed-group-id>

fiscal categories create "Groceries" --group <variable-group-id>
fiscal categories create "Dining Out" --group <variable-group-id>
fiscal categories create "Transportation" --group <variable-group-id>
fiscal categories create "Entertainment" --group <variable-group-id>
fiscal categories create "Clothing" --group <variable-group-id>
fiscal categories create "Personal Care" --group <variable-group-id>
fiscal categories create "Misc" --group <variable-group-id>

fiscal categories create "Emergency Fund" --group <savings-group-id>
fiscal categories create "Vacation" --group <savings-group-id>

fiscal categories create "Salary" --group <income-group-id> --income

# Get all category IDs
fiscal categories list

# Set initial budget amounts for the current month
fiscal budget set 2026-02 <rent-cat> 1500.00
fiscal budget set 2026-02 <utilities-cat> 200.00
fiscal budget set 2026-02 <internet-cat> 60.00
fiscal budget set 2026-02 <insurance-cat> 150.00
fiscal budget set 2026-02 <subscriptions-cat> 50.00
fiscal budget set 2026-02 <groceries-cat> 600.00
fiscal budget set 2026-02 <dining-cat> 200.00
fiscal budget set 2026-02 <transport-cat> 150.00
fiscal budget set 2026-02 <entertainment-cat> 100.00
fiscal budget set 2026-02 <clothing-cat> 75.00
fiscal budget set 2026-02 <personal-cat> 50.00
fiscal budget set 2026-02 <misc-cat> 100.00
fiscal budget set 2026-02 <emergency-cat> 500.00
fiscal budget set 2026-02 <vacation-cat> 200.00

# Verify the budget
fiscal budget show 2026-02
```

## 2. Full monthly cycle

Complete monthly routine: import, categorize, review, adjust.

```bash
# Import from multiple accounts
fiscal transactions import <checking-id> ./checking-feb.ofx --report
fiscal transactions import <credit-card-id> ./visa-feb.ofx --report

# Check what needs categorizing
fiscal transactions uncategorized

# Get rule suggestions
fiscal transactions triage --limit 100

# Parse the triage output and batch categorize
# The triage output shows suggested categories — build a map from the suggestions
fiscal transactions categorize --map "txn1=cat1,txn2=cat2,txn3=cat3" --dry-run
fiscal transactions categorize --map "txn1=cat1,txn2=cat2,txn3=cat3"

# Check for any remaining uncategorized
fiscal transactions uncategorized

# Review budget status
fiscal budget status --month 2026-02 --compare 3

# Find overspent categories
fiscal budget status --month 2026-02 --only over

# Adjust: move money from underspent to overspent categories
fiscal budget set 2026-02 <overspent-cat> 750.00     # increase
fiscal budget set 2026-02 <underspent-cat> 350.00     # decrease to compensate

# Verify final state
fiscal budget show 2026-02
```

## 3. CSV import with custom mapping

Common scenario: bank exports CSV with non-standard columns.

Example bank CSV:
```
Transaction Date,Post Date,Description,Category,Type,Amount,Memo
01/15/2026,01/16/2026,WHOLE FOODS #10234,Groceries,Sale,-45.67,
01/16/2026,01/17/2026,PAYROLL DEPOSIT,,Direct Dep,2500.00,Monthly salary
```

```bash
# Preview first
fiscal transactions import <acct-id> ./bank-export.csv \
  --csv-date-col "Transaction Date" \
  --csv-payee-col "Description" \
  --csv-amount-col "Amount" \
  --csv-notes-col "Memo" \
  --date-format "MM/dd/yyyy" \
  --dry-run --show-rows

# If it looks correct, import
fiscal transactions import <acct-id> ./bank-export.csv \
  --csv-date-col "Transaction Date" \
  --csv-payee-col "Description" \
  --csv-amount-col "Amount" \
  --csv-notes-col "Memo" \
  --date-format "MM/dd/yyyy" \
  --report
```

For a CSV with separate debit/credit columns:
```
Date,Description,Debit,Credit
15/01/2026,WHOLE FOODS,45.67,
16/01/2026,PAYROLL,,2500.00
```

```bash
fiscal transactions import <acct-id> ./export.csv \
  --csv-date-col "Date" \
  --csv-payee-col "Description" \
  --csv-outflow-col "Debit" \
  --csv-inflow-col "Credit" \
  --date-format "dd/MM/yyyy" \
  --report
```

## 4. Payee cleanup with rules

Clean up messy bank payee names and set up auto-categorization.

```bash
# See payee statistics to identify messy names
fiscal payees stats --min-count 2 --extended

# List payees to find duplicates
fiscal payees list

# Create a clean payee if needed
fiscal payees create "Amazon"
fiscal payees list   # get the new payee ID

# Create a pre-stage rule to clean the payee on import
fiscal rules create '{
  "stage": "pre",
  "conditionsOp": "and",
  "conditions": [
    {"field": "imported_payee", "op": "contains", "value": "AMAZON"}
  ],
  "actions": [
    {"field": "payee", "op": "set", "value": "<amazon-payee-id>"}
  ]
}'

# Create a default-stage rule to auto-categorize
fiscal rules create '{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    {"field": "payee", "op": "is", "value": "<amazon-payee-id>"}
  ],
  "actions": [
    {"field": "category", "op": "set", "value": "<shopping-cat-id>"}
  ]
}'

# Apply rules retroactively
fiscal rules apply --dry-run
fiscal rules apply

# Merge duplicate payees
fiscal payees merge <amazon-payee-id> <amazon-com-payee-id> <amzn-payee-id>
```

## 5. Triage-to-categorize pipeline

Systematic approach to categorizing a large batch of uncategorized transactions.

```bash
# See the full scope
fiscal transactions uncategorized

# Get triage suggestions (rules engine recommends categories)
fiscal transactions triage --limit 50

# From the triage output, identify:
# - Transactions with good suggestions: build --map entries
# - Transactions needing new rules: note them for rule creation
# - Transactions needing manual review: handle individually

# Batch categorize the ones with clear categories
fiscal transactions categorize \
  --map "txn1=groceries-cat,txn2=groceries-cat,txn3=dining-cat,txn4=transport-cat" \
  --dry-run

# If the dry-run looks good, apply
fiscal transactions categorize \
  --map "txn1=groceries-cat,txn2=groceries-cat,txn3=dining-cat,txn4=transport-cat"

# For recurring payees, create rules so they auto-categorize next time
fiscal rules create '{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    {"field": "payee", "op": "is", "value": "<kroger-payee-id>"}
  ],
  "actions": [
    {"field": "category", "op": "set", "value": "<groceries-cat-id>"}
  ]
}'

# Check what's left
fiscal transactions uncategorized
```

## 6. Credit card debt setup

Set up tracking for credit card debt being paid down.

```bash
# Create the debt category group and categories
fiscal categories create-group "Credit Card Debt"
fiscal categories list  # get group ID

fiscal categories create "Visa Debt" --group <debt-group-id>
fiscal categories list  # get category ID

# Enable rollover so the negative balance persists across months
fiscal budget set-carryover 2026-02 <visa-debt-cat-id> true

# Create the credit card account with current balance owed
fiscal accounts create "Visa" --type credit --balance -2500.00

# The starting balance transaction should be categorized to the debt category
# (this may need to be done via transaction update after account creation)
fiscal transactions list <visa-acct-id> --start 2025-01-01 --end 2026-12-31
fiscal transactions update <starting-balance-txn-id> --category <visa-debt-cat-id>

# Budget the minimum payment plus extra
fiscal budget set 2026-02 <visa-debt-cat-id> 250.00  # $50 min + $200 extra

# When statement arrives, enter interest charge
fiscal transactions add <visa-acct-id> --date 2026-02-10 --amount -32.75 \
  --payee "Visa" --category <visa-debt-cat-id> --notes "Interest charge"

# Make the payment (transfer from checking)
fiscal transactions add <visa-acct-id> --date 2026-02-15 --amount 250.00 \
  --payee "Transfer" --notes "Monthly payment"
fiscal transactions add <checking-acct-id> --date 2026-02-15 --amount -250.00 \
  --payee "Transfer" --notes "Visa payment"

# Check progress
fiscal accounts balance <visa-acct-id>
```

## 7. Server sync setup

Connect to an Actual Budget server for web UI access.

```bash
# Option A: Pull an existing budget from a server
fiscal --server-url http://actual.local:5006 --password secret budgets pull <sync-id>
fiscal budgets list
fiscal budgets use <downloaded-budget-id>

# Option B: Push a local budget to a server
fiscal --server-url http://actual.local:5006 --password secret budgets push

# Verify sync works
fiscal sync

# From now on, write operations auto-sync when server is configured
# You can also set server credentials in config to avoid passing them every time
```

To persist server credentials, add to `~/.config/fiscal/config.json`:

```json
{
  "dataDir": "/path/to/data",
  "activeBudgetId": "your-budget-id",
  "serverURL": "http://actual.local:5006",
  "password": "your-password"
}
```

## 8. Advanced queries

Use the query command for custom analytics.

```bash
# Inline query: total spending by category this month
fiscal query --inline "q('transactions').filter({date:{$gte:'2026-02-01'}}).select(['category.name','amount']).groupBy('category.name')"

# Module query: save reusable queries as files
```

Example query module — top payees by spending:

```javascript
// top-payees.mjs
export default (q) =>
  q('transactions')
    .filter({
      date: { $gte: '2026-01-01', $lte: '2026-12-31' },
      amount: { $lt: 0 }
    })
    .select(['payee.name', { total: { $sum: '$amount' } }])
    .groupBy('payee.name')
    .orderBy({ total: 'asc' })
    .limit(20);
```

```bash
fiscal query --module ./top-payees.mjs
```
