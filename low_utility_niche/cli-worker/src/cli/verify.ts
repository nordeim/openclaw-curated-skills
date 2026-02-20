import { verifyAll } from "../auth/verify.js";

export async function runVerify(): Promise<number> {
  const result = verifyAll();
  if (result.ok) {
    console.log("✓ Kimi CLI is installed and authenticated.");
    return 0;
  }
  console.error("✗ Verification failed:", result.reason);
  if (result.detail) console.error("\n", result.detail);
  console.error(
    "\nTo fix:\n  1. Run: kimi\n  2. Type: /login\n  3. Complete browser OAuth\n  4. Verify with: cli-worker verify"
  );
  return 1;
}
