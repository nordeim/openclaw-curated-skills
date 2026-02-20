---
name: spirit
description: State Preservation & Identity Resurrection Infrastructure Tool (SPIRIT). Preserves AI agent identity, memory, and projects to a private Git repository using git and GitHub CLI (gh).
metadata:
  openclaw:
    requires:
      bins: ["spirit", "git", "gh"]
    install:
      - id: spirit-cli
        kind: brew
        tap: TheOrionAI/tap
        package: spirit
        bins: ["spirit"]
        label: Install SPIRIT via Homebrew
---

# SPIRIT 🌌

> **S**tate **P**reservation & **I**dentity **R**esurrection **I**nfrastructure **T**ool

Preserves AI agent identity, memory, and projects in a portable Git repository.

**Your AI's spirit, always preserved.** Death. Migration. Multi-device. **Always you.**

---

## Requirements

Before using SPIRIT, ensure you have:

| Tool | Purpose | Install |
|------|---------|---------|
| `git` | Version control | Built-in or `apt install git` |
| `gh` | GitHub CLI for secure auth | `brew install gh` or see [cli.github.com](https://cli.github.com) |
| `spirit` | This tool | Via Homebrew: `brew install TheOrionAI/tap/spirit` |

---

## When to Use

- **Session ending** → Preserve state: `spirit sync`
- **Manual backup** → User says "checkpoint", "backup", "preserve"
- **Setup** → First-time initialization
- **Restore** → New server resurrection

---

## Quick Start

### 1. Install

```bash
brew tap TheOrionAI/tap
brew install spirit
```

**Verify:**
```bash
which spirit && which git && which gh
```

### 2. Initialize

```bash
spirit init --name="my-agent" --emoji="🌌"

# Output creates ~/.spirit with tracked files
```

### 3. Configure Remote Securely

**⚠️ Required:** Create a **PRIVATE** repository first.

```bash
cd ~/.spirit

# Authenticate securely (interactive, token stored encrypted)
gh auth login

# Create and clone private repo
gh repo create my-agent-state --private
gh repo clone my-agent-state .
```

**Alternative (SSH keys):**
```bash
cd ~/.spirit
git remote add origin git@github.com:USER/REPO.git
```

**Do NOT use:**
- ❌ `https://TOKEN@github.com/...` in remote URL
- ❌ `GITHUB_TOKEN` environment variable in remote URL

These expose credentials in process lists and shell history.

### 4. Sync

```bash
# Review what will be synced
spirit status

# Sync to remote
cd ~/.spirit && git add -A && git commit -m "Checkpoint" && git push

# Or use:
spirit sync
```

---

## What Gets Preserved

| Location | Contents |
|----------|----------|
| `~/.spirit/IDENTITY.md` | Your agent's identity |
| `~/.spirit/SOUL.md` | Behavior/personality |
| `~/.spirit/memory/` | Daily conversation logs |
| `~/.spirit/projects/` | Active project files |

---

## Security Checklist

☑️ **Repository:** Always PRIVATE — state files contain identity and memory

☑️ **Authentication:** Use `gh auth login` or SSH keys — never tokens in URLs

☑️ **Review:** Check `spirit status` before each sync — know what's leaving your machine

☑️ **Test:** Verify first sync in isolation before enabling automation

---

## Optional: Scheduled Sync

**⚠️ Warning:** Auto-sync pushes data to remote periodically. Only enable after verifying:

1. First manual sync completed successfully
2. Reviewed what files are tracked (`cat ~/.spirit/.spirit-tracked`)
3. Confirmed remote is private and accessible

**Manual cron (if desired):**
```bash
crontab -e
# Add: */15 * * * * cd ~/.spirit && git add -A && git commit -m "Auto" && git push 2>/dev/null || true
```

**Built-in (if desired):**
```bash
spirit autobackup --interval=15m
```

---

## Restore on New Machine

```bash
# Install
cd ~ && gh auth login
gh repo clone YOUR-PRIVATE-REPO ./.spirit

# Your agent's state is restored
```

---

## Resources

- **SPIRIT:** https://github.com/TheOrionAI/spirit
- **GitHub CLI:** https://cli.github.com
- **Security:** See SECURITY.md in SPIRIT repo

---

**License:** MIT
