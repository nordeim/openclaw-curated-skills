import { execSync } from "child_process";

interface ToolContext {
  action: string;
}

export function register(api: any) {
  api.registerTool({
    id: "sparkle_vpn_start",
    description: "Start Sparkle VPN - Launch the application and activate DirectAccess",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/start-vpn.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_stop",
    description: "Stop Sparkle VPN - Deactivate connection and close application",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/stop-vpn.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });
}
