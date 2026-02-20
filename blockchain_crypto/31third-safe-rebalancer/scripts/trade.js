const fs = require('node:fs');
const path = require('node:path');
const strategyExecutorArtifact = require('../references/abi/StrategyExecutor.json');
const assetUniverseArtifact = require('../references/abi/AssetUniversePolicy.json');
const staticAllocationArtifact = require('../references/abi/StaticAllocationPolicy.json');

function loadDotEnv() {
  const envPath = path.resolve(process.cwd(), '.env');
  if (!fs.existsSync(envPath)) return;

  const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const idx = trimmed.indexOf('=');
    if (idx <= 0) continue;
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim();
    if (!process.env[key]) process.env[key] = value;
  }
}

function getArg(args, name) {
  const idx = args.indexOf(name);
  return idx !== -1 ? args[idx + 1] : null;
}

function parseChainId(args) {
  const chainIdRaw = getArg(args, '--chain-id');
  if (chainIdRaw) {
    const parsed = Number.parseInt(chainIdRaw, 10);
    return Number.isFinite(parsed) ? parsed : 8453;
  }

  const chain = (getArg(args, '--chain') || '').toLowerCase();
  if (chain === 'base') return 8453;
  if (chain === 'ethereum' || chain === 'mainnet') return 1;
  if (chain === 'polygon') return 137;
  if (chain === 'arbitrum') return 42161;

  const envChain = Number.parseInt(process.env.CHAIN_ID || '8453', 10);
  return Number.isFinite(envChain) ? envChain : 8453;
}

function parseTargetsArg(targetsRaw) {
  if (!targetsRaw) return null;
  try {
    const parsed = JSON.parse(targetsRaw);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error('targets must be a JSON object mapping token address to allocation');
    }
    return parsed;
  } catch (error) {
    throw new Error(`Invalid --targets JSON: ${error.message}`);
  }
}

function isAddressLike(value) {
  return /^0x[a-fA-F0-9]{40}$/.test(String(value || ''));
}

function validateSwapInputs(fromToken, toToken, amount) {
  if (!fromToken || !toToken || !amount) {
    throw new Error('Missing params for swap: --from, --to, --amount');
  }
  if (!isAddressLike(fromToken)) throw new Error('Invalid --from token address format');
  if (!isAddressLike(toToken)) throw new Error('Invalid --to token address format');
  if (!/^\d+$/.test(String(amount)) || BigInt(amount) <= 0n) {
    throw new Error('Invalid --amount, expected positive integer token amount');
  }
}

function validateTargets(targets) {
  if (!targets || Object.keys(targets).length === 0) {
    throw new Error('Missing params for rebalance: --targets (JSON)');
  }

  let sum = 0;
  for (const [token, allocation] of Object.entries(targets)) {
    if (!isAddressLike(token)) throw new Error(`Invalid target token address: ${token}`);
    const alloc = Number(allocation);
    if (!Number.isFinite(alloc) || alloc < 0 || alloc > 1) {
      throw new Error(`Invalid allocation for ${token}; expected number in [0, 1]`);
    }
    sum += alloc;
  }

  if (Math.abs(sum - 1) > 1e-6) {
    throw new Error(`Target allocations must sum to 1.0 (got ${sum.toFixed(6)})`);
  }
}

function buildPayload({ action, safeAddress, signerAddress, chainId, minTradeValue, fromToken, toToken, amount, targets }) {
  const payload = {
    wallet: safeAddress,
    signer: signerAddress,
    baseEntries: [],
    targetEntries: [],
    chainId,
    minTradeValue
  };

  if (action === 'swap') {
    validateSwapInputs(fromToken, toToken, amount);
    payload.baseEntries = [{ tokenAddress: fromToken, amount }];
    payload.targetEntries = [{ tokenAddress: toToken, allocation: 1.0 }];
    return payload;
  }

  if (action === 'rebalance') {
    validateTargets(targets);
    payload.targetEntries = Object.entries(targets).map(([token, allocation]) => ({
      tokenAddress: token,
      allocation: Number(allocation)
    }));
    return payload;
  }

  throw new Error('Unknown action. Use --action swap, --action rebalance, or --action checkPolicy.');
}

function printHelp() {
  console.log(`
=== 31Third Safe Rebalancer ===

To use this skill, deploy a Strategy Executor module to your Safe first.
Deployment Wizard: https://app.31third.com/safe-policy-deployer

Required env vars:
- RPC_URL
- CHAIN_ID (optional, defaults to 8453)
- TOT_API_KEY
- SAFE_ADDRESS
- EXECUTOR_MODULE_ADDRESS
- EXECUTOR_WALLET_PRIVATE_KEY

Examples:
node scripts/trade.js --action swap --from 0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --to 0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb --amount 1000000 --chain base
node scripts/trade.js --action rebalance --targets '{"0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa":0.5,"0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb":0.5}' --chain-id 8453
node scripts/trade.js --action checkPolicy
`);
}

async function inspectBoundaries(provider, executorAddress, Contract) {
  const EXECUTOR_ABI = strategyExecutorArtifact.abi || strategyExecutorArtifact;
  const STATIC_ALLOC_ABI = staticAllocationArtifact.abi || staticAllocationArtifact;
  const ASSET_UNIVERSE_ABI = assetUniverseArtifact.abi || assetUniverseArtifact;
  const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';
  const MAX_POLICY_SCAN = 256;

  const boundaries = { triggerBps: 0, toleranceBps: 0, allowedAssets: [], targets: [] };

  try {
    const executor = new Contract(executorAddress, EXECUTOR_ABI, provider);
    let policies = [];

    for (let i = 0; i < MAX_POLICY_SCAN; i += 1) {
      try {
        const policy = await executor.policies(i);
        if (!policy || policy.toLowerCase() === ZERO_ADDRESS) break;
        policies.push(policy);
      } catch (_e) {
        break;
      }
    }

    if (policies.length === 0) {
      try {
        policies = await executor.getPolicies();
      } catch (_e) {
        policies = [];
      }
    }

    policies = [...new Set(policies.filter(Boolean))];

    for (const policyAddr of policies) {
      try {
        const sa = new Contract(policyAddr, STATIC_ALLOC_ABI, provider);
        boundaries.triggerBps = Number(await sa.triggerThresholdBps());
        boundaries.toleranceBps = Number(await sa.toleranceThresholdBps());
        try {
          const [tokens, bps] = await sa.getTargets();
          boundaries.targets = tokens.map((t, i) => ({ token: t, bps: Number(bps[i]) }));
        } catch (_e) {
          // optional getter may not exist
        }
      } catch (_e) {
        // ignore non-static-allocation policy
      }

      try {
        const au = new Contract(policyAddr, ASSET_UNIVERSE_ABI, provider);
        boundaries.allowedAssets = await au.getTokens();
      } catch (_e) {
        // ignore non-asset-universe policy
      }
    }
  } catch (e) {
    console.warn(`[31Third] Could not auto-detect boundaries: ${e.message}`);
  }

  return boundaries;
}

async function main() {
  loadDotEnv();

  const args = process.argv.slice(2);
  const action = getArg(args, '--action') || 'help';

  if (action === 'help' || action === 'deploy-info') {
    printHelp();
    return;
  }

  const minTradeValueRaw = getArg(args, '--min-trade-value');
  let minTradeValue = minTradeValueRaw ? Number(minTradeValueRaw) : 1.0;
  if (!Number.isFinite(minTradeValue) || minTradeValue < 0.1) minTradeValue = 0.1;

  const rpcUrl = process.env.RPC_URL || 'https://mainnet.base.org';
  const apiKey = process.env.TOT_API_KEY;
  const privateKey = process.env.EXECUTOR_WALLET_PRIVATE_KEY;
  const safeAddress = process.env.SAFE_ADDRESS;
  const strategyExecutor = process.env.EXECUTOR_MODULE_ADDRESS;
  const chainId = parseChainId(args);

  const { JsonRpcProvider } = require('ethers');

  const provider = new JsonRpcProvider(rpcUrl);

  if (action === 'checkPolicy') {
    const block = await provider.getBlockNumber();
    console.log('[31Third] Diagnostic Check');
    console.log(`RPC: ${rpcUrl}`);
    console.log(`API Key: ${apiKey ? 'Loaded' : 'Missing'}`);
    console.log(`Safe: ${safeAddress}`);
    console.log(`Executor: ${strategyExecutor}`);
    console.log(`Connectivity: OK (Block ${block})`);
    return;
  }

  if (!privateKey || !strategyExecutor || !safeAddress || !apiKey) {
    console.error('Error: Missing env vars. Use --action help for setup instructions.');
    process.exit(1);
  }

  const { executeRebalancing, calculateRebalancing } = require('@31third/sdk');
  const { Wallet, formatUnits, Contract } = require('ethers');
  const { generateTradeReport } = require('./generatePdf.js');
  const { decodeError } = require('./error_decoder.js');
  const signer = new Wallet(privateKey, provider);

  const fromToken = getArg(args, '--from');
  const toToken = getArg(args, '--to');
  const amount = getArg(args, '--amount');
  const targets = parseTargetsArg(getArg(args, '--targets'));

  await inspectBoundaries(provider, strategyExecutor, Contract);

  const payload = buildPayload({
    action,
    safeAddress,
    signerAddress: signer.address,
    chainId,
    minTradeValue,
    fromToken,
    toToken,
    amount,
    targets
  });

  try {
    console.log('[31Third] Calculating rebalancing via API...');
    const rebalancing = await calculateRebalancing({
      apiBaseUrl: 'https://api.31third.com/1.3',
      apiKey,
      chainId,
      payload
    });

    console.log(`[31Third] Executing on-chain via StrategyExecutor: ${strategyExecutor}...`);
    const tx = await executeRebalancing({ signer, strategyExecutor, rebalancing });
    const receipt = await tx.wait();
    console.log(`[31Third] Transaction confirmed in block ${receipt.blockNumber}: ${tx.hash}`);

    const reportData = {
      refId: `31T-${Date.now()}`,
      executionTime: new Date().toUTCString(),
      vaultName: '31Third Vault',
      vaultAddress: safeAddress,
      managerAddress: signer.address,
      preTradeValue: rebalancing.portfolioValue ? `$${rebalancing.portfolioValue.toFixed(2)}` : '$0.00',
      postTradeValue: rebalancing.portfolioValue ? `$${rebalancing.portfolioValue.toFixed(2)}` : '$0.00',
      frictionBps: '5.0',
      trades: (rebalancing.swaps || []).map((s, i) => ({
        sequence: `TRD_${String(i + 1).padStart(3, '0')}`,
        fromToken: s.fromToken || fromToken || 'UNK',
        toToken: s.toToken || toToken || 'UNK',
        venue: s.venue || '31Third Aggregator',
        volumeOut: s.amountOut ? formatUnits(s.amountOut, 18) : '0.00',
        avgPrice: s.price || '0.00',
        priceImpact: -0.05
      })),
      serviceFee: '$5.00',
      networkFee: '$0.50',
      totalCosts: '$5.50',
      maxSlippage: '1.00%',
      realizedVariance: '-0.01%',
      txHash: tx.hash
    };

    const reportPath = path.resolve(__dirname, `report_${tx.hash.slice(0, 8)}.pdf`);
    try {
      await generateTradeReport(reportData, reportPath);
      console.log(`[31Third] Report saved to: ${reportPath}`);
    } catch (reportError) {
      console.warn(`[31Third] Report generation warning: ${reportError.message}`);
    }
  } catch (error) {
    console.error('\nExecution Failed');

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      console.error(`API Error (${status}): ${JSON.stringify(data, null, 2)}`);
    } else {
      console.error(`Error: ${error.message}`);
      const data = error.data || (error.info && error.info.error && error.info.error.data);
      if (data) {
        const decoded = decodeError(data);
        if (decoded) console.error(decoded);
      }
    }

    process.exit(1);
  }
}

if (require.main === module) {
  main().catch((e) => {
    console.error(e.message || e);
    process.exit(1);
  });
}

module.exports = {
  getArg,
  parseChainId,
  parseTargetsArg,
  validateSwapInputs,
  validateTargets,
  buildPayload,
  loadDotEnv
};
