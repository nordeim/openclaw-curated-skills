---
name: localsend
description: Send and receive files to/from nearby devices using the LocalSend protocol. Use when a user wants to transfer files to their phone, another computer, or any LocalSend-compatible device on the local network — or when they want to receive files from such devices.
metadata:
  openclaw:
    emoji: "📡"
    requires:
      bins:
        - localsend-cli
        - openssl
---

# LocalSend

Use this skill to transfer files between devices on the local network via the LocalSend v2 protocol. Works with any device running the LocalSend app (Android, iOS, Windows, macOS, Linux).

## Interactive Mode (Telegram Buttons)

When the user triggers LocalSend from a messaging channel, present an interactive menu using inline buttons:

### Main Menu

Present these options as buttons when the user says "localsend", "send files", "receive files", or similar:

```
📡 LocalSend
├── [🔍 Discover Devices]  → runs discover, shows device list as buttons
├── [📤 Send File]          → prompts for file path, then shows device picker
├── [📥 Receive Files]      → starts receiver in background, confirms ready
└── [❌ Cancel]             → exits
```

### Discover → Device Picker Flow

1. Run `localsend-cli discover --json -t 5`
2. Parse the JSON output into a list of devices
3. Present each device as a tappable button:
   ```
   Found 3 devices:
   [📱 Fast Potato (192.168.0.148)]
   [💻 Rami-Desktop (192.168.0.100)]
   [🖥️ Living Room PC (192.168.0.105)]
   ```
4. When user taps a device → store as target for next send operation

### Send Flow (with buttons)

1. User taps **📤 Send File** or says "send [file] to [device]"
2. If no target device cached → run discover and show device picker buttons
3. If no file specified → prompt: "Send me the file or tell me the path"
4. Confirm before sending:
   ```
   Send project.zip (4.2 MB) to Fast Potato?
   [✅ Send] [❌ Cancel]
   ```
5. Run transfer, report result

### Receive Flow (with buttons)

1. User taps **📥 Receive Files** or says "start receiving"
2. Start receiver in background (see Background Receive below)
3. Confirm ready:
   ```
   📡 Receiver active as "openclaw-workspace"
   Saving to: ~/incoming/
   Auto-accept: ON

   Send files from your device whenever ready.
   [🛑 Stop Receiver]
   ```
4. **IMPORTANT — Post-Receive Confirmation:**
   When a transfer completes, you MUST immediately confirm in chat with full details:
   ```
   ✅ Received from Fast Potato:

   📄 portfolio.zip — 240 MB
   📁 Saved to: ~/incoming/portfolio.zip

   [📂 Open/Extract] [🚀 Deploy] [🛑 Stop Receiver]
   ```

   **For images** — show the image inline using the message media path:
   ```
   ✅ Received from Fast Potato:

   🖼️ screenshot.png — 2.1 MB
   MEDIA:./incoming/screenshot.png

   [📂 Open Folder] [🛑 Stop Receiver]
   ```

   **For multiple files** — list each one:
   ```
   ✅ Received 3 files from Fast Potato:

   📄 app.apk — 45 MB
   📄 README.md — 2 KB
   🖼️ icon.png — 128 KB
   📁 Saved to: ~/incoming/

   [📂 Show All] [🛑 Stop Receiver]
   ```

### Post-Receive Detection

After starting the receiver, **actively monitor** for new files:

1. Poll the save directory every 2-3 seconds while receiver is running
2. Compare file list before and after to detect new arrivals
3. When new file(s) detected:
   - Read file metadata (name, size, type)
   - If image → present with MEDIA: path for inline preview
   - If archive (.zip, .tar.gz) → offer to extract/list contents
   - If code/text → offer to preview first few lines
   - Always show action buttons relevant to file type
4. If receiver process exits → confirm "Receiver stopped" in chat

## Commands

### Discover devices

```bash
localsend-cli discover --json -t 5
```

Lists all LocalSend devices on the network. Use `--json` for parseable output, `-t 5` for 5-second scan.

**Parse JSON output** to extract device names and IPs for button generation:
```bash
localsend-cli discover --json -t 5 | python3 -c "
import sys, json
for d in json.load(sys.stdin):
    print(f\"{d.get('alias','?')} ({d.get('ip','?')}) [{d.get('deviceType','?')}]\")
"
```

### Send files

```bash
localsend-cli send --to "Fast Potato" file1.txt file2.png
```

Use `--to` to target a device by name (case-insensitive substring match). Without `--to`, an interactive picker is shown (not useful in headless/agent mode — always use `--to`).

### Receive files

```bash
localsend-cli receive --save-dir ~/incoming -y
```

Starts an HTTPS server and listens for incoming transfers. Use `-y` to auto-accept without prompting.

## Background Receive (Important)

The receive command blocks until stopped. **Always run it in the background** so the agent stays responsive:

```bash
# Correct — run in background with alias BEFORE subcommand
localsend-cli --alias openclaw-workspace receive --save-dir ~/incoming -y
```

**CRITICAL: Flag order matters!**
- ✅ `localsend-cli --alias NAME receive --save-dir DIR -y`
- ❌ `localsend-cli receive --alias NAME --save-dir DIR -y` (FAILS — alias is a global flag)

When running in background:
1. Start with `run_in_background: true` or use the exec tool's background mode
2. Store the session/task ID so you can stop it later
3. Monitor for completion — when a file arrives, the process may exit or log output
4. Stop with the stored task ID when the user taps **🛑 Stop Receiver**

## Options

| Flag | Scope | Command | Description |
|------|-------|---------|-------------|
| `--alias NAME` | **Global** | all | Device name to advertise (default: hostname). **Must come before subcommand.** |
| `--to NAME` | Subcommand | send | Target device by name, skip interactive picker |
| `-t, --timeout N` | Subcommand | discover | Scan duration in seconds (default: 3) |
| `--json` | Subcommand | discover | Machine-readable JSON output |
| `--save-dir DIR` | Subcommand | receive | Where to save files (default: ~/Downloads) |
| `-y, --yes` | Subcommand | receive | Auto-accept incoming transfers |

## Workflow

### Standard (text-based)

1. Run `localsend-cli discover --json -t 5` to confirm the target device is visible and get its exact name.
2. If the target device is not found, ask the user to confirm LocalSend is open on it and it's on the same Wi-Fi network.
3. For sending, use `--to` with the device name — the CLI does case-insensitive substring matching.
4. For large files, warn the user the transfer may take a moment — the CLI blocks until complete.
5. When receiving, always run in background with `-y` for unattended operation.

### Recommended (button-based)

1. Show main menu buttons on trigger
2. Discover → present devices as tappable buttons
3. User taps device → cached as target
4. User sends file or path → confirm with Send/Cancel buttons
5. Show transfer progress and result
6. For receiving → start background, show Stop button

## Real-World Examples

### Deploy a website update
```
User: "Start receiving, I'm sending the new portfolio"
Agent: Starts receiver → user sends zip via LocalSend app → agent confirms receipt
       "✅ Received: rami-portfolio.zip (240 MB). Ready to deploy?"
       [🚀 Deploy] [📂 Just Save]
```

### Send build artifacts to phone
```
User: "Send the APK to my phone"
Agent: Discovers devices → shows phone as button → user taps → sends build/app.apk
       "✅ Sent app.apk (45 MB) to Fast Potato"
```

### Batch file transfer
```
User: "Send all the screenshots to my desktop"
Agent: Discovers devices → user picks desktop → sends ~/Screenshots/*.png
       "✅ Sent 12 files (28 MB total) to Rami-Desktop"
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `unrecognized arguments: --alias` | `--alias` placed after subcommand | Move `--alias` BEFORE `receive`/`send`/`discover` |
| Port 53317 in use | LocalSend GUI running on same machine | CLI auto-falls back to 53318/53319 — this is fine |
| Device not found | Target not on same WiFi or app closed | Ask user to open LocalSend app, keep screen on |
| Transfer declined (403) | Receiver rejected in UI | Use `-y` on receiver, or ask user to accept |
| Busy (409) | Another active transfer session | Wait for current transfer to finish |
| Transfer hangs | Large file on slow WiFi | Be patient — no timeout by default. Warn user for files >100MB |

## Reference

Read `references/protocol.md` for full LocalSend v2 protocol details.
