# fiscal Output Format

fiscal outputs machine-readable plain text by default (`--format record`). Use `--format table` for human-readable padded columns.

## Record format (default)

### Status line

Every command emits a status line as its first output:

**Success:**
```
status	ok	entity=transactions	count=5
```

**Error:**
```
status	err	message=No budget selected. Use --budget <id> or run `fiscal budgets use <id>`.
```

The status line is tab-separated. Fields after `ok`/`err` are `key=value` pairs. Common status fields:

| Field | Description |
|---|---|
| `entity` | Entity type (e.g. `transactions`, `accounts`, `import`) |
| `count` | Number of data rows following |
| `action` | What was done (`create`, `update`, `delete`) |
| `id` | ID of created/updated/deleted entity |
| `message` | Error message (on `err` status) |

Import-specific status fields:

| Field | Description |
|---|---|
| `added` | Number of new transactions added |
| `updated` | Number of existing transactions updated |
| `preview` | Total transactions in preview |
| `errors` | Number of parse errors |

### Data rows

If the command returns rows, the line after the status is a tab-separated header, followed by data rows:

```
status	ok	entity=accounts	count=2
id	name	type	offbudget	closed	balance
a1b2c3	Checking	checking	0	0	523400
d4e5f6	Savings	savings	0	0	1200000
```

### Value encoding

| Type | Encoding | Example |
|---|---|---|
| String | As-is (with escaping) | `STARBUCKS` |
| Null | Empty string | `` |
| Boolean | `1` (true) or `0` (false) | `1` |
| Integer | Decimal digits | `42` |
| Amount | Integer minor units (cents) | `-4599` = -$45.99 |
| JSON | JSON string (for complex fields) | `[{"field":"payee",...}]` |

### Text escaping

Tabs, newlines, and backslashes in text field values are escaped:

| Character | Escaped as |
|---|---|
| Tab (`\t`) | `\t` |
| Newline (`\n`) | `\n` |
| Carriage return (`\r`) | `\r` |
| Backslash (`\`) | `\\` |

### Error block

When the status line includes `errors=N` where N > 0, an additional block follows the data rows (or directly after the status line):

```
error
message
Invalid amount format: ABCD
Date parse failed: 13/42/2026
```

The error block has its own header line (`error`) and column header (`message`), followed by one error per line.

## Table format

With `--format table`, output is human-readable padded columns:

```
id        name       type      offbudget  closed  balance
--------  ---------  --------  ---------  ------  -------
a1b2c3    Checking   checking  false      false   523400
d4e5f6    Savings    savings   false      false   1200000
```

Table format does not include a status line. Booleans render as `true`/`false`. Text fields are not escaped. This format is for human reading, not machine parsing.
