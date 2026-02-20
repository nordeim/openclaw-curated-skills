const { JsonRpcProvider, Contract } = require('ethers');
const strategyExecutorArtifact = require('../references/abi/StrategyExecutor.json');

const rpcUrl = process.env.RPC_URL || 'https://mainnet.base.org';
const safeAddress = process.env.SAFE_ADDRESS;
const targetExecutor = process.env.CHECK_EXECUTOR_ADDRESS;

const SAFE_ABI = [
  'function isModuleEnabled(address module) view returns (bool)',
  'function getModulesPaginated(address start, uint256 pageSize) view returns (address[] array, address next)'
];

const EXECUTOR_ABI = strategyExecutorArtifact.abi || strategyExecutorArtifact;
const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';
const MAX_POLICY_SCAN = 256;

async function getExecutorPolicies(executor) {
  const byIndex = [];
  for (let i = 0; i < MAX_POLICY_SCAN; i += 1) {
    try {
      const policy = await executor.policies(i);
      if (!policy || policy.toLowerCase() === ZERO_ADDRESS) break;
      byIndex.push(policy);
    } catch (_e) {
      break;
    }
  }

  if (byIndex.length > 0) return [...new Set(byIndex)];

  try {
    const list = await executor.getPolicies();
    return [...new Set(list.filter(Boolean))];
  } catch (_e) {
    return [];
  }
}

async function check() {
  const provider = new JsonRpcProvider(rpcUrl);

  if (!safeAddress) {
    console.error('Error: Missing SAFE_ADDRESS env var.');
    return;
  }

  let executorsToCheck = targetExecutor ? [targetExecutor] : [];
  const safe = new Contract(safeAddress, SAFE_ABI, provider);

  try {
    const allModules = [];
    let start = '0x0000000000000000000000000000000000000001';
    const sentinel = '0x0000000000000000000000000000000000000001';

    // Safe modules are returned paginated; iterate until the sentinel is returned as next pointer.
    while (true) {
      const page = await safe.getModulesPaginated(start, 50);
      const modules = page.array || page[0] || [];
      const next = page.next || page[1] || sentinel;
      allModules.push(...modules);
      if (next.toLowerCase() === sentinel) break;
      start = next;
    }

    console.log(`Checking Safe: ${safeAddress}`);

    if (allModules.length === 0) {
      console.log('No modules enabled on this Safe.');
      return;
    }

    console.log(`Enabled Modules (${allModules.length}):`);
    allModules.forEach((m, i) => console.log(`[${i}] ${m}`));

    if (executorsToCheck.length === 0) {
      executorsToCheck = allModules;
    }
  } catch (e) {
    console.log('Safe check failed:', e.message);
    return;
  }

  console.log('\nScanning modules for policy configurations...');

  for (const exAddr of executorsToCheck) {
    const ex = new Contract(exAddr, EXECUTOR_ABI, provider);
    try {
      const policies = await getExecutorPolicies(ex);
      if (policies.length === 0) continue;
      console.log(`\nExecutor Identified: ${exAddr}`);
      console.log(`Attached Policies (${policies.length}):`);
      policies.forEach((p) => console.log(`- ${p}`));
    } catch (_e) {
      // not strategy executor
    }
  }
}

check();
