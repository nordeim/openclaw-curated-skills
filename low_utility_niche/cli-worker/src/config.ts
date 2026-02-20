import fs from "node:fs";
import path from "node:path";
import os from "node:os";

export interface OpenClawConfig {
  worktree?: { basePath?: string };
  [key: string]: unknown;
}

const DEFAULT_OPENCLAW_JSON = path.join(
  os.homedir(),
  ".openclaw",
  "openclaw.json"
);

export function getConfigPath(): string {
  return process.env.OPENCLAW_CONFIG ?? DEFAULT_OPENCLAW_JSON;
}

export function getConfig(): OpenClawConfig {
  const configPath = getConfigPath();
  try {
    if (!fs.existsSync(configPath)) {
      return {};
    }
    const raw = fs.readFileSync(configPath, "utf-8");
    return JSON.parse(raw) as OpenClawConfig;
  } catch {
    console.error("Config unreadable, using defaults.");
    return {};
  }
}
