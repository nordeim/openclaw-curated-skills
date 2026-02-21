---
name: water-coach
description: "Hydration tracking and coaching skill. Use when user wants to track water intake, get reminders to drink water, log body metrics, or get analytics on hydration habits."
compatibility: "Requires python3, openclaw cron feature, heartbeat feature"
metadata: {"clawdbot":{"emoji":"💧"} 
  author: oristides
  version: "1.5.1"
---

# 💧 Water Coach v1.5.1



## First-time Setup  [references/setup.md](references/setup.md)



## CLI Structure

```bash
water_coach.py <namespace> <command> [options]
```

Namespaces: `water` | `body` | `analytics`

---

## Data Format 

### CSV Format
```
logged_at,drank_at,date,slot,ml_drank,goal_at_time,message_id
```

| Column | Description |
|--------|-------------|
| logged_at | When user told you (NOW) |
| drank_at | When user actually drank (user can specify past time) |
| date | Derived from drank_at |
| slot | morning/lunch/afternoon/evening/manual |
| ml_drank | Amount in ml |
| goal_at_time | Goal at that moment |
| message_id | Audit trail - link to conversation |

**Key Rules:**
- **drank_at is MANDATORY** - always required
- If user doesn't specify drank_at → assume drank_at = logged_at
- **Cumulative is calculated at query time** (not stored)
- Use drank_at to determine which day counts

Details at  [references/log_format.md](references/log_format.md)

### Audit Trail

Every water log entry captures:
- **message_id**: Links to the conversation message where user requested the log
- **Auto-capture**: CLI automatically gets message_id from session transcript
- **Proof**: Use `water audit <message_id>` to get entry + conversation context

```bash
# Check proof of a water entry
water audit msg_123
# Returns: entry data + surrounding messages for context
```

> ⚠️ **Privacy Notice**: The audit trail feature can read your conversation transcripts to link water entries with messages. By default, this is **disabled** (`audit_auto_capture: false`). To enable it:
> 
> ```bash
> # Edit water_config.json and set:
> "audit_auto_capture": true
> ```
> 
> **Why would you want this?** If you need proof of water intake for medical/legal purposes, the audit provides conversation context showing exactly when you logged water.
> 
> **Why disable it?** If you discuss sensitive topics in your chats, you may prefer not to have that content read by the skill.

---

## Daily Commands

```bash
# Water
water status                                      # Current progress (calculated from drank_at)
water log 500                                    # Log intake (drank_at = now)
water log 500 --drank-at=2026-02-18T18:00:00Z  # Log with past time
water log 500 --drank-at=2026-02-18T18:00:00Z --message-id=msg_123
water dynamic                                    # Check if extra notification needed
water threshold                                  # Get expected % for current hour
water set_body_weight 80                        # Update weight + logs to body_metrics
water set_body_weight 80 --update-goal          # + update goal
water audit <message_id>                        # Get entry + conversation context

# Body
body log --weight=80 --height=1.75 --body-fat=18
body latest          # Get latest metrics
body history 30     # Get history

# Analytics
analytics week       # Weekly briefing (Sunday 8pm)
analytics month     # Monthly briefing (2nd day 8pm)
```

---

## Rules (MUST FOLLOW)

1. **ALWAYS use CLI** - never calculate manually
2. **LLM interprets first** - "eu tomei 2 copos" → 500ml → water log 500
3. **Threshold from CLI** - run `water threshold`, don't hardcode
4. **GOAL is USER'S CHOICE** - weight × 35 is just a DEFAULT suggestion:
   - At setup: Ask weight → suggest goal → **CONFIRM with user**
   - On weight update: Ask "Want to update your goal to the new suggested amount?"
   - User can set any goal (doctor's orders, preference, etc.)

---

## Config Tree

```
water-coach/
├── SKILL.md              ← You are here
├── scripts/
│   ├── water_coach.py   ← Unified CLI
│   └── water.py         ← Core functions
├── data/
│   ├── water_config.json (Current configs)
│   ├── water_log.csv
│   └── body_metrics.csv
└── references/
    ├── setup.md
    ├── dynamic.md
    └── log_format.md
```

---

## Notifications Schedule

| Type | When | Command |
|------|------|---------|
| Base (5x) | 9am, 12pm, 3pm, 6pm, 9pm | water status |
| Dynamic | Every ~30 min (heartbeat) | water dynamic |
| Weekly | Sunday 8pm | analytics week |
| Monthly | 2nd day 8pm | analytics month |

---

## Quick Reference

| Task | Command |
|------|---------|
| Check progress | `water_coach.py water status` |
| Log water | `water_coach.py water log 500` |
| Need extra? | `water_coach.py water dynamic` |
| Body metrics | `water_coach.py body log --weight=80` |
| Weekly report | `water_coach.py analytics week` |
| Monthly report | `water_coach.py analytics month` |

## Dynamic Scheduling details→ [references/dynamic.md](references/dynamic.md)



## Tests

```bash
python3 -m pytest skills/water-coach/scripts/test/test_water.py -v
```

## Example

```
User: "eu tomei 2 copos"
Agent: (LLM interprets: 2 copos ≈ 500ml)
Agent: exec("water_coach.py water log 500")
→ Python logs to CSV
```



Agent Evaluations → [evaluation/AGENT.md](evaluation/AGENT.md)

