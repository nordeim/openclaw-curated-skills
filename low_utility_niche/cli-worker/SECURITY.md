# Security

## How the skill invokes the Kimi CLI

The skill runs the Kimi CLI via Node.js `child_process.spawn()`, **not** a shell:

- **No shell:** The prompt is passed as a single element in the `args` array to `spawn(cmd, args, options)`. The operating system passes it as one argument to the `kimi` process. There is no `execSync('kimi -p "' + prompt + '"')` or similar; therefore there is no shell command injection at this layer.
- **Input sanitization:** Before calling the CLI, the prompt is sanitized:
  - Null bytes (`\0`) are removed (they could truncate arguments in C-style parsers).
  - Other C0 control characters (except tab, newline, carriage return) are replaced with spaces to avoid control sequences that could confuse downstream parsers.
- **Trust boundary:** The skill does not store or log credentials. It only verifies that the user has already authenticated the Kimi CLI; the CLI runs with the user’s privileges in the configured worktree.

## Path traversal (taskId)

The `taskId` argument for `cli-worker status <taskId>` and `cli-worker worktree remove <taskId>` is validated before use:

- **Allowed:** Single segment only: alphanumeric and hyphens (e.g. UUIDs like `550e8400-e29b-41d4-a716-446655440000`). No path separators (`/`, `\`), no `..`, no leading hyphen.
- **Resolution:** Paths are resolved with `path.resolve(basePath, taskId)` and checked to remain under `basePath` before reading files or running `git worktree remove`. Invalid `taskId` is rejected with an error.

This prevents arbitrary file read (e.g. `status ../../../../etc/passwd`) and destructive worktree remove in arbitrary directories.

## Credentials and environment variables

- **No required env vars.** The skill works with defaults (e.g. `kimi` on PATH, `~/.kimi` for config, `~/.openclaw` for config/logs/worktrees). All env vars are optional overrides.
- **Optional env vars:** `KIMI_CLI_PATH`, `KIMI_HOME`, `OPENCLAW_CONFIG`, `OPENCLAW_LOG_DIR`, `KIMI_NO_BROWSER`. Documented in README.
- **KIMI_CLI_PATH:** If set, it is validated (no spaces, no shell metacharacters, length limit). Verify and spawn use `spawnSync` / `spawn` with an argument array and `shell: false`, so the value is never passed to a shell. Invalid values fall back to `kimi`.
- **Paths:** The skill reads config/credentials under `~/.kimi` (Kimi’s own dir) and writes logs and task manifests under `~/.openclaw`. No credentials are stored by the skill.

## RCE / argument injection

The ClawHub finding concerns possible RCE if the Kimi CLI were susceptible to argument or command injection. On the skill side:

1. We never invoke a shell; we use `spawn` with an argument array.
2. We sanitize the prompt (null bytes and control characters) before passing it as the `-p` argument.
3. The Kimi CLI is a dependency run by the user; we recommend keeping it updated. Any vulnerability inside the Kimi CLI itself would need to be addressed by its maintainers.

## Reporting a vulnerability

If you believe you’ve found a security issue, please open an issue on the [repository](https://github.com/quratus/openclaw_cli_agent_skill) or contact the maintainers privately.
