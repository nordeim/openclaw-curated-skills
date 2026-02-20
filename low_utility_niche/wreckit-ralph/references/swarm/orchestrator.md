# Swarm Orchestrator Pattern

## Architecture

```
Main agent → wreckit orchestrator (depth 1)
  ├─ PHASE 1: Planning
  │   └→ Architect worker (depth 2)
  ├─ PHASE 2: Building (sequential)
  │   ├→ Implementer worker 1 (depth 2)
  │   ├→ Implementer worker 2 (depth 2)
  │   └→ ... (one fresh worker per task)
  ├─ PHASE 3: Parallel Verification
  │   ├→ Slop scan worker (depth 2)
  │   ├→ Type check worker (depth 2)
  │   ├→ Test quality worker (depth 2)
  │   ├→ Mutation kill worker (depth 2)
  │   └→ Security review worker (depth 2)
  ├─ PHASE 4: Sequential Verification
  │   ├→ Cross-verify / Regression
  │   └→ LLM-as-judge (if needed)
  └─ PHASE 5: Decision
      └→ Proof bundle → Ship / Caution / Blocked
```

## Config Required

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 8,
        "maxConcurrent": 8
      }
    }
  }
}
```

## Spawning Workers

**Orchestrator** (depth 1):
```
sessions_spawn with:
  task: [full context: project path, mode, PRD, acceptance criteria]
  label: "wreckit-orchestrator"
```

**Planning** (depth 2, from orchestrator):
```
sessions_spawn with:
  task: "Architect role. Read PRD at [path]. Gap analysis. Produce IMPLEMENTATION_PLAN.md."
  label: "wreckit-architect"
```

**Build** (depth 2, sequential, one per task):
```
sessions_spawn with:
  task: "Implementer role. Task: [description]. Implement ONE task. Type check + slop scan. Commit."
  label: "wreckit-build-N"
```

**Verification** (depth 2, parallel):
```
sessions_spawn with:
  task: "[Gate name]: Check [project]. Report as structured handoff per swarm/handoff.md."
  label: "wreckit-[gate]"
  model: "anthropic/claude-sonnet-4-20250514"  # cheaper for analysis
```

## CRITICAL: Worker Completion

**DO NOT fabricate results.** Use the collect pattern in `swarm/collect.md`.
The orchestrator MUST wait for ALL workers to complete before writing the proof bundle.

## Cost Control

| Role | Model | Why |
|------|-------|-----|
| Orchestrator | Opus | Ship/caution/blocked decisions |
| Architect | Opus | Planning needs judgment |
| Implementer | Opus | Coding needs quality |
| Slop scan | Sonnet | Analysis, not generation |
| Type check | Haiku | Just runs a command |
| Test quality | Sonnet | Analysis |
| Mutation kill | Sonnet | Simple mutations + runs tests |
| Security | Sonnet | Pattern recognition |
| Cross-verify | Opus | Regenerate quality code |
| LLM-as-judge | Opus | Subjective judgment |

## Failure Handling

- **Fail-fast:** Hallucinated deps in slop → stop everything → Blocked
- **Complete parallel gates:** Type check fails but slop passes → report both
- **Loop back:** Mutation kill fails → return to Ralph loop with "strengthen tests" tasks
- **Hard cap:** 50 iterations total. Still failing → Blocked with all evidence
- **Cascade stop:** `/stop` or `/subagents kill all` halts swarm
