# Transaction Rules

Rules automatically process transactions during import or when applied retroactively. They can rename payees, set categories, update notes, and more.

## Rule JSON schema

```json
{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    { "field": "imported_payee", "op": "contains", "value": "AMAZON" }
  ],
  "actions": [
    { "field": "payee", "op": "set", "value": "<payee-id>" },
    { "field": "category", "op": "set", "value": "<category-id>" }
  ]
}
```

## Stages

Rules run in three stages, in order:

| Stage | Purpose | Typical use |
|---|---|---|
| `"pre"` | Runs first | Payee renaming (clean up raw imported names) |
| `null` (default) | Auto-ranked by specificity | Categorization, most rules |
| `"post"` | Runs last, always wins | Overrides, forced assignments |

Within each stage, rules are automatically ranked from least to most specific. An `is` condition always ranks higher than `contains`, so more specific rules override broader ones.

When a transaction is imported, it runs through all rules in stage order. Each rule runs at most once. If multiple rules set the same field, the last one wins.

## Condition fields

| Field | Description |
|---|---|
| `imported_payee` | Raw payee/description text from the import file. Always the original text, unaffected by rules |
| `payee` | Payee entity in Actual (after any previous rule renames it) |
| `account` | Account the transaction belongs to |
| `category` | Category assigned to the transaction |
| `date` | Transaction date |
| `notes` | Notes/memo field |
| `amount` | Signed amount in minor units (negative = expense) |
| `amount_inflow` | Amount filtered to positive values only |
| `amount_outflow` | Amount filtered to negative values only (as positive number) |

**Important:** Use `imported_payee` (not `payee`) for matching raw bank text. The `payee` field references an entity in Actual and changes as previous rules rename it. Multiple rules checking `imported_payee` won't interfere with each other.

## Condition operators

| Operator | Applies to | Description |
|---|---|---|
| `is` | strings, payee, account, category | Exact match |
| `isNot` | strings, payee, account, category | Not exact match |
| `contains` | strings | Substring match (case-insensitive) |
| `doesNotContain` | strings | No substring match |
| `matches` | strings | Regular expression match |
| `oneOf` | payee, account, category | Matches any in a list |
| `notOneOf` | payee, account, category | Matches none in a list |
| `gt` | amount, date | Greater than |
| `lt` | amount, date | Less than |
| `gte` | amount, date | Greater than or equal |
| `lte` | amount, date | Less than or equal |
| `isapprox` | date, amount | Approximately equal |

All string matching is case-insensitive.

## Action fields

| Field | Description |
|---|---|
| `category` | Set the transaction's category |
| `payee` | Set the transaction's payee |
| `notes` | Set the notes field |
| `cleared` | Set cleared status (value: `true` or `false`) |
| `account` | Set the account |
| `date` | Set the date |
| `amount` | Set the amount |

## Action operators

| Operator | Description |
|---|---|
| `set` | Replace the field value |
| `prepend-notes` | Prepend text to the notes field |
| `append-notes` | Append text to the notes field |
| `link-schedule` | Link the transaction to a schedule |
| `set-split-amount` | Set amount on a split transaction |

## Automatic rules

Actual automatically creates rules based on user behavior:

1. **Payee renaming** — When you rename a payee and the old name is no longer used, Actual creates a `pre` stage rule with an `imported_payee` `is` condition that sets the payee. This means future imports auto-clean the payee name.

2. **Categorization** — When you categorize a transaction, Actual determines the most common category for that payee and creates/updates a default stage rule. Over time, most categories auto-apply on import.

You can edit or delete these auto-created rules at any time.

## Workflow: creating rules via fiscal

### 1. Preview what a rule would match

```bash
fiscal rules preview '{
  "conditions": [
    {"field": "imported_payee", "op": "contains", "value": "UBER EATS"}
  ],
  "conditionsOp": "and",
  "actions": [
    {"field": "category", "op": "set", "value": "<dining-cat-id>"},
    {"field": "payee", "op": "set", "value": "<uber-eats-payee-id>"}
  ]
}'
```

This shows matching transactions without creating the rule.

### 2. Create the rule

```bash
fiscal rules create '{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    {"field": "imported_payee", "op": "contains", "value": "UBER EATS"}
  ],
  "actions": [
    {"field": "category", "op": "set", "value": "<dining-cat-id>"},
    {"field": "payee", "op": "set", "value": "<uber-eats-payee-id>"}
  ]
}'
```

### 3. Apply retroactively

```bash
# Preview what would change
fiscal rules apply --dry-run

# Apply all rules to uncategorized transactions
fiscal rules apply

# Apply just one rule
fiscal rules apply --rule <rule-id> --dry-run
fiscal rules apply --rule <rule-id>
```

### 4. Update a rule

You must provide the full rule object including `id`:

```bash
fiscal rules update '{
  "id": "<rule-id>",
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    {"field": "imported_payee", "op": "contains", "value": "UBER"}
  ],
  "actions": [
    {"field": "category", "op": "set", "value": "<dining-cat-id>"},
    {"field": "payee", "op": "set", "value": "<uber-eats-payee-id>"}
  ]
}'
```

## Common rule patterns

### Payee cleanup (pre stage)

Clean up ugly bank payee names:

```json
{
  "stage": "pre",
  "conditionsOp": "and",
  "conditions": [
    { "field": "imported_payee", "op": "contains", "value": "AMAZON" }
  ],
  "actions": [
    { "field": "payee", "op": "set", "value": "<amazon-payee-id>" }
  ]
}
```

### Auto-categorize by payee

```json
{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    { "field": "payee", "op": "is", "value": "<grocery-store-payee-id>" }
  ],
  "actions": [
    { "field": "category", "op": "set", "value": "<groceries-cat-id>" }
  ]
}
```

### Auto-clear for instant accounts (post stage)

Cash or Venmo accounts where transactions clear immediately:

```json
{
  "stage": "post",
  "conditionsOp": "and",
  "conditions": [
    { "field": "account", "op": "oneOf", "value": ["<cash-acct-id>", "<venmo-acct-id>"] }
  ],
  "actions": [
    { "field": "cleared", "op": "set", "value": true }
  ]
}
```

### Create transfers between accounts

Set the payee to the target account's transfer payee to create a transfer:

```json
{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    { "field": "account", "op": "is", "value": "<checking-acct-id>" },
    { "field": "imported_payee", "op": "contains", "value": "TRANSFER TO SAVINGS" }
  ],
  "actions": [
    { "field": "payee", "op": "set", "value": "<savings-transfer-payee-id>" }
  ]
}
```

If both accounts use bank sync, create matching rules for both to avoid duplicate transfers.
