---
name: mac-reminders-agent
version: 1.1.2
author: swancho
license: CC-BY-NC-4.0
description: |
  Integrate with macOS Reminders app to check today's/this week's tasks or add new reminders.
  Supports native recurrence (매주/weekly/毎週/每周) via Swift EventKit - creates single reminder with repeat rule.
  Supports multiple languages (en, ko, ja, zh) for trigger detection and response formatting.
  When users request recurring reminders, MUST use --repeat option (daily|weekly|monthly|yearly).
requirements:
  runtime:
    - node >= 18.0.0
    - npm
    - macOS with Xcode Command Line Tools (includes Swift compiler)
  permissions:
    - macOS Reminders access (system prompt on first use)
install: |
  cd $SKILL_DIR && npm install
---

# Mac Reminders Agent

## Overview

This skill integrates with the local macOS **Reminders** app to:

- View and organize today's/this week's reminders (work/personal/sessions)
- Add new reminders based on natural language requests
- **Native recurrence**: Weekly, daily, monthly, yearly repeating reminders
- **Multi-language support**: English, Korean, Japanese, Chinese

The skill uses the following files relative to its directory:

- `cli.js` (unified entry point)
- `reminders/apple-bridge.js` (backend: AppleScript + `applescript` npm module)
- `reminders/eventkit-bridge.swift` (native recurrence via Swift EventKit)
- `locales.json` (language-specific triggers and responses)

## Language Support

The skill automatically detects user language or can be explicitly set via `--locale` parameter.

### Supported Languages

| Code | Language | Example Trigger |
|------|----------|-----------------|
| `en` | English | "What do I have to do today?" |
| `ko` | 한국어 | "오늘 할 일 뭐 있어?" |
| `ja` | 日本語 | "今日のタスクは？" |
| `zh` | 中文 | "今天有什么任务？" |

### Language Detection

1. **Explicit**: Use `--locale` parameter
2. **Automatic**: Detect from user's message language
3. **Default**: Falls back to `en` (English)

---

## How It Works

User natural language requests are handled in two cases:

1. **List reminders (list)**
2. **Add reminder (add)**

For each case, call the Node.js CLI, receive JSON results, and format them using locale-specific templates.

---

## 1) List Reminders

### Trigger Examples (by language)

**English:**
- "What do I have to do today?"
- "Show me today's reminders"
- "What's on my schedule this week?"

**Korean (한국어):**
- "오늘 할 일 뭐 있어?"
- "오늘 미리알림 정리해줘"
- "이번 주 일정 뭐 있어?"

**Japanese (日本語):**
- "今日のタスクは？"
- "今日のリマインダーを見せて"

**Chinese (中文):**
- "今天有什么任务？"
- "显示今天的提醒"

### Command Invocation

```bash
# List with default locale (en)
node skills/mac-reminders-agent/cli.js list --scope today

# List with specific locale
node skills/mac-reminders-agent/cli.js list --scope week --locale ko
```

### Scope Options

- `today` - Today only
- `week` - This week (today ~ +7 days)
- `all` - All reminders

### Output Format

Returns JSON array:

```json
[
  {
    "title": "Task title",
    "due": "2026-02-05T16:30:00" | null
  }
]
```

### Response Formatting

Use `locales.json` templates to format responses in user's language:

**English:**
```
[Incomplete Reminders]
- 2/2 (Mon) 09:00 [Work] Meeting
- 2/3 (Tue) 14:00 [Personal] Visit bank

[Completed]
- 2/1 (Sun) [Work] Submit report ✅
```

**Korean:**
```
[미완료 미리알림]
- 2/2 (월) 09:00 [업무] 회의
- 2/3 (화) 14:00 [개인] 은행 방문

[완료됨]
- 2/1 (일) [업무] 보고서 제출 ✅
```

---

## 2) Add Reminder

### Trigger Examples (by language)

**English:**
- "Add a meeting reminder for 9am tomorrow"
- "Set a reminder to submit report by Friday"

**Korean (한국어):**
- "내일 아침 9시에 회의 미리알림 추가해줘"
- "이번 주 금요일까지 보고서 제출 미리알림 넣어줘"

**Japanese (日本語):**
- "明日の朝9時に会議のリマインダーを追加して"

**Chinese (中文):**
- "添加明天早上9点的会议提醒"

### Command Invocation

```bash
# Add with locale
node skills/mac-reminders-agent/cli.js add --title "Meeting" --due "2026-02-05T09:00:00+09:00" --locale ko
```

### Parameters

- `--title` (required): Reminder title
- `--due` (optional): ISO 8601 format (`YYYY-MM-DDTHH:mm:ss+09:00`)
- `--note` (optional): Additional notes
- `--locale` (optional): Response language (en, ko, ja, zh)

### Response Examples

**English:**
- "Added 'Meeting' reminder for 9am tomorrow."
- "Added 'Submit report' reminder without a due date."

**Korean:**
- "'회의' 미리알림을 추가했어요 (내일 오전 9시)."
- "'보고서 제출' 미리알림을 추가했어요 (마감일 없음)."

---

## 3) Recurring Reminders (Native Recurrence)

Use `--repeat` to create reminders with **native recurrence** (single reminder with repeat rule, not multiple copies).

### Command Invocation

```bash
# Weekly recurring reminder
node skills/mac-reminders-agent/cli.js add --title "Weekly standup" --due "2026-02-10T09:00:00+09:00" --repeat weekly

# Bi-weekly reminder
node skills/mac-reminders-agent/cli.js add --title "Sprint review" --due "2026-02-10T14:00:00+09:00" --repeat weekly --interval 2

# Monthly reminder until end of year
node skills/mac-reminders-agent/cli.js add --title "Monthly report" --due "2026-02-28T17:00:00+09:00" --repeat monthly --repeat-end 2026-12-31
```

### Parameters

- `--repeat` (optional): `daily`, `weekly`, `monthly`, `yearly`
- `--interval` (optional): Repeat interval (default: 1). Example: `--interval 2` = every 2 weeks
- `--repeat-end` (optional): End date in `YYYY-MM-DD` format

### IMPORTANT: Always use --repeat for recurring schedules

When user requests recurring reminders (매주, 격주, 매월, etc.), **MUST use --repeat option**.
Do NOT create multiple individual reminders manually.

**Correct:**
```bash
node cli.js add --title "주간 회의" --due "2026-02-10T09:00:00+09:00" --repeat weekly
```

**Wrong (DO NOT DO THIS):**
```bash
# Creating 12 separate reminders is WRONG
node cli.js add --title "주간 회의 - 2/10" --due "2026-02-10T09:00:00+09:00"
node cli.js add --title "주간 회의 - 2/17" --due "2026-02-17T09:00:00+09:00"
...
```

---

## Error Handling

### Locale-aware Error Messages

**English:**
- "There was a problem accessing the Reminders app."

**Korean:**
- "미리알림 앱에 접근하는 데 문제가 생겼어요."

**Japanese:**
- "リマインダーアプリへのアクセスに問題が発生しました。"

### Fallback Suggestions

When automatic integration fails, offer alternatives in user's language.

---

## Requirements & Installation

### System Requirements

| Requirement | Details |
|-------------|---------|
| **OS** | macOS only (tested on macOS 13+) |
| **Node.js** | v18.0.0 or higher |
| **npm** | Included with Node.js |
| **Swift** | Included with Xcode Command Line Tools |

### Installation

```bash
# 1. Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# 2. Install npm dependencies
cd $SKILL_DIR
npm install
```

### macOS Permissions

This skill requires access to the **Reminders** app. On first use:

1. macOS will display a permission dialog asking to allow access to Reminders
2. Click **"OK"** or **"Allow"** to grant access
3. If denied, go to **System Settings > Privacy & Security > Reminders** and enable access for Terminal/your IDE

> **Note**: The Swift EventKit bridge (`eventkit-bridge.swift`) is compiled on-the-fly when needed. No manual compilation required.

---

## Summary

- Multi-language support via `locales.json` (en, ko, ja, zh)
- Core commands:
  - `list --scope today|week|all [--locale XX]`
  - `add --title ... [--due ...] [--repeat daily|weekly|monthly|yearly] [--interval N] [--repeat-end YYYY-MM-DD] [--locale XX]`
- **Native recurrence**: Use `--repeat` for recurring reminders (creates single reminder with repeat rule)
- Automatically detect user language or use explicit `--locale` parameter
- Format responses using locale-specific templates
