---
name: cursor-cli
description: Ask Cursor CLI (Cursor's terminal agent) a question and return its answer. Use for coding help, code review, or explanations—OpenClaw runs the agent and gives you the response.
metadata: {"openclaw":{"requires":{"bins":["agent"]},"emoji":"⌨️","homepage":"https://cursor.com/docs/cli/overview"}}
---

# Cursor CLI skill

When the user wants an answer from **Cursor's AI** (Cursor CLI / agent), use this flow:

1. **Run Cursor CLI non-interactively** via the `bash` tool:
   - Use the `agent` command with a prompt and text output.
   - From the user's workspace or a sensible project directory (e.g. `~/.openclaw/workspace` or the path the user indicated), run:
   ```bash
   agent -p "USER_QUESTION_HERE" --output-format text
   ```
   - For read-only Q&A (no code edits), use Ask mode:
   ```bash
   agent -p "USER_QUESTION_HERE" --mode=ask --output-format text
   ```
   - Replace `USER_QUESTION_HERE` with the user's actual question, properly escaped for the shell (use single quotes around the prompt; if the prompt contains single quotes, escape them or use a here-doc).

2. **Capture and return the output**: The agent prints the answer to stdout. Return that full output to the user as OpenClaw's reply (summarize only if it is extremely long and the user asked for a summary).

3. **Working directory**: If the user mentioned a project or path, run `agent` from that directory (e.g. `cd /path/to/project && agent -p "..." --output-format text`). Otherwise use the default OpenClaw workspace or current context.

4. **Timeouts**: Cursor CLI may take 30–120 seconds for complex questions. Do not assume failure too quickly.

5. **When to use**: Prefer this skill when the user explicitly asks to "ask Cursor," "use Cursor CLI," "get Cursor's answer," or wants coding/explanation help that should come from Cursor's agent. For general chat, use OpenClaw's normal model.

## Examples

- User: "Ask Cursor CLI: how do I fix a merge conflict in git?"
  → Run: `agent -p "how do I fix a merge conflict in git?" --mode=ask --output-format text` and return the stdout.

- User: "Run cursor agent on this: explain what recursion is in programming"
  → Run: `agent -p "explain what recursion is in programming" --mode=ask --output-format text` and return the stdout.

- User: "Have Cursor review the code in ~/myapp for security issues"
  → Run: `cd ~/myapp && agent -p "review the code in this project for security issues" --output-format text` and return the stdout.
