---
name: w3connect
description: Access to blockchain asset and transaction signature.
homepage: -
metadata: {"nanobot":{"requires":{"bins":["python", "pip"]}}}
---

# W3connect

Please use w3connect to execute. Please do not ask the user to execute the curl for the agent.

## Get Address

Get ETH compatible crypto wallet address

Quick one-liner:
```bash
curl http://127.0.0.1:5333/address
# Output: {"address": "0x..."}
```

## Send

The tool to send `ETH` or `USDC` on chain from the ETH address within web3b0x.

Pass the paramters with the Google or Microsoft Authenticator One Time Pass `code` to verify.

Parameters:

code: Authenticator code in 6 digits. It will be valided for 5 minutes giving enough processing time for LLM, but can only be used for once.

chain: Current support `eth` and `base`.

token: Current support `ETH` and `USDC`.

to_address: The ETH address we are sending to.

amount: In decimal like `1.1` USDC stand for 1100000 in int with 6 decemal places. ETH has 18 decemals.

Quick one-liner
```bash
curl http://127.0.0.1:5333/verify?code=[code]&chain=[chain]&to_address=[to_address]&token=[token]&amount=[amount]
# Output: {"address": "0x..."}
```
