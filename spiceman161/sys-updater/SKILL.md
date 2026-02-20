---
name: sys-updater
description: System package maintenance for Ubuntu (apt), npm, brew, and OpenClaw skills. Conservative workflow with 2-day quarantine for non-security updates, automatic security updates, and scheduled reviews with web search for bug assessment.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔄",
        "os": ["linux"],
        "requires": { "bins": ["apt-get", "npm", "brew", "clawhub"] },
      },
  }
---

# System Updater (sys-updater)

Comprehensive system maintenance automation for Ubuntu hosts with support for apt, npm, brew, and OpenClaw skills.

## Features

- **APT (Ubuntu)**: Daily update check, automatic security updates, 2-day quarantine for non-security packages
- **NPM**: Global package tracking with web search review for bugs before upgrade
- **Brew**: Package tracking with same conservative workflow as npm
- **OpenClaw Skills**: Immediate auto-update without quarantine
- **Scheduled Reports**: Daily Telegram reports at 09:00 MSK
- **Bug Review**: Automatic web search for package issues before applying updates

## Workflow

### Daily (06:00 MSK)
```
run_6am:
├── apt: update, security upgrades, simulate, track non-security
├── npm/brew: check outdated, add to tracking
└── skills: auto-update immediately (no quarantine)
```

### Report (09:00 MSK)
- Summary of all package managers
- Planned updates for next day
- Blocked packages with reasons

### T+2 Days (Review)
- Web search for bugs/regressions in tracked packages
- Mark as planned or blocked based on findings

### T+3 Days (Upgrade)
- Apply planned npm/brew upgrades
- Send completion report

## State Files

- `state/apt/last_run.json` — Last run results
- `state/apt/tracked.json` — APT packages being tracked
- `state/apt/npm_tracked.json` — NPM packages
- `state/apt/brew_tracked.json` — Brew packages
- `state/logs/apt_maint.log` — Daily logs (10-day rotation)

## Manual Commands

```bash
# Daily maintenance (runs automatically)
./scripts/apt_maint.py run_6am

# Generate report
./scripts/apt_maint.py report_9am

# Check npm/brew only
./scripts/pkg_maint.py check

# Review packages (after 2 days)
./scripts/pkg_maint.py review

# Apply planned upgrades
./scripts/pkg_maint.py upgrade

# Update skills only
./scripts/pkg_maint.py skills
```

## Configuration

Environment variables:
- `SYS_UPDATER_BASE_DIR` — Base directory (default: ~/clawd/sys-updater)
- `SYS_UPDATER_STATE_DIR` — State files location
- `SYS_UPDATER_LOG_DIR` — Log files location

## Cron Jobs

Requires 4 cron jobs:
1. `run_6am` — Daily 06:00 MSK (apt + check npm/brew + auto skills)
2. `report_9am` — Daily 09:00 MSK (Telegram report)
3. `review_2d` — T+2 days 09:00 MSK (web search bugs)
4. `upgrade_3d` — T+3 days 06:00 MSK (apply planned)

## Conservative Design

- **Security updates**: Applied automatically via unattended-upgrade
- **Non-security**: 2-day observation period with bug research
- **User control**: Can block any package with reason
- **Safety**: Dry-run simulation before any apt upgrade

## Requirements

- Ubuntu with apt
- Node.js + npm (for npm packages)
- Homebrew (for brew packages)
- OpenClaw with clawhub CLI
- sudo access for specific apt commands (see below)

## Sudoers Configuration

For unattended operation, grant the running user passwordless sudo for specific apt commands only. **Do not add the user to full sudoers.**

Create file `/etc/sudoers.d/sys-updater`:

```bash
# Allow sys-updater to run apt maintenance commands without password
# Replace 'username' with your actual username
username ALL=(root) NOPASSWD: /usr/bin/apt-get update
username ALL=(root) NOPASSWD: /usr/bin/apt-get -s upgrade
username ALL=(root) NOPASSWD: /usr/bin/unattended-upgrade -d
```

Set secure permissions:
```bash
sudo chmod 440 /etc/sudoers.d/sys-updater
sudo visudo -c  # Verify syntax is valid
```

### Required Commands Explained

| Command | Purpose |
|---------|---------|
| `apt-get update` | Refresh package lists |
| `apt-get -s upgrade` | Simulate upgrade (dry-run, no actual changes) |
| `unattended-upgrade -d` | Apply security updates automatically |

### Security Notes

- Only these 3 specific commands are allowed
- No `apt-get upgrade` without `-s` (simulation only for tracking)
- No `apt-get dist-upgrade` or `autoremove`
- No package installation/removal through sudo
- NPM and brew do not require sudo (user installs)
