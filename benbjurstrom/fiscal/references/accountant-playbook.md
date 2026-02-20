# Accountant Playbook

Decision heuristics, category templates, common scenarios, and proactive monitoring patterns for acting as the user's personal accountant.

## Category Templates

Use these as starting points. Adapt based on what the user tells you about their life. Don't create categories they won't use — you can always add more later.

### Single person, renting

```
Housing:          Rent, Utilities, Internet, Renter's Insurance
Food:             Groceries, Dining Out, Coffee
Transportation:   Gas/Transit, Car Insurance, Car Maintenance, Parking
Personal:         Clothing, Personal Care, Health/Medical, Subscriptions
Lifestyle:        Entertainment, Hobbies, Gifts
Financial:        Savings, Emergency Fund, Investments
Income:           Salary, Side Income
```

### Single person, homeowner

Add to the above:
```
Housing:          Mortgage, Property Tax, HOA, Home Insurance, Home Maintenance
```
Remove: Rent, Renter's Insurance

### Couple, shared budget

```
Housing:          Rent/Mortgage, Utilities, Internet, Insurance
Shared Living:    Groceries, Household Supplies, Dining Out
Transportation:   Gas/Transit, Car Insurance, Maintenance
Kids (if any):    Childcare, School, Activities, Kids Clothing
Personal - [Name A]: Clothing, Personal Care, Hobbies, Fun Money
Personal - [Name B]: Clothing, Personal Care, Hobbies, Fun Money
Financial:        Emergency Fund, Savings Goals, Investments
Debt (if any):    [Card Name] Debt
Income:           [Name A] Income, [Name B] Income, Partner Contributions
```

### Freelancer / variable income

Add:
```
Business:         Equipment, Software, Professional Services, Business Travel
Taxes:            Estimated Taxes, Tax Prep
```

Key difference: Budget conservatively using the lowest expected monthly income. In good months, put extra toward savings or taxes.

## Budget Amount Heuristics

When the user doesn't know how much to budget, use these guidelines. These are starting points — adjust based on actual spending after 1-2 months of data.

### Percentage-of-income guidelines (50/30/20 rule)

- **50% Needs:** Housing, utilities, groceries, insurance, transportation, minimum debt payments
- **30% Wants:** Dining out, entertainment, subscriptions, hobbies, clothing
- **20% Savings & Debt:** Emergency fund, investments, extra debt payments

### Common amounts (adjust for local cost of living)

These are rough US averages for a single person. Scale up for families.

| Category | Budget Range | Notes |
|---|---|---|
| Groceries | $300–600/mo | $75–150/week for one person |
| Dining Out | $100–300/mo | Highly variable by lifestyle |
| Utilities | $100–250/mo | Electric, gas, water, trash |
| Internet | $50–100/mo | |
| Transportation | $150–500/mo | Gas + insurance, or transit pass |
| Subscriptions | $30–100/mo | Streaming, apps, gym |
| Personal Care | $30–75/mo | Haircuts, toiletries |
| Clothing | $50–150/mo | Can be $0 some months |
| Entertainment | $50–200/mo | |
| Emergency Fund | 3–6 months of expenses | Build over time |

### First-time budget strategy

1. Ask the user for their take-home income
2. Start with fixed/known expenses (rent, car payment, insurance)
3. Subtract from income to see what's left for variable categories
4. Budget variable categories conservatively
5. Put remaining amount toward savings
6. Tell the user: "This is a starting point. After a month of tracking, we'll see your actual spending and adjust."

## Common User Scenarios

### "I just got paid"

1. Check if income transaction was imported or needs to be added manually
2. The money is now available to budget
3. If following a "month ahead" strategy, this income funds next month's budget
4. If not month-ahead yet, allocate to current month's underfunded categories
5. Show the user their updated "To Budget" amount

### "How am I doing this month?"

```bash
fiscal budget status --month <current-month> --compare 3
fiscal budget status --month <current-month> --only over
fiscal transactions uncategorized
```

Present a summary like:
> **February Budget Check-in**
> - You've spent $2,340 of your $3,200 budget (73%) with 2 weeks left
> - **Watch out:** Dining Out is at $185 of $200 (92%)
> - **On track:** Groceries at $290 of $500 (58%)
> - **Under budget:** Transportation at $45 of $150 (30%)
> - 3 uncategorized transactions need attention
> - Compared to the last 3 months, your dining spending is up 15%

### "I overspent on [category]"

1. Check how much they're over by
2. Look for categories with surplus that could cover it
3. Suggest a transfer: "You're $45 over on Dining. Your Entertainment category has $80 left. Want me to move $45 from Entertainment to cover it?"
4. If no surplus anywhere, explain that this overspending will reduce next month's available budget
5. After handling it, consider whether the budget needs long-term adjustment

```bash
fiscal budget status --month <month> --only over
fiscal budget show <month>
# Identify surplus categories, then adjust:
fiscal budget set <month> <surplus-cat> <reduced-amount>
fiscal budget set <month> <overspent-cat> <increased-amount>
```

### "I want to save for [goal]"

1. Create a savings category for the goal
2. Ask: How much do they need? By when?
3. Calculate monthly contribution needed
4. Add it to the budget
5. Track progress each month

```bash
fiscal categories create "Vacation Fund" --group <savings-group-id>
fiscal budget set 2026-02 <vacation-cat-id> 300.00
```

Report progress: "You've saved $900 of your $3,000 vacation goal (30%). At $300/month, you'll reach it by November."

### "I have a new credit card" / "I'm carrying credit card debt"

See [references/credit-cards.md](credit-cards.md) for the full strategy.

Quick steps:
1. Create the card as an on-budget account with negative balance
2. If paying in full monthly: no special setup needed, just categorize purchases normally
3. If carrying debt: create a debt category with rollover overspending, budget minimum payments + extra

### "Import my bank transactions"

1. Ask what format the file is (or check the extension)
2. Always preview first with `--dry-run`
3. Import, then report results
4. Categorize new transactions
5. Create rules for recurring payees

If CSV and the first attempt fails or looks wrong:
- Ask the user what the columns mean
- Use `--csv-date-col`, `--csv-amount-col`, `--csv-payee-col` to map them
- See [references/import-guide.md](import-guide.md) for all CSV options

### "I returned something" / "I'm getting reimbursed"

- **Return:** Add as a positive-amount transaction in the same category as the original purchase. This restores the category balance.
- **Reimbursement:** Create a dedicated category (e.g., "Business Expenses") if not exists. Enable rollover with `set-carryover true`. The category goes negative when you spend, returns to zero when reimbursed.

### "I share expenses with my partner"

Ask: Do they want a shared budget or to track the partner's contributions in their personal budget?

- **Shared budget:** Both use the same budget file via server sync. Create a "Partner Personal Spending" rollover category for accidental personal purchases.
- **Personal budget with shared account:** Create the joint account on-budget. Track partner deposits as income using a "Partner Contribution" category.

See [references/budgeting.md](budgeting.md) for full joint account strategies.

## Proactive Monitoring

When you have access to the budget, check for and flag these issues without being asked:

### Immediate alerts

- **Overspent categories**: Any category with negative balance needs attention now
- **Large uncategorized transactions**: Anything over $100 uncategorized should be flagged
- **Negative "To Budget"**: The user has over-budgeted — they've assigned more money than they have

### Monthly check

- **Categories consistently over/under budget**: After 2-3 months of data, suggest permanent adjustments. "You've gone over your Groceries budget 3 months in a row. Want me to increase it to $550?"
- **Unused categories**: Categories with $0 spent for 2+ months might not be needed
- **Missing rules**: Payees that appear 3+ times without a rule should get one
- **Payee cleanup**: Merge duplicate payees (e.g., "AMAZON.COM" and "AMZN MKTP US")

### Quarterly review

- **Spending trends**: Compare category totals across months. Flag significant increases.
- **Savings progress**: Report on savings goals and whether the user is on track
- **Debt paydown progress**: If carrying credit card debt, report remaining balance and projected payoff date

## Rule-Building Strategy

Rules make categorization automatic over time. Build them systematically:

### When to create a rule

- A payee has appeared 2+ times with the same category assignment
- A payee name is messy (bank-style text like "WHOLEFDS MKT 10234")
- The user explicitly says "always categorize X as Y"

### Two-rule pattern for clean automation

For each recurring payee, create two rules:

1. **Pre-stage: Clean the payee name**
   - Condition: `imported_payee` contains key text (e.g., "WHOLEFDS")
   - Action: Set `payee` to clean name (e.g., "Whole Foods")

2. **Default-stage: Set the category**
   - Condition: `payee` is the clean payee
   - Action: Set `category` to the right category (e.g., "Groceries")

This separation means payee cleanup and categorization are independent — you can change the category later without touching the payee rule.

### After creating rules

Always apply retroactively to clean up existing uncategorized transactions:

```bash
fiscal rules apply --dry-run    # preview first
fiscal rules apply              # apply
```

## Handling Mistakes

### User categorized something wrong

Just update the transaction. No need to make it complicated:

```bash
fiscal transactions update <txn-id> --category <correct-cat-id>
```

If the wrong category was set by a rule, update the rule too.

### Duplicate transactions

This usually means the same file was imported twice, or the user entered a transaction manually and then imported it. Fiscal's reconciliation handles most of this automatically, but if duplicates slip through:

```bash
fiscal transactions delete <duplicate-txn-id>
```

### Budget amounts need correction

Just set the new amount — it replaces the old one:

```bash
fiscal budget set <month> <cat-id> <corrected-amount>
```
