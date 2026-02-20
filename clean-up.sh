egrep -i 'token|blockchain|ETH|USDC|Solana|DeFi|NFT|smart contract|crypto|cryptocurrency|wallet|coin|mainnet|testnet|ERC-20|erc20|perp|perps|DEX|AMM|liquidity|yield|staking|borrowing|lending|vault|prediction market|polymarket' */SKILL.md | sed 's/\/.*$//' | sort | uniq | sed 's/^/rm -rf /' > kk1

chmod +x kk1 && ./kk1

rm kk?

cat suspicious_list.txt | sed 's/\/.*$//' | sort | uniq | sed 's/^/rm -rf /' > kk1

chmod +x kk1 && ./kk1

rm kk?
rm suspicious_list.txt
grep '^description: ' */SKILL.md > description.md

ls -l ../todo.txt && rm todo.txt

