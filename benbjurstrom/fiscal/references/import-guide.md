# Importing Transactions

fiscal imports bank transaction files into an account. The import pipeline parses the file, normalizes data, optionally runs rules and deduplication, and commits to the budget.

## Supported formats

| Extension | Format | Description |
|---|---|---|
| `.csv`, `.tsv` | CSV/TSV | Comma or tab-separated values |
| `.qif` | QIF | Quicken Interchange Format |
| `.ofx`, `.qfx` | OFX | Open Financial Exchange (also Quicken Financial Exchange) |
| `.xml` | CAMT | ISO 20022 CAMT XML |

Format is auto-detected by file extension.

## Basic usage

```bash
# Import with rule processing and deduplication (default)
fiscal transactions import <accountId> ./export.ofx

# Preview without committing
fiscal transactions import <accountId> ./export.ofx --dry-run

# See individual imported rows
fiscal transactions import <accountId> ./export.ofx --show-rows

# Get a compact summary
fiscal transactions import <accountId> ./export.ofx --report
```

## Import pipeline

1. **Parse** — Read file, extract transactions based on format
2. **Normalize** — Apply date format, amount multiplier, flip-amount
3. **Reconcile** (default) — Run through Actual's rule engine and deduplication
4. **Commit** — Add/update transactions in the budget

With `--no-reconcile`, steps 3 is skipped (raw add, no rules, no dedup).

## General flags

| Flag | Default | Description |
|---|---|---|
| `--no-reconcile` | off | Skip rule processing and deduplication |
| `--dry-run` | off | Preview without committing changes |
| `--show-rows` | off | Print each imported transaction row |
| `--report` | off | Print compact import summary row |
| `--no-clear` | off | Don't auto-set `cleared=true` on imported transactions |
| `--no-import-notes` | off | Skip the memo/notes field from the source file |
| `--date-format <fmt>` | auto | Override date parsing format (e.g. `MM/dd/yyyy`, `dd/MM/yyyy`) |
| `--multiplier <n>` | 1 | Multiply all parsed amounts by this factor |
| `--flip-amount` | off | Negate all amounts (useful when bank exports use opposite sign convention) |

## OFX/QFX-specific

| Flag | Default | Description |
|---|---|---|
| `--fallback-payee-to-memo` | off | Use the memo field as payee when payee is missing |

## CSV-specific flags

### File structure

| Flag | Default | Description |
|---|---|---|
| `--no-csv-header` | off | CSV has no header row (use column indices instead of names) |
| `--csv-delimiter <char>` | `,` | Field delimiter character |
| `--csv-skip-start <n>` | 0 | Skip N lines at the start of the file |
| `--csv-skip-end <n>` | 0 | Skip N lines at the end of the file |

### Column mapping

Map CSV columns to transaction fields by name or zero-based index:

| Flag | Description |
|---|---|
| `--csv-date-col <name\|index>` | Date column |
| `--csv-amount-col <name\|index>` | Signed amount column |
| `--csv-payee-col <name\|index>` | Payee/description column |
| `--csv-notes-col <name\|index>` | Notes/memo column |
| `--csv-category-col <name\|index>` | Category column |

### Amount modes

There are three ways CSV files represent amounts:

**Mode 1: Single signed amount column** (default)

One column has positive values for income and negative for expenses (or vice versa):

```bash
fiscal transactions import <acct> export.csv --csv-amount-col "Amount"
```

**Mode 2: Separate inflow/outflow columns**

Two columns, one for money in and one for money out:

```bash
fiscal transactions import <acct> export.csv \
  --csv-inflow-col "Credit" \
  --csv-outflow-col "Debit"
```

**Mode 3: In/out marker column**

An amount column plus a separate column that indicates direction:

```bash
fiscal transactions import <acct> export.csv \
  --csv-amount-col "Amount" \
  --csv-inout-col "Type" \
  --csv-out-value "DR"
```

### Adjusting amounts

| Flag | Description |
|---|---|
| `--flip-amount` | Negate all amounts. Use when your bank uses the opposite sign convention |
| `--multiplier <n>` | Multiply all amounts. Use `--multiplier 100` if amounts are already in dollars (no cents), or `--multiplier -1` as an alternative to `--flip-amount` |

## Examples

### Standard OFX import

```bash
fiscal transactions import abc123 ./checking-jan.ofx --report
# status	ok	entity=import	added=42	updated=0	preview=42	errors=0
```

### CSV with custom columns

Bank exports: `Date,Description,Debit,Credit,Balance`

```bash
fiscal transactions import abc123 ./statement.csv \
  --csv-date-col "Date" \
  --csv-payee-col "Description" \
  --csv-inflow-col "Credit" \
  --csv-outflow-col "Debit" \
  --date-format "dd/MM/yyyy"
```

### CSV with no header and tab delimiter

```bash
fiscal transactions import abc123 ./export.tsv \
  --no-csv-header \
  --csv-delimiter "\t" \
  --csv-date-col 0 \
  --csv-amount-col 1 \
  --csv-payee-col 2
```

### CSV with extra header/footer lines

Some bank exports include summary lines before/after the data:

```bash
fiscal transactions import abc123 ./export.csv \
  --csv-skip-start 3 \
  --csv-skip-end 1 \
  --csv-date-col "Date" \
  --csv-amount-col "Amount" \
  --csv-payee-col "Payee"
```

### Dry-run to preview

Always preview first with unfamiliar files:

```bash
fiscal transactions import abc123 ./unknown.csv --dry-run --show-rows
```

This shows what would be imported without making changes. Check the output for correct dates, amounts, and payees before committing.

### QIF import with amount flip

```bash
fiscal transactions import abc123 ./download.qif --flip-amount --report
```

## Import output

### With `--report`

```
status	ok	entity=import	added=14	updated=3	preview=17	errors=0
```

### With `--show-rows`

After the status line, a TSV block with the imported transactions:

```
status	ok	entity=import	added=14	updated=3	preview=17	errors=0
date	amount	imported_payee	notes
2026-01-05	-4599	STARBUCKS #1234	coffee
2026-01-06	-12300	WHOLE FOODS MKT	groceries
```

### With `--dry-run`

Same output format but no changes are committed. The `added` and `updated` counts show what *would* happen.
