import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { verifyAll } from "../auth/verify.js";
import { runKimi } from "../spawn/run.js";
import { parseStreamJson } from "../parser/stream-json.js";
import { generateAgentsMd } from "../templates/agents-md.js";
import { writeManifest } from "../manifest/write.js";
import { getRepoPath } from "../worktree/repo.js";
import { createWorktree } from "../worktree/create.js";
import type { TaskInput } from "../types.js";

function isGitRepo(dir: string): boolean {
  const gitDir = path.join(dir, ".git");
  return fs.existsSync(gitDir) && fs.statSync(gitDir).isDirectory();
}

function parseArgs(args: string[]): {
  prompt: string;
  outputFormat: "text" | "json";
  cwd: string;
  repoFlag?: string;
  timeoutMinutes?: number;
  constraints: string[];
  successCriteria: string[];
  relevantFiles: string[];
} {
  let prompt = "";
  let outputFormat: "text" | "json" = "json";
  const cwd = process.cwd();
  let repoFlag: string | undefined;
  let timeoutMinutes: number | undefined;
  const constraints: string[] = [];
  const successCriteria: string[] = [];
  let relevantFiles: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--repo" && args[i + 1]) {
      repoFlag = args[i + 1];
      i++;
      continue;
    }
    if (args[i] === "--timeout" && args[i + 1]) {
      timeoutMinutes = parseInt(args[i + 1], 10);
      if (!Number.isFinite(timeoutMinutes) || timeoutMinutes < 1)
        timeoutMinutes = undefined;
      i++;
      continue;
    }
    if (args[i] === "--output-format" && args[i + 1]) {
      const fmt = args[i + 1];
      outputFormat = fmt === "text" ? "text" : "json";
      i++;
      continue;
    }
    if (args[i] === "--constraint" && args[i + 1]) {
      constraints.push(args[i + 1]);
      i++;
      continue;
    }
    if (args[i] === "--success" && args[i + 1]) {
      successCriteria.push(args[i + 1]);
      i++;
      continue;
    }
    if (args[i] === "--files" && args[i + 1]) {
      relevantFiles = args[i + 1]
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      i++;
      continue;
    }
    if (!args[i].startsWith("--")) {
      prompt = args[i];
      break;
    }
  }

  return {
    prompt,
    outputFormat,
    cwd,
    repoFlag,
    timeoutMinutes,
    constraints,
    successCriteria,
    relevantFiles,
  };
}

const AGENTS_MD = "AGENTS.md";

export async function runExecute(args: string[]): Promise<number> {
  const parsed = parseArgs(args);
  const { prompt, outputFormat, cwd } = parsed;

  if (!prompt) {
    console.error(
      'Usage: cli-worker execute "<prompt>" [--output-format text|json] [--constraint "X"] [--success "Y"] [--files "path1,path2"]'
    );
    return 1;
  }

  const auth = verifyAll();
  if (!auth.ok) {
    console.error("✗", auth.detail ?? auth.reason);
    return 1;
  }

  const taskId = randomUUID();
  const repoPath = getRepoPath(cwd, parsed.repoFlag);
  let worktreePath: string;
  if (isGitRepo(repoPath)) {
    try {
      worktreePath = await createWorktree(repoPath, taskId);
    } catch (err) {
      console.error(
        "Failed to create worktree:",
        err instanceof Error ? err.message : err
      );
      return 1;
    }
  } else {
    worktreePath = cwd;
  }
  const reportPath = path.join(
    worktreePath,
    ".openclaw",
    "kimi-reports",
    `${taskId}.json`
  );

  const task: TaskInput = {
    prompt,
    worktreePath,
    taskId,
    reportPath,
    relevantFiles:
      parsed.relevantFiles.length > 0 ? parsed.relevantFiles : undefined,
    constraints: parsed.constraints.length > 0 ? parsed.constraints : undefined,
    successCriteria:
      parsed.successCriteria.length > 0 ? parsed.successCriteria : undefined,
  };

  try {
    writeManifest(taskId, task, worktreePath, reportPath);
    const agentsMd = generateAgentsMd(task);
    fs.writeFileSync(path.join(worktreePath, AGENTS_MD), agentsMd, "utf-8");
  } catch (err) {
    console.error(
      "Could not write task files:",
      err instanceof Error ? err.message : err
    );
    return 1;
  }

  const timeoutMs =
    parsed.timeoutMinutes != null
      ? parsed.timeoutMinutes * 60 * 1000
      : undefined;
  const result = await runKimi(prompt, worktreePath, { timeoutMs });

  if (result.exitCode !== 0) {
    const exitCode = result.exitCode ?? 1;
    const stderrMsg = result.stderr ? `: ${result.stderr.trim()}` : "";
    console.error(`Kimi failed (exit ${exitCode})${stderrMsg}`);
    return exitCode;
  }

  if (outputFormat === "text") {
    result.stdoutLines.forEach((line) => console.log(line));
    return 0;
  }

  const { finalText } = parseStreamJson(result.stdoutLines);
  if (finalText) console.log(finalText);
  return 0;
}
