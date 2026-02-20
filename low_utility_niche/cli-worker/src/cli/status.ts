import path from "node:path";
import { getWorktreeBasePath } from "../worktree/repo.js";
import { parseReport } from "../parser/report.js";
import { resolveTaskIdPath } from "../safe-task-id.js";

export async function runStatus(args: string[]): Promise<number> {
  const taskId = args[0];
  if (!taskId) {
    console.error("Usage: cli-worker status <taskId>");
    return 1;
  }

  const basePath = getWorktreeBasePath();
  const worktreeDir = resolveTaskIdPath(basePath, taskId);
  if (!worktreeDir) {
    console.error("Invalid taskId: must be alphanumeric and hyphens only (no path traversal).");
    return 1;
  }
  const reportPath = path.join(
    worktreeDir,
    ".openclaw",
    "kimi-reports",
    `${taskId}.json`
  );

  try {
    const report = parseReport(reportPath);
    console.log("Task ID:", report.task_id ?? taskId);
    console.log("Status:", report.execution?.status ?? "unknown");
    if (report.execution?.duration_seconds != null) {
      console.log("Duration (s):", report.execution.duration_seconds);
    }
    if (report.artifacts?.test_status) {
      console.log("Tests:", report.artifacts.test_status);
    }
    if (report.artifacts?.files_modified?.length) {
      console.log(
        "Files modified:",
        report.artifacts.files_modified.join(", ")
      );
    }
    if (report.cognitive_state?.blockers?.length) {
      console.log("Blockers:", report.cognitive_state.blockers.join("; "));
    }
    return 0;
  } catch (err) {
    console.error("Status failed:", err instanceof Error ? err.message : err);
    return 1;
  }
}
