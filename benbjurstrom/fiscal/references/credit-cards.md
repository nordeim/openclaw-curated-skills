# Credit Cards

## How credit cards work in Actual Budget

Credit card accounts are on-budget accounts with a negative balance. Actual treats them like any other account — the negative balance is subtracted from your positive deposit account balances to give your total on-budget funds.

When you make a credit card purchase and categorize it, the money comes from that budget category (just like a debit card purchase). The only difference is the timing of when the actual cash leaves your checking account (when you pay the credit card bill).

**Key insight:** If every credit card purchase is categorized to a funded budget category, you will always have enough money to pay the bill. The budget already accounted for the spending.

## Strategy: Paying in Full (Within the Budget)

Use this when you pay off your credit card statement every month.

### Rules

- Never over-budget. Only budget funds you actually have
- Check your category balance before spending
- Enter purchase transactions promptly
- Cover all overspending by moving money between categories
- Reconcile accounts at least monthly
- Pay at least your statement balance before the due date

### Setup

1. Create the credit card as an on-budget account with a negative starting balance:

```bash
fiscal accounts create "Chase Visa" --type credit --balance -35.00
```

2. No special budget category needed — each purchase uses your regular expense categories

### Monthly workflow

1. Throughout the month, categorize every credit card purchase to a funded category
2. When the statement arrives, note the New Balance
3. Reconcile the account
4. Pay the statement balance by creating a transfer from checking:

```bash
fiscal transactions add <chase-acct-id> --date 2026-02-15 --amount 213.15 \
  --payee "Transfer from Checking" --notes "Statement payment"
fiscal transactions add <checking-acct-id> --date 2026-02-15 --amount -213.15 \
  --payee "Transfer to Chase Visa" --notes "Statement payment"
```

(Alternatively, create the transfer as a single transaction if using the transfer payee mechanism.)

## Strategy: Carrying Debt

Use this when you have a credit card balance you cannot pay in full. The goal is to pay it off safely without incurring more debt.

### Setup

1. Create a "Credit Card Debt" category group:

```bash
fiscal categories create-group "Credit Card Debt"
```

2. Create a debt category for each card carrying debt:

```bash
fiscal categories create "Citi Card Debt" --group <debt-group-id>
fiscal categories create "DEMO Card Debt" --group <debt-group-id>
```

3. Enable rollover overspending on each debt category:

```bash
fiscal budget set-carryover 2026-02 <citi-debt-cat-id> true
fiscal budget set-carryover 2026-02 <demo-debt-cat-id> true
```

4. Create the credit card account with the total amount owed as the starting balance, categorized to the debt category:

```bash
fiscal accounts create "Citibank" --type credit --balance -2590.00
```

The starting balance transaction should be categorized to the debt category.

### Why rollover is needed

Negative credit card account balances are already subtracted from your available on-budget funds. Without rollover, the negative debt category balance would also be deducted from "To Budget" — double-counting the debt. Rollover prevents this.

### Monthly workflow (card with debt, no new purchases)

1. At the start of the month, budget the expected minimum payment to the debt category:

```bash
fiscal budget set 2026-02 <citi-debt-cat-id> 90.00
```

2. If you have extra money after funding all expenses, add it to the debt category to pay down faster:

```bash
fiscal budget set 2026-02 <citi-debt-cat-id> 290.00  # 90 minimum + 200 extra
```

3. When the statement arrives, enter interest and fees as a transaction categorized to the debt category:

```bash
fiscal transactions add <citi-acct-id> --date 2026-02-10 --amount -64.00 \
  --payee "Citibank" --category <citi-debt-cat-id> --notes "Interest charge"
```

4. Make the payment (transfer from checking):

```bash
fiscal transactions add <citi-acct-id> --date 2026-02-15 --amount 290.00 \
  --payee "Transfer from Checking" --notes "Monthly payment"
fiscal transactions add <checking-acct-id> --date 2026-02-15 --amount -290.00 \
  --payee "Transfer to Citibank" --notes "CC payment"
```

### Monthly workflow (card with debt AND new purchases)

If you must use a card that has existing debt:

1. Categorize new purchases to regular funded budget categories (staying Within the Budget)
2. When the statement arrives, enter interest/fees to the debt category
3. Reconcile the account
4. Calculate payment:
   - **Payment = New Purchases - Return Credits + Uncleared Total + Budgeted Column**
   - Or equivalently: **Account Balance - Debt Category Balance** (using absolute values)
5. The minimum payment must be at least the statement minimum

### Paying off the highest interest first

When carrying debt on multiple cards:
- Budget minimum payments for all cards
- After funding all necessary expenses, add extra to the highest-interest card
- Once the highest-interest card is paid off, redirect that extra payment to the next highest
- Use only one card for new purchases and pay it in full monthly

### Important notes

- All credit card accounts should be **on-budget** (not off-budget)
- You cannot change an off-budget account to on-budget — set it correctly from the start
- Only set a credit card as off-budget if there will be no new purchases and the account will be closed once paid off
- A credit limit is not an invitation to spend it
- If you lose your grace period due to late payment, you'll incur interest from purchase date on all new purchases until you pay in full for several consecutive months
