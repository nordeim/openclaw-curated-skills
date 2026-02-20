const { JsonRpcProvider, Contract } = require('ethers');
const strategyExecutorArtifact = require('../references/abi/StrategyExecutor.json');
const assetUniverseArtifact = require('../references/abi/AssetUniversePolicy.json');
const staticAllocationArtifact = require('../references/abi/StaticAllocationPolicy.json');
const slippageArtifact = require('../references/abi/SlippagePolicy.json');

const rpcUrl = process.env.RPC_URL || 'https://mainnet.base.org';
const executorAddress = process.env.EXECUTOR_MODULE_ADDRESS;

if (!executorAddress) {
  console.error('Error: Missing EXECUTOR_MODULE_ADDRESS env var.');
  process.exit(1);
}

const TOKENS = {
  WETH: '0x4200000000000000000000000000000000000006',
  USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  WBTC: '0x0555E30da8f98308EdB960aa94C0Db47230d2B9c',
  EURC: '0x60a3E35Cc302bFA44Cb288Bc5a4F316Fdb1adb42',
  cbETH: '0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22',
  cbBTC: '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',
  AAVE: '0x54330d28ca3357F294334BDC454a032e7f353416',
  LINK: '0x88Fb150BDc53A65fe94Dea0c9BA0a6dAf8C6e196',
  USDe: '0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34',
  sUSDe: '0x2113938A47a0F084bB494c289c8A5c0c98D8Ca2d',
  MORPHO: '0xBaA644bCfe0E546D67f58E5E8EC529618B8B8350'
};

const ABIs = {
  Executor: strategyExecutorArtifact.abi || strategyExecutorArtifact,
  AssetUniverse: assetUniverseArtifact.abi || assetUniverseArtifact,
  StaticAllocation: staticAllocationArtifact.abi || staticAllocationArtifact,
  Slippage: slippageArtifact.abi || slippageArtifact
};

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

  if (byIndex.length > 0) {
    return [...new Set(byIndex)];
  }

  try {
    const list = await executor.getPolicies();
    return [...new Set(list.filter(Boolean))];
  } catch (_e) {
    return [];
  }
}

async function inspect() {
  const provider = new JsonRpcProvider(rpcUrl);
  console.log('=== 31Third Policy Inspection Tool ===');
  console.log(`Target Executor: ${executorAddress}\n`);

  const executor = new Contract(executorAddress, ABIs.Executor, provider);
  const policies = await getExecutorPolicies(executor);
  try {
    if (policies.length === 0) throw new Error('no policies discovered');
    console.log(`Found ${policies.length} Active Policies:`);
    policies.forEach((p) => console.log(`- ${p}`));
    console.log('');
  } catch (e) {
    console.error('Failed to fetch policies from executor:', e.message);
    return;
  }

  for (const policyAddr of policies) {
    console.log(`--- Inspecting Policy: ${policyAddr} ---`);
    let identified = false;

    try {
      const au = new Contract(policyAddr, ABIs.AssetUniverse, provider);
      const tokens = await au.getTokens();
      console.log('Type: Asset Universe Policy');
      console.log(`Allowed Tokens (${tokens.length}):`);

      const addressToName = {};
      for (const [name, addr] of Object.entries(TOKENS)) addressToName[addr.toLowerCase()] = name;
      tokens.forEach((addr) => console.log(`- ${addr} (${addressToName[addr.toLowerCase()] || 'Unknown Token'})`));
      identified = true;
    } catch (_e) {
      // not asset universe
    }

    if (!identified) {
      try {
        const sa = new Contract(policyAddr, ABIs.StaticAllocation, provider);
        const trigger = await sa.triggerThresholdBps();
        const tolerance = await sa.toleranceThresholdBps();
        console.log('Type: Static Allocation Policy');
        console.log(`Trigger Threshold: ${trigger} bps`);
        console.log(`Tolerance Threshold: ${tolerance} bps`);
        identified = true;
      } catch (_e) {
        // not static allocation
      }
    }

    if (!identified) {
      try {
        const sp = new Contract(policyAddr, ABIs.Slippage, provider);
        const max = await sp.maxSlippageBps();
        console.log('Type: Slippage Policy');
        console.log(`Max Slippage: ${max} bps`);
        identified = true;
      } catch (_e) {
        // not slippage
      }
    }

    if (!identified) {
      console.log('Type: Unknown Policy (custom or proxy)');
    }
    console.log('');
  }
}

inspect();
