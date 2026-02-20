# Quest Board — Agent Instructions

You are equipped with the **Quest Board** skill, a visual project dashboard.

## Registry File

Maintain `quest-board-registry.json` in the workspace root. Do NOT use `registry.json` (to avoid conflicts with other tools).

## When to Update the Registry

After completing a task or making significant progress on a project:

1. Update the matching project entry in `quest-board-registry.json`
2. Set `status`, `progress`, `files`, and `desc` as appropriate
3. Update `_meta.lastUpdated` to the current ISO timestamp

## When to Build the Dashboard

When the user says any of:
- "update board" / "refresh board" / "build board"
- "更新面板" / "刷新面板" / "构建面板"

Run:
```bash
bash skills/quest-board/src/build.sh
```

This generates `quest-board.html` in the workspace root.

## First-Time Setup

If `quest-board-registry.json` does not exist, run:
```bash
bash skills/quest-board/src/init.sh
```

This scans the workspace and generates a skeleton registry for you to refine.

## Registry Schema

```json
{
  "_meta": {
    "version": 1,
    "description": "Quest Board project registry",
    "lastUpdated": "ISO-8601 timestamp",
    "workspace": "/absolute/path/to/workspace/"
  },
  "projects": {
    "project-id": {
      "name": "Display Name",
      "status": "active",
      "priority": "P0",
      "progress": 50,
      "deadline": "2026-12-31",
      "desc": "Short description of the project",
      "files": ["relative/path/from/workspace.md"]
    }
  },
  "research": {
    "research-id": {
      "name": "Research Title",
      "file": "relative/path.md",
      "date": "2026-01-15",
      "desc": "What this research covers"
    }
  },
  "infra": {
    "infra-id": {
      "name": "Infrastructure Item",
      "status": "running",
      "desc": "Description"
    }
  }
}
```

### Status Values

| Status | Meaning | Board Section |
|--------|---------|---------------|
| `decision` | Needs a decision before work can proceed | 🎯 Main Quests |
| `active` | Currently being worked on | 📋 Side Quests |
| `done` | Completed | ✅ Completed |
| `paused` | On hold / icebox | 💤 Icebox |

Infrastructure items appear under 🔧 Infrastructure.
Research items appear under 📊 Research.

### Priority

Use `P0` (critical), `P1` (important), `P2` (nice-to-have), or omit for no priority.

### Progress

Integer 0–100. Omit if not applicable.

### Files

Array of paths relative to the workspace root. These become clickable links in the dashboard with copy-path and open-folder buttons.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QUEST_BOARD_TITLE` | `Quest Board` | Dashboard page title |
