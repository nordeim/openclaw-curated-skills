# Gate: Mutation Kill

**Question:** Do the tests actually catch bugs, or do they just run green?

## Process

Generate mutations — small, realistic code changes that SHOULD break something:

- Flip boolean conditions (`if (x > 0)` → `if (x < 0)`)
- Remove null checks
- Swap function arguments
- Change boundary values (`>=` → `>`)
- Remove error handling
- Return early before side effects

For each mutation:
1. Apply mutation to a copy (never mutate real code)
2. Run test suite against mutated copy
3. Tests still pass → **mutation survived** (tests are weak here)
4. Revert mutation, record result

## External Tools (optional, better)

- **Stryker** (JS/TS) — real mutation framework, much more thorough
- **mutmut** (Python)
- **cargo-mutants** (Rust)

If available, prefer external tools over AI-generated mutations.

## Pass/Fail

- **Pass:** ≥95% of mutations killed
- **Caution:** 90-95% kill rate
- **Fail:** <90% kill rate — tests are not trustworthy
