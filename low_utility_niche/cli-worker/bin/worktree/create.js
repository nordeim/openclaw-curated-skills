import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { getWorktreeBasePath } from "./repo.js";
export async function createWorktree(repoPath, taskId, baseBranch = "HEAD") {
    const basePath = getWorktreeBasePath();
    const worktreeBase = path.join(basePath, taskId);
    if (fs.existsSync(worktreeBase)) {
        throw new Error(`Worktree already exists: ${worktreeBase}`);
    }
    const branchName = `openclaw/${taskId}`;
    execSync(`git worktree add -b ${branchName} "${worktreeBase}" ${baseBranch}`, {
        cwd: repoPath,
        encoding: "utf-8",
    });
    return worktreeBase;
}
//# sourceMappingURL=create.js.map