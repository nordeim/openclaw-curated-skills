# FootballBin Predictions - ClawHub Skill

AI-powered match predictions for Premier League and Champions League.

## What it does

Returns real-time predictions for upcoming football matches:
- Half-time and full-time scores
- Next goal scorer
- Corner count predictions
- Key player analysis with current season stats

## Quick start

```bash
# Get all current matchweek predictions
scripts/footballbin.sh predictions premier_league

# Get Champions League predictions
scripts/footballbin.sh predictions ucl

# Filter by team
scripts/footballbin.sh predictions epl --home arsenal
scripts/footballbin.sh predictions epl --away liverpool
```

## Requirements

- `curl` (HTTP requests)
- `jq` (optional, for formatted output)

No API key or authentication needed.

## Links

- [FootballBin iOS App](https://apps.apple.com/app/footballbin/id6757111871)
- [FootballBin Android App](https://play.google.com/store/apps/details?id=com.achan.footballbinandroid)
