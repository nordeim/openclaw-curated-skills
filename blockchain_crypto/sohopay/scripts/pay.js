const { ethers } = require('ethers');
const crypto = require('crypto');
require('dotenv').config();

// --- CONFIGURATION ---
const RPC_URL = "https://sepolia.base.org";
const CHAIN_ID = 84532; // Base Sepolia
const USDC_DECIMALS = 6;

const ADDRESSES = {
    creditor: "0x669324C8c8011c3C0cA31faFBdD9C76219C06dB1",
    borrowerManager: "0xFdcb4abf261944383dbac37cB8E9147E50E2a609",
    usdc: "0x08B1797bB535C4cf86f93424137Cb3e004476624",
};

// --- ABIs ---
const CREDITOR_ABI = [
    "function spendWithAuthorization(address,address,address,uint256,uint256,bytes32,uint256,uint256,bytes)"
];
const BORROWER_MANAGER_ABI = [
    "function isBorrowerRegistered(address) view returns (bool)",
    "function isActiveBorrower(address) view returns (bool)",
    "function getAgentSpendLimit(address) view returns (uint256)"
];

async function main() {
    // 1. Load Signer from Environment
    const privateKey = process.env.PRIVATE_KEY || process.env.SOHO_TEST_PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ FATAL: PRIVATE_KEY / SOHO_TEST_PRIVATE_KEY environment variable not set. This skill cannot sign transactions.");
        process.exit(1);
    }

    // 2. Parse Command-Line Arguments
    if (process.argv.length < 4) {
        console.error("❌ USAGE: node pay.js <amount> <merchant_address>");
        process.exit(1);
    }
    const amountString = process.argv[2];
    const merchantInput = process.argv[3];

    if (!ethers.isAddress(merchantInput)) {
        console.error("❌ ERROR: merchant_address must be a valid EVM address (0x...). No name-to-address or random generation is allowed.");
        process.exit(1);
    }

    const amount = ethers.parseUnits(amountString, USDC_DECIMALS);

    // 3. Setup Provider & Wallet
    const provider = new ethers.JsonRpcProvider(RPC_URL);

    // Safety guard: ensure we are on Base Sepolia and never on mainnet
    const network = await provider.getNetwork();
    const chainIdBigInt = network.chainId;

    if (chainIdBigInt === 1n) {
        console.error("❌ FATAL: Connected to Ethereum mainnet. This script is TESTNET ONLY. Aborting.");
        process.exit(1);
    }

    if (chainIdBigInt !== BigInt(CHAIN_ID)) {
        console.error(`❌ FATAL: Unexpected chainId ${chainIdBigInt}. Expected Base Sepolia (${CHAIN_ID}). Aborting.`);
        process.exit(1);
    }

    const wallet = new ethers.Wallet(privateKey, provider);
    const payerAddress = wallet.address;

    // Safety guard: warn if native balance looks too large for a test key
    const nativeBalance = await provider.getBalance(payerAddress);
    const nativeBalanceEth = Number(ethers.formatEther(nativeBalance));
    if (nativeBalanceEth > 0.5) {
        console.warn(`⚠️  WARNING: Signer native balance is ${nativeBalanceEth} ETH-equivalent, which is high for a testnet key. Ensure this is NOT a mainnet or real-funds wallet.`);
    }

    console.log(`--- Initializing SOHO Pay Transaction ---`);
    console.log(`- Signer (PRIVATE_KEY/SOHO_TEST_PRIVATE_KEY): ${payerAddress}`);

    // 4. Merchant Address (explicit only)
    const merchantAddress = merchantInput;
    console.log(`- Merchant (Address): ${merchantAddress}`);
    console.log(`- Amount: ${amountString} USDC (${amount.toString()} atomic units)`);
    console.log(`-------------------------------------------`);

    // 5. Pre-Flight Checks
    console.log("\n🔍 Performing Pre-Flight Checks...");
    const borrowerManager = new ethers.Contract(ADDRESSES.borrowerManager, BORROWER_MANAGER_ABI, provider);

    const isRegistered = await borrowerManager.isBorrowerRegistered(payerAddress);
    const isActive = await borrowerManager.isActiveBorrower(payerAddress);
    const creditLimit = await borrowerManager.getAgentSpendLimit(payerAddress);

    console.log(`- Borrower Registered? ${isRegistered ? '✅ Yes' : '❌ No'}`);
    console.log(`- Borrower Active? ${isActive ? '✅ Yes' : '❌ No'}`);
    console.log(`- Borrower Credit Limit: ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);
    
    if (!isRegistered || !isActive || creditLimit < amount) {
        if (!isRegistered) console.error("\n❌ REASON: Borrower is not registered.");
        if (!isActive) console.error("\n❌ REASON: Borrower is not active.");
        if (creditLimit < amount) console.error(`\n❌ REASON: Credit limit (${ethers.formatUnits(creditLimit, USDC_DECIMALS)}) is less than amount (${amountString}).`);
        console.error("Transaction aborted due to failed pre-flight checks.");
        process.exit(1);
    }
    console.log("✅ All checks passed.");

    // 6. EIP-712 Signing
    const domain = { name: 'CreditContract', version: '1', chainId: CHAIN_ID, verifyingContract: ADDRESSES.creditor };
    const types = {
        SpendWithAuthorization: [
            { name: 'payer', type: 'address' }, { name: 'merchant', type: 'address' },
            { name: 'asset', type: 'address' }, { name: 'amount', type: 'uint256' },
            { name: 'paymentPlanId', type: 'uint256' }, { name: 'nonce', type: 'bytes32' },
            { name: 'validAfter', type: 'uint256' }, { name: 'expiry', type: 'uint256' }
        ]
    };
    const nonce = '0x' + crypto.randomBytes(32).toString('hex');
    const now = Math.floor(Date.now() / 1000);
    const message = {
        payer: payerAddress, merchant: merchantAddress, asset: ADDRESSES.usdc,
        amount: amount, paymentPlanId: 0, nonce: nonce,
        validAfter: now - 60, expiry: now + 600
    };
    
    console.log("\n✍️  Signing EIP-712 message...");
    const signature = await wallet.signTypedData(domain, types, message);

    // 7. Execute Transaction
    const creditorContract = new ethers.Contract(ADDRESSES.creditor, CREDITOR_ABI, wallet);
    try {
        console.log("\n🚀 Submitting transaction to the blockchain...");
        const tx = await creditorContract.spendWithAuthorization(
            message.payer, message.merchant, message.asset, message.amount,
            message.paymentPlanId, message.nonce, message.validAfter, message.expiry,
            signature
        );
        console.log(`\n✅ Transaction sent! Hash: ${tx.hash}`);
        console.log(`Waiting for confirmation...`);
        const receipt = await tx.wait();
        console.log(`\n🎉 Transaction confirmed in block: ${receipt.blockNumber}`);
    } catch (error) {
        console.error("\n❌ On-Chain Transaction Failed:", error.reason || error.message);
        process.exit(1);
    }
}

main();
