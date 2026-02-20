# Budgeting Concepts

## Envelope budgeting

Fiscal implements envelope budgeting (also called zero-based budgeting). The core principles:

1. **Budget only money you have.** Your total account balance is what's available to budget. No forecasting or estimating future income.
2. **Categories are envelopes.** Each category holds a specific amount of money allocated for a purpose (rent, food, entertainment).
3. **Spend from envelopes.** When you make a purchase and categorize it, the money comes out of that category's balance.
4. **Every dollar has a job.** Budget until "To Budget" reaches zero. All your money should be assigned to categories.
5. **Adjust as life happens.** Move money between categories when you overspend in one area. Your budget is a living plan, not a rigid constraint.

## Creating a budget

When setting up a budget for the first time:

1. Your total account balance becomes available to budget
2. Assign amounts to each category based on what you expect to spend
3. Continue budgeting until "To Budget" is zero
4. Don't overthink initial amounts — you'll adjust as you learn your spending patterns

Using fiscal:

```bash
fiscal budgets create "My Budget"
fiscal budgets use <id>
fiscal accounts create "Checking" --type checking --balance 5000.00
fiscal categories list                    # see default categories
fiscal budget set 2026-02 <rent-cat> 1500.00
fiscal budget set 2026-02 <food-cat> 600.00
fiscal budget set 2026-02 <transport-cat> 200.00
# ... continue until To Budget = 0
```

## The monthly workflow

1. **Import transactions** — Bring in new bank transactions periodically
2. **Categorize** — Assign categories to uncategorized transactions
3. **Review budget** — Check for overspending, adjust as needed
4. **Handle overspending** — Move money from other categories to cover overages
5. **New month** — When a new month starts, create a fresh budget. Use last month's budget as a template

```bash
# 1. Import
fiscal transactions import <acct> ./export.ofx --report

# 2. Categorize
fiscal transactions triage --limit 50
fiscal transactions categorize --map "txn1=cat1,txn2=cat2"

# 3. Review
fiscal budget status --month 2026-02 --compare 3
fiscal budget status --month 2026-02 --only over

# 4. Adjust
fiscal budget set 2026-02 <food-cat> 700.00      # increase food
fiscal budget set 2026-02 <savings-cat> 400.00    # decrease savings to compensate

# 5. New month — set budgets based on last month's patterns
fiscal budget show 2026-02                        # reference last month
fiscal budget set 2026-03 <rent-cat> 1500.00
# ...
```

## Income handling

When you receive income:

- It becomes immediately available to budget (appears in "Available Funds" / "To Budget")
- If you don't budget it this month, it rolls over to next month
- Common strategy: "hold" current month's income for next month's budget, so you're always budgeting with last month's income

Using fiscal, income shows up as a positive-amount transaction categorized to an income category.

## Overspending

When you overspend in a category (balance goes negative):

- **Default behavior:** The negative balance is automatically deducted from next month's "To Budget" amount, and the category balance resets to zero
- This means overspending reduces your ability to budget next month
- To handle it: move money from another category to cover the overspent amount, or accept that next month will have less to budget

### Rollover overspending (carryover)

Sometimes you want to keep a negative balance across months (e.g., tracking reimbursable expenses). Enable per-category:

```bash
fiscal budget set-carryover 2026-02 <category-id> true
```

When rollover is enabled, the negative balance stays in the category instead of being deducted from "To Budget."

## Category management

### Category groups

Categories are organized into groups. Common structure:

- **Fixed Expenses** — Rent, utilities, insurance, subscriptions
- **Variable Expenses** — Food, dining, entertainment, clothing
- **Savings & Goals** — Emergency fund, vacation, investments
- **Income** — Salary, freelance, interest (only one income group)

```bash
# Create a group
fiscal categories create-group "Fixed Expenses"

# Create categories in the group
fiscal categories create "Rent" --group <group-id>
fiscal categories create "Utilities" --group <group-id>
fiscal categories create "Internet" --group <group-id>
```

### Merging categories

If you have duplicate or redundant categories, delete one and transfer its transactions:

```bash
# Move all "Foods" transactions to "Food", then delete "Foods"
fiscal categories delete <foods-id> --transfer-to <food-id>
```

### Income categories

Create income categories in the income group:

```bash
fiscal categories create "Salary" --group <income-group-id> --income
fiscal categories create "Freelance" --group <income-group-id> --income
```

## Returns and reimbursements

### Returns

A return is not income — it goes back to the category you originally spent from. Enter the return as a positive-amount transaction with the same category:

```bash
fiscal transactions add <acct-id> --date 2026-02-10 --amount 32.99 \
  --payee "Amazon" --category <clothing-cat-id> --notes "Sandals return"
```

This restores $32.99 to the Clothing category balance.

### Reimbursements

For reimbursable expenses (business travel, shared costs):

1. Create a dedicated category (e.g., "Business Expenses")
2. **Option A: Pre-fund** — Budget money into the category before spending. True zero-budget approach.
3. **Option B: Carry negative** — Let the category go negative, enable rollover overspending, and refill when reimbursed.

```bash
# Create category and enable carryover
fiscal categories create "Business Expenses" --group <group-id>
fiscal budget set-carryover 2026-02 <biz-exp-cat-id> true

# Spend (category goes negative if not pre-funded)
fiscal transactions add <acct-id> --date 2026-02-05 --amount -150.00 \
  --payee "Hotel" --category <biz-exp-cat-id> --notes "Client trip"

# Receive reimbursement (positive amount, same category)
fiscal transactions add <acct-id> --date 2026-02-20 --amount 150.00 \
  --payee "Employer" --category <biz-exp-cat-id> --notes "Trip reimbursement"
```

## Joint accounts

### Shared budget (recommended for committed couples)

Both partners use the same budget file. Sync via an Actual Budget server so both can access it.

Setup:
1. Create a joint checking account
2. Use the shared budget on a synced server
3. Create a "Partner Personal Spending" category (with rollover) for tracking personal purchases made on the shared account
4. Track income contributions via a "Partners Contributions" income category

### Personal budget with shared account

Track your partner's contributions in your own budget:

1. Create the joint account on-budget
2. Your transfers to the joint account don't need a category (on-budget to on-budget transfer)
3. Your partner's deposits are categorized as income (use a "Partner Contribution" income category)
4. Budget the full bill amounts in shared expense categories

### Contribution strategy

For proportional contributions based on income:
- If Partner A earns $4,000/month and Partner B earns $6,000/month
- Total = $10,000. Partner A contributes 40%, Partner B contributes 60%
- If shared expenses are $3,000/month: A pays $1,200, B pays $1,800
