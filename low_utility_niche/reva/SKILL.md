---
name: payid
description: Complete Reva wallet management - passwordless authentication, PayID name claiming, multi-chain crypto transfers to PayIDs or wallet addresses, balance tracking across networks, account details information, and deposit management
---

# Reva

**Passwordless authentication and wallet management for Reva users.**

Reva provides a simple way to authenticate users, claim unique PayID names, and manage cryptocurrency balances. All authentication is passwordless using email-based OTP verification.

## Authentication

Reva uses a passwordless authentication flow. Users receive a one-time password (OTP) via email, verify it, and receive an access token for subsequent operations.

### Login/Register Flow

There is no difference between registration and login - both use the same passwordless flow:

1. User provides their email address
2. System sends OTP to the email
3. User provides the OTP code
4. System verifies OTP and returns access token
5. Access token is stored securely for future operations

**The access token MUST be stored securely after verification and reused for all protected operations.**

## Available Commands

### 1. Login or Register

**Triggers:** When user wants to login, register, sign in, sign up, authenticate, or access Reva

**Process:**

1. Ask user for their email address if not provided
2. Call the authentication script to send OTP: `{baseDir}/scripts/send-otp.sh <email>`
3. Inform user that OTP has been sent to their email
4. Ask user to provide the OTP code they received
5. Call the verification script: `{baseDir}/scripts/verify-otp.sh <email> <otp>`
6. If successful, inform user they are now authenticated
7. The access token is automatically stored for future use

### 2. Claim PayID

**Triggers:** When user wants to claim a PayID, get a PayID name, register a PayID, or set their PayID

**Requirements:** User must be authenticated first (have valid access token)

**Process:**

1. Check if user is authenticated by calling: `{baseDir}/scripts/check-auth.sh`
2. If not authenticated, prompt user to login first
3. Ask user for their desired PayID name if not provided
4. Call the claim script: `{baseDir}/scripts/claim-payid.sh <desired_payid>`
5. Handle response:
   - Success: Inform user their PayID was claimed successfully
   - Already taken: Inform user the PayID is taken and ask for another choice
   - Invalid format: Explain format requirements and ask again
   - Unauthorized: Token expired, ask user to login again

### 3. View Balance

**Triggers:** When user wants to check balance, see wallet balance, view funds, or check how much money they have

**Requirements:** User must be authenticated first (have valid access token)

**Process:**

1. Check if user is authenticated by calling: `{baseDir}/scripts/check-auth.sh`
2. If not authenticated, prompt user to login first
3. Call the balance script: `{baseDir}/scripts/get-balance.sh`
4. Display the balance to user in a friendly format showing each token with its amount, symbol, and chain (network)
5. If unauthorized error, token expired - ask user to login again

**Display Format Example:**

```
Your current balance:
- 0.001016 ETH on Base
- 1.97 USDC on Base
- 1.21 USDT on BNB Smart Chain
- 0.80 USDC on BNB Smart Chain
- 0.00088 BNB on BNB Smart Chain
```

### 4. Get User Information

**Triggers:** When user asks about their account details, PayID, wallet address, email, referral code, cashback points, connected Twitter, avatar, or wants to deposit funds

**Requirements:** User must be authenticated first (have valid access token)

**Process:**

1. Check if user is authenticated by calling: `{baseDir}/scripts/check-auth.sh`
2. If not authenticated, prompt user to login first
3. Call the user info script: `{baseDir}/scripts/get-user-info.sh`
4. Extract and display the relevant information the user asked for:
   - **PayID**: Show from `payId` field
   - **Wallet Address**: Show from `walletAddress` field
   - **Email**: Show from `email` field
   - **Referral Code**: Show from `referralCode` field
   - **Cashback Points**: Show from `cashbackPoints` field
   - **Connected Twitter**: Show from `twitter` field
   - **Avatar**: Show from `avatarUrl` field
   - **Transaction Limit**: Show `transactionLimit` and `transactionUsed`
5. If user wants to deposit funds, provide their wallet address and instruct them to send funds to it

**Important for Deposits:** When user asks to deposit, simply provide their wallet address from the `/api/users/me` response and tell them to send funds to that address.

### 5. Send Funds

**Triggers:** When user wants to send money, send funds, send crypto, transfer tokens, or pay someone

**Requirements:** User must be authenticated first (have valid access token)

**Process:**

**CRITICAL: You must act as a message forwarder. Take the user's message EXACTLY as they say it and forward it to the Reva AI endpoint. Do NOT parse or interpret the message yourself. Let the Reva AI handle all the logic.**

1. Check if user is authenticated by calling: `{baseDir}/scripts/check-auth.sh`
2. If not authenticated, prompt user to login first
3. Forward the user's EXACT message to: `{baseDir}/scripts/send-message.sh "<user_message>"`
4. Display the response from Reva AI to the user
5. If Reva AI asks for more information (network, token, amount), continue forwarding user responses using the same script
6. The script automatically manages the `roomId` to maintain conversation context
7. When transaction is complete, display the transaction link and share link if provided

**Message Forwarding Examples:**

- User: "send 0.01 usdt on bnb to aldo"
  → Forward: `send-message.sh "send 0.01 usdt on bnb to aldo"`

- User: "can you send some funds to aldo?"
  → Forward: `send-message.sh "can you send some funds to aldo?"`
  → Reva AI Response: "got it - to aldo. which network? (eth, pol, op, bnb, or base)"
  → User: "lets do bnb"
  → Forward: `send-message.sh "lets do bnb"` (uses same roomId automatically)
  → Continue until complete

**Important Notes:**

- The `roomId` is automatically managed across the conversation session
- Each follow-up message reuses the same `roomId` to maintain context
- Only forward messages that are about sending funds/money/crypto
- Do NOT forward general questions or other commands
- If the conversation is finished or user changes topic, the room state persists until a new send transaction starts

**To Clear Room State (optional):**
If you need to start a fresh conversation context, call: `{baseDir}/scripts/clear-room.sh`

## Error Handling

### Token Expiration

If any protected operation returns an unauthorized error, the access token has expired. Inform the user and ask them to login again.

### Rate Limiting

If OTP request fails due to rate limiting, inform user to wait before trying again.

### Network Errors

If scripts fail due to network issues, inform user and suggest trying again.

### Invalid Input

Validate email format before sending requests. PayID format should be alphanumeric with optional underscores/hyphens.

## Security Notes

- Access tokens are stored in encrypted storage at `~/.openclaw/payid/auth.json`
- Never log or display access tokens to the user
- OTP codes should only be entered once and never stored
- Always use HTTPS for API requests (enforced in scripts)

## Script Reference

All scripts are located in `{baseDir}/scripts/`:

- `send-otp.sh <email>` - Send OTP to email
- `verify-otp.sh <email> <otp>` - Verify OTP and get access token
- `claim-payid.sh <payid>` - Claim a PayID name
- `get-balance.sh` - Get wallet balance with all tokens across chains
- `get-user-info.sh` - Get current logged user information
- `send-message.sh "<message>"` - Forward message to Reva AI for sending funds
- `clear-room.sh` - Clear room state for fresh conversation
- `check-auth.sh` - Check if user is authenticated

## Common Workflows

### First Time User

1. User asks to login or register
2. User provides email
3. System sends OTP
4. User provides OTP code
5. User is authenticated
6. User can now claim PayID or check balance

### Claim PayID

1. User asks to claim a PayID
2. Check authentication status
3. User provides desired payid name
4. System attempts to claim
5. Success or ask for alternative if taken

### Check Balance

1. User asks for balance
2. Check authentication status
3. Display current balance

### Get Account Info

1. User asks about their PayID, wallet address, referral code, etc.
2. Check authentication status
3. Fetch user info from `/api/users/me`
4. Display the requested information

### Deposit Funds

1. User asks how to deposit
2. Check authentication status
3. Get wallet address from user info
4. Provide wallet address for deposits

### Send Funds (Simple)

1. User: "send 0.01 usdt on bnb to aldo"
2. Forward message to Reva AI
3. Reva AI processes and sends funds
4. Display transaction confirmation with links

### Send Funds (Multi-Step)

1. User: "send some funds to aldo"
2. Forward to Reva AI
3. Reva AI: "which network?"
4. User: "bnb"
5. Forward to Reva AI (same room)
6. Reva AI: "which token?"
7. User: "0.01 usdt"
8. Forward to Reva AI (same room)
9. Transaction complete with confirmation

## API Endpoints

### Login (Send OTP)

- **Method**: POST
- **Path**: `/api/openclaw/login`
- **Body**: `{"email": "user@example.com"}`
- **Response**: `{"success": true, "message": "OTP sent to your email"}`

### Verify OTP

- **Method**: POST
- **Path**: `/api/openclaw/verify`
- **Body**: `{"email": "user@example.com", "otp": "123456"}`
- **Response**: `{"success": true, "token": "jwt_token", "user": {...}}`

### Get Balance

- **Method**: GET
- **Path**: `/api/wallet?isForceUpdateWallet=true`
- **Header**: `openclaw-token: <token>`
- **Response**: `{"success": true, "tokens": [{"name": "...", "symbol": "...", "balance": ..., "chain": "..."}]}`

### Claim PayID

- **Method**: POST
- **Path**: `/api/payid/register`
- **Header**: `openclaw-token: <token>`
- **Body**: `{"payIdName": "payid_name"}`
- **Response**: `{"success": true, "data": {...}}`

### Get User Info

- **Method**: GET
- **Path**: `/api/users/me`
- **Header**: `openclaw-token: <token>`
- **Response**: `{"user": {"id": "...", "email": "...", "payId": "...", "walletAddress": "...", "referralCode": "...", "cashbackPoints": ..., "twitter": "...", ...}}`

### Send Message (Forward to Reva AI)

- **Method**: POST
- **Path**: `/api/message/create-message`
- **Header**: `openclaw-token: <token>`
- **Body**: `{"message": "user message text", "roomId": "optional-room-id or null"}`
- **Response**: `{"success": true, "data": {"roomCreated": {"roomId": "..."}, "messages": [{...}]}}`

## Tips

- Always check authentication before performing protected operations
- Display all token balances with their respective chains for clarity
- For deposits, simply provide the user's wallet address from `/api/users/me`
- **CRITICAL for sending funds**: Act as a pure message forwarder - send user's exact message to Reva AI without parsing
- The `roomId` is automatically managed for multi-step send fund conversations
- When user asks about account details (PayID, wallet, referral code, etc.), fetch from `/api/users/me`
- Provide clear error messages based on API responses
- Guide users through the authentication flow step-by-step
- Suggest alternative PayIDs if the desired one is taken
- Display transaction links when funds are sent successfully
