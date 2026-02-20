# Worker Completion Protocol (Collect Pattern)

## The Problem

The orchestrator spawns parallel workers via `sessions_spawn`. Worker results arrive
asynchronously via announce messages. If the orchestrator doesn't wait, it will
**fabricate results** — this happened on the first midas-mcp audit (Feb 16, 2026).

## The Rule

**NEVER write the proof bundle until ALL spawned workers have reported back.**
**NEVER make up results for workers that haven't responded.**
**NEVER assume a worker succeeded or failed without its actual announce message.**

## Collect Protocol

### Step 1: Track spawned workers

Before spawning, create a checklist:
```
WORKERS_EXPECTED:
- wreckit-slop: PENDING
- wreckit-typecheck: PENDING
- wreckit-testquality: PENDING
- wreckit-mutation: PENDING
- wreckit-security: PENDING
```

### Step 2: Spawn all parallel workers

Spawn all at once. Each worker's task must end with:
```
"When complete, your results will announce back automatically. Include your label
and PASS/FAIL/WARN status in the first line of your response."
```

### Step 3: Wait for announces

After spawning, the orchestrator should **stop and wait**. Worker completions
arrive as announce messages in the orchestrator's session.

As each announce arrives, update the checklist:
```
WORKERS_EXPECTED:
- wreckit-slop: PASS ✅ (received)
- wreckit-typecheck: PASS ✅ (received)
- wreckit-testquality: PENDING ⏳
- wreckit-mutation: PENDING ⏳
- wreckit-security: PASS ✅ (received)
```

### Step 4: Check completion

After each announce, check: are ALL workers complete?
- **YES** → proceed to proof bundle
- **NO** → continue waiting

### Step 5: Timeout

If a worker hasn't reported after 5 minutes:
1. Check `subagents list` to see if it's still running
2. If still running → wait longer (up to 10 min)
3. If crashed/gone → mark as ERROR, note in proof bundle
4. **NEVER fill in fake results**

## What WRONG Looks Like

```
❌ Orchestrator spawns 5 workers
❌ Only 1 completes
❌ Orchestrator writes proof bundle with results for all 5
❌ 4 results are fabricated
```

## What RIGHT Looks Like

```
✅ Orchestrator spawns 5 workers
✅ Waits for all 5 announces
✅ 4 complete, 1 times out
✅ Proof bundle shows 4 real results + 1 ERROR (timed out)
✅ Decision based only on real data
```
