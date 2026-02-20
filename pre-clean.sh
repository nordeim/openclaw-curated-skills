egrep -i 'token|blockchain|ETH|USDC|Solana|DeFi|NFT|smart contract|crypto|cryptocurrency|wallet|coin|mainnet|testnet|ERC-20|erc20|perp|perps|DEX|AMM|liquidity|yield|staking|borrowing|lending|vault|prediction market|polymarket' */*/SKILL.md | sed 's/\/.*$//' | sort | uniq | sed 's/^/rm -rf /' > kk1

chmod +x kk1 && ./kk1

rm kk?
