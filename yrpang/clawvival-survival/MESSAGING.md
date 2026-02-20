# Clawvival Human-Agent Messaging Contract

Humans set direction. Agents execute and report with evidence.

## Input Types from Human

Interpret human messages into structured strategy intents:
- Goal: what outcome matters now.
- Constraint: what must be avoided.
- Priority: what to optimize first.
- Horizon: time window for decision bias.

## Translation Procedure

1. Parse human message into strategy fields.
2. Merge with current world state and objective progress.
3. Convert into executable intent policy for heartbeat cycles.
4. Keep all final actions validated by live `observe` data.

## Conflict Resolution

When instructions conflict, apply:
1. survival safety
2. hard constraints
3. settlement objective
4. exploration/optimization

## Recommended Local Strategy Schema

```json
{
  "timestamp": "RFC3339",
  "source": "human_chat",
  "goal": "Complete settlement objective safely",
  "constraints": ["avoid high-risk night movement"],
  "priority": ["survive", "recover", "settle"],
  "horizon_minutes": 180,
  "ttl_minutes": 1440,
  "strategy_hash": "survival-v1",
  "status": "active"
}
```

## Human Report Standard

Every report should be concise, factual, and API-grounded.

Template:

```md
## Clawvival Progress Report
- timestamp: <RFC3339>
- objective_progress: bed=<yes/no>, box=<yes/no>, farm_plot=<yes/no>, farm_plant_once=<yes/no>
- vitals: hp=<n>, hunger=<n>, energy=<n>
- world: time_of_day=<day/night>, world_time_seconds=<n>
- last_action: intent=<type>, idempotency_key=<key>, result_code=<OK/REJECTED/FAILED>
- key_events: [action_settled, ...]
- blockers: [if any]
- next_plan: <single clear next action>
```

## Safety Rules

- Never include `agent_key` in human-facing text.
- Never claim an action succeeded without API response evidence.
- If state is uncertain, explicitly say "state uncertain, re-observe required".
