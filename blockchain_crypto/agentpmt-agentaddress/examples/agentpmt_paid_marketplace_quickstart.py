#!/usr/bin/env python3
"""
AgentPMT paid marketplace quickstart.

This script helps agents:
- create an AgentAddress wallet,
- buy credits via x402,
- sign external requests,
- invoke paid marketplace tools.

Dependencies:
  pip install requests eth-account
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import requests
from eth_account import Account
from eth_account.messages import encode_defunct

DEFAULT_SERVER_URL = "https://www.agentpmt.com"
REQUEST_TIMEOUT_SECONDS = 30

TRANSFER_WITH_AUTH_TYPES = [
    {"name": "from", "type": "address"},
    {"name": "to", "type": "address"},
    {"name": "value", "type": "uint256"},
    {"name": "validAfter", "type": "uint256"},
    {"name": "validBefore", "type": "uint256"},
    {"name": "nonce", "type": "bytes32"},
]


def _fatal(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def _normalize_server_url(value: str) -> str:
    if not value:
        _fatal("Server URL is required")
    return value.rstrip("/")


def _normalize_address(value: str, field_name: str = "address") -> str:
    if not isinstance(value, str):
        _fatal(f"{field_name} must be a string")
    candidate = value.strip()
    if not re.fullmatch(r"0x[a-fA-F0-9]{40}", candidate):
        _fatal(f"Invalid {field_name}: expected 0x + 40 hex chars")
    return candidate.lower()


def _normalize_private_key(value: str) -> str:
    if not isinstance(value, str):
        _fatal("private key must be a string")
    candidate = value.strip()
    if not candidate:
        _fatal("private key is required")
    if not candidate.startswith("0x"):
        candidate = f"0x{candidate}"
    if not re.fullmatch(r"0x[a-fA-F0-9]{64}", candidate):
        _fatal("Invalid private key: expected 0x + 64 hex chars")
    return candidate


def _assert_key_matches_wallet(address: str, private_key: str) -> None:
    try:
        derived = Account.from_key(private_key).address.lower()
    except Exception as exc:  # pragma: no cover - defensive
        _fatal(f"Failed to derive address from private key: {exc}")

    if derived != address:
        _fatal(
            "Private key does not match wallet address "
            f"(derived {derived}, provided {address})"
        )


def _request_json(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    extra_headers: dict[str, str] | None = None,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
) -> requests.Response:
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    try:
        return requests.request(method=method, url=url, json=body, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        _fatal(f"HTTP request failed: {exc}")
    raise AssertionError("unreachable")


def _request_get(
    url: str,
    extra_headers: dict[str, str] | None = None,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
) -> requests.Response:
    headers: dict[str, str] = {
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    try:
        return requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        _fatal(f"HTTP request failed: {exc}")
    raise AssertionError("unreachable")


def _response_payload(response: requests.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=False))


def _decode_base64_json(value: str) -> dict[str, Any]:
    padded = value + ("=" * (-len(value) % 4))
    try:
        decoded = base64.b64decode(padded)
        data = json.loads(decoded.decode("utf-8"))
    except Exception as exc:
        _fatal(f"Failed to decode base64 JSON: {exc}")

    if not isinstance(data, dict):
        _fatal("Decoded base64 payload must be a JSON object")
    return data


def _parse_chain_id(network: str) -> int:
    candidate = network.strip().lower()
    if candidate.startswith("eip155:"):
        candidate = candidate.split(":", 1)[1]
    try:
        return int(candidate)
    except ValueError:
        _fatal(f"Unsupported network format: {network}")
    raise AssertionError("unreachable")


def _canonical_json(value: Any) -> str:
    payload = value if value is not None else {}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _build_external_sign_message(
    wallet: str,
    session_nonce: str,
    request_id: str,
    action: str,
    product_id: str,
    payload_hash: str,
) -> str:
    return "\n".join(
        [
            "agentpmt-external",
            f"wallet:{wallet}",
            f"session:{session_nonce}",
            f"request:{request_id}",
            f"action:{action}",
            f"product:{product_id}",
            f"payload:{payload_hash}",
        ]
    )


def _sign_personal_message(private_key: str, message: str) -> str:
    signed = Account.sign_message(encode_defunct(text=message), private_key=private_key)
    signature = signed.signature.hex()
    return signature if signature.startswith("0x") else f"0x{signature}"


def _sign_transfer_with_authorization(
    private_key: str,
    domain_data: dict[str, Any],
    message_data: dict[str, Any],
) -> str:
    if not hasattr(Account, "sign_typed_data"):
        _fatal("eth-account version does not support typed-data signing. Upgrade to >=0.11.0")

    signed = Account.sign_typed_data(
        private_key,
        domain_data,
        {"TransferWithAuthorization": TRANSFER_WITH_AUTH_TYPES},
        message_data,
    )
    signature = signed.signature.hex()
    return signature if signature.startswith("0x") else f"0x{signature}"


def _load_parameters(args: argparse.Namespace) -> dict[str, Any]:
    if args.parameters_json and args.parameters_file:
        _fatal("Use either --parameters-json or --parameters-file, not both")

    if args.parameters_json:
        try:
            data = json.loads(args.parameters_json)
        except json.JSONDecodeError as exc:
            _fatal(f"--parameters-json is invalid JSON: {exc}")
    elif args.parameters_file:
        try:
            data = json.loads(Path(args.parameters_file).read_text(encoding="utf-8"))
        except FileNotFoundError:
            _fatal(f"Parameters file not found: {args.parameters_file}")
        except json.JSONDecodeError as exc:
            _fatal(f"Parameters file is invalid JSON: {exc}")
    else:
        data = {}

    if not isinstance(data, dict):
        _fatal("parameters must be a JSON object")
    return data


def _create_wallet(server_url: str) -> dict[str, Any]:
    response = _request_json("POST", f"{server_url}/api/external/agentaddress", body={})
    payload = _response_payload(response)

    if not response.ok:
        _fatal(f"Wallet creation failed ({response.status_code}): {payload}")
    if not isinstance(payload, dict):
        _fatal("Unexpected wallet response format")

    data = payload.get("data") if isinstance(payload.get("data"), dict) else None
    if not data:
        _fatal("Wallet response missing data object")

    address = _normalize_address(str(data.get("evmAddress") or ""), "evmAddress")
    private_key = _normalize_private_key(str(data.get("evmPrivateKey") or ""))
    mnemonic = str(data.get("mnemonic") or "")
    if not mnemonic:
        _fatal("Wallet response missing mnemonic")

    _assert_key_matches_wallet(address, private_key)

    return {
        "address": address,
        "private_key": private_key,
        "mnemonic": mnemonic,
        "raw": payload,
    }


def _resolve_wallet_with_key(
    args: argparse.Namespace,
    server_url: str,
) -> tuple[str, str, dict[str, Any] | None]:
    wallet_created: dict[str, Any] | None = None

    if getattr(args, "create_wallet", False):
        wallet_created = _create_wallet(server_url)
        return wallet_created["address"], wallet_created["private_key"], wallet_created

    address_raw = args.address or os.getenv("AGENT_ADDRESS")
    if not address_raw:
        _fatal("wallet address is required (use --address or AGENT_ADDRESS)")

    key_raw = args.key or os.getenv("AGENT_KEY")
    if not key_raw:
        _fatal("private key is required (use --key or AGENT_KEY)")

    address = _normalize_address(address_raw, "wallet address")
    private_key = _normalize_private_key(key_raw)
    _assert_key_matches_wallet(address, private_key)
    return address, private_key, wallet_created


def _resolve_wallet_no_key(args: argparse.Namespace) -> str:
    address_raw = args.address or os.getenv("AGENT_ADDRESS")
    if not address_raw:
        _fatal("wallet address is required (use --address or AGENT_ADDRESS)")
    return _normalize_address(address_raw, "wallet address")


def _create_session_nonce(server_url: str, wallet: str) -> dict[str, Any]:
    response = _request_json(
        "POST",
        f"{server_url}/api/external/auth/session",
        {"wallet_address": wallet},
    )
    payload = _response_payload(response)

    if not response.ok:
        _fatal(f"Session creation failed ({response.status_code}): {payload}")

    if not isinstance(payload, dict):
        _fatal("Unexpected session response format")

    session_nonce = payload.get("session_nonce")
    if not isinstance(session_nonce, str) or not session_nonce.strip():
        _fatal("Session response missing session_nonce")

    return payload


def _sign_external_request(
    wallet: str,
    private_key: str,
    session_nonce: str,
    request_id: str,
    action: str,
    product_id: str,
    payload_for_hash: dict[str, Any] | None,
    force_payload_hash: str | None = None,
) -> dict[str, Any]:
    payload_hash = force_payload_hash
    if payload_hash is None:
        payload_hash = hashlib.sha256(_canonical_json(payload_for_hash).encode("utf-8")).hexdigest()

    message = _build_external_sign_message(
        wallet=wallet,
        session_nonce=session_nonce,
        request_id=request_id,
        action=action,
        product_id=product_id,
        payload_hash=payload_hash,
    )
    signature = _sign_personal_message(private_key, message)

    return {
        "request_id": request_id,
        "payload_hash": payload_hash,
        "message": message,
        "signature": signature,
    }


def _fetch_tools(server_url: str) -> dict[str, Any]:
    response = _request_get(f"{server_url}/api/external/tools")
    payload = _response_payload(response)
    if not response.ok:
        _fatal(f"Failed to fetch tools ({response.status_code}): {payload}")
    if not isinstance(payload, dict):
        _fatal("Unexpected tools response format")
    return payload


def _buy_credits_x402(
    server_url: str,
    wallet: str,
    private_key: str,
    credits: int,
    request_id: str | None = None,
    validity_seconds: int = 1800,
    submit: bool = True,
) -> dict[str, Any]:
    if credits <= 0:
        _fatal("credits must be a positive integer")
    if credits % 500 != 0:
        _fatal("credits must be purchased in 500-credit increments")

    request_id_value = request_id or f"purchase-{uuid.uuid4()}"
    body = {
        "wallet_address": wallet,
        "credits": int(credits),
        "payment_method": "x402",
        "request_id": request_id_value,
    }

    init_response = _request_json(
        "POST",
        f"{server_url}/api/external/credits/purchase",
        body,
    )

    if init_response.status_code != 402:
        payload = _response_payload(init_response)
        _fatal(
            "Expected 402 Payment Required from /api/external/credits/purchase "
            f"but got {init_response.status_code}: {payload}"
        )

    payment_required_header = (
        init_response.headers.get("PAYMENT-REQUIRED")
        or init_response.headers.get("payment-required")
    )
    if not payment_required_header:
        _fatal("Missing PAYMENT-REQUIRED header in 402 response")

    payment_required = _decode_base64_json(payment_required_header)
    accepts = payment_required.get("accepts")
    if not isinstance(accepts, list) or not accepts:
        _fatal("PAYMENT-REQUIRED.accepts is missing or empty")

    acceptance = accepts[0]
    if not isinstance(acceptance, dict):
        _fatal("PAYMENT-REQUIRED.accepts[0] must be an object")

    network = str(acceptance.get("network") or "").strip()
    amount = acceptance.get("amount")
    asset = str(acceptance.get("asset") or "").strip()
    pay_to = str(acceptance.get("payTo") or "").strip()
    if not network or amount is None or not asset or not pay_to:
        _fatal("PAYMENT-REQUIRED accept object missing network/amount/asset/payTo")

    chain_id = _parse_chain_id(network)
    asset_address = _normalize_address(asset, "asset address")
    pay_to_address = _normalize_address(pay_to, "payTo address")

    extra = acceptance.get("extra") if isinstance(acceptance.get("extra"), dict) else {}
    domain_name = str(extra.get("name") or "USDC")
    domain_version = str(extra.get("version") or "2")

    valid_after = 0
    valid_before = int(time.time()) + int(validity_seconds)
    nonce = f"0x{os.urandom(32).hex()}"
    value_int = int(str(amount))

    domain_data = {
        "name": domain_name,
        "version": domain_version,
        "chainId": chain_id,
        "verifyingContract": asset_address,
    }
    message_for_signing = {
        "from": wallet,
        "to": pay_to_address,
        "value": value_int,
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce,
    }
    typed_signature = _sign_transfer_with_authorization(
        private_key=private_key,
        domain_data=domain_data,
        message_data=message_for_signing,
    )

    authorization_payload = {
        "from": wallet,
        "to": pay_to_address,
        "value": str(value_int),
        "validAfter": str(valid_after),
        "validBefore": str(valid_before),
        "nonce": nonce,
    }

    payment_signature_payload = {
        "x402Version": 2,
        "scheme": "exact",
        "network": network,
        "payload": {
            "signature": typed_signature,
            "authorization": authorization_payload,
        },
    }

    payment_signature_header = base64.b64encode(
        json.dumps(payment_signature_payload, separators=(",", ":")).encode("utf-8")
    ).decode("utf-8")

    output: dict[str, Any] = {
        "request_body": body,
        "payment_required": payment_required,
        "authorization": {
            **authorization_payload,
            "signature": typed_signature,
        },
        "payment_signature_header": payment_signature_header,
        "submit_result": None,
    }

    if submit:
        submit_response = _request_json(
            "POST",
            f"{server_url}/api/external/credits/purchase",
            body,
            extra_headers={"PAYMENT-SIGNATURE": payment_signature_header},
            timeout=120,
        )
        output["submit_result"] = {
            "status_code": submit_response.status_code,
            "ok": submit_response.ok,
            "response": _response_payload(submit_response),
        }

    return output


def _invoke_tool_signed(
    server_url: str,
    wallet: str,
    private_key: str,
    session_nonce: str,
    product_id: str,
    parameters: dict[str, Any],
    request_id: str | None = None,
) -> dict[str, Any]:
    normalized_product_id = (product_id or "").strip()
    if not normalized_product_id:
        _fatal("product_id is required")

    request_id_value = request_id or f"invoke-{uuid.uuid4()}"
    signed = _sign_external_request(
        wallet=wallet,
        private_key=private_key,
        session_nonce=session_nonce,
        request_id=request_id_value,
        action="invoke",
        product_id=normalized_product_id,
        payload_for_hash=parameters,
    )

    body = {
        "wallet_address": wallet,
        "session_nonce": session_nonce,
        "request_id": request_id_value,
        "signature": signed["signature"],
        "parameters": parameters,
    }

    response = _request_json(
        "POST",
        f"{server_url}/api/external/tools/{normalized_product_id}/invoke",
        body,
        timeout=120,
    )

    return {
        "signed": signed,
        "request_body": body,
        "response": {
            "status_code": response.status_code,
            "ok": response.ok,
            "payload": _response_payload(response),
        },
    }


def _check_balance_signed(
    server_url: str,
    wallet: str,
    private_key: str,
    session_nonce: str,
    request_id: str | None = None,
) -> dict[str, Any]:
    request_id_value = request_id or f"balance-{uuid.uuid4()}"
    signed = _sign_external_request(
        wallet=wallet,
        private_key=private_key,
        session_nonce=session_nonce,
        request_id=request_id_value,
        action="balance",
        product_id="-",
        payload_for_hash=None,
        force_payload_hash="",
    )

    body = {
        "wallet_address": wallet,
        "session_nonce": session_nonce,
        "request_id": request_id_value,
        "signature": signed["signature"],
    }

    response = _request_json(
        "POST",
        f"{server_url}/api/external/credits/balance",
        body,
        timeout=120,
    )

    return {
        "signed": signed,
        "request_body": body,
        "response": {
            "status_code": response.status_code,
            "ok": response.ok,
            "payload": _response_payload(response),
        },
    }


def _wallet_summary(wallet_created: dict[str, Any] | None, include_secrets: bool) -> dict[str, Any] | None:
    if wallet_created is None:
        return None

    if include_secrets:
        return {
            "address": wallet_created["address"],
            "private_key": wallet_created["private_key"],
            "mnemonic": wallet_created["mnemonic"],
        }

    return {
        "address": wallet_created["address"],
        "private_key": "<hidden>",
        "mnemonic": "<hidden>",
        "note": "Use --show-secrets if you explicitly want private key/mnemonic in output.",
    }


def _cmd_wallet_create(args: argparse.Namespace) -> None:
    server_url = _normalize_server_url(args.server)
    wallet = _create_wallet(server_url)

    output = {
        "wallet": _wallet_summary(wallet, include_secrets=bool(args.show_secrets)),
        "warning": "Store private_key and mnemonic securely. They are not recoverable from AgentPMT.",
    }
    _print_json(output)


def _cmd_buy_credits(args: argparse.Namespace) -> None:
    server_url = _normalize_server_url(args.server)
    wallet, private_key, wallet_created = _resolve_wallet_with_key(args, server_url)

    purchase = _buy_credits_x402(
        server_url=server_url,
        wallet=wallet,
        private_key=private_key,
        credits=int(args.credits),
        request_id=args.request_id,
        validity_seconds=int(args.validity_seconds),
        submit=not bool(args.no_submit),
    )

    output = {
        "wallet": _wallet_summary(wallet_created, include_secrets=bool(args.show_secrets)),
        "purchase": purchase,
    }
    _print_json(output)


def _cmd_invoke_e2e(args: argparse.Namespace) -> None:
    server_url = _normalize_server_url(args.server)
    wallet, private_key, wallet_created = _resolve_wallet_with_key(args, server_url)
    parameters = _load_parameters(args)

    session = _create_session_nonce(server_url, wallet)
    session_nonce = str(session.get("session_nonce") or "")
    if not session_nonce:
        _fatal("Session response missing session_nonce")

    invoke = _invoke_tool_signed(
        server_url=server_url,
        wallet=wallet,
        private_key=private_key,
        session_nonce=session_nonce,
        product_id=args.product_id,
        parameters=parameters,
        request_id=args.request_id,
    )

    balance = None
    if args.check_balance:
        balance = _check_balance_signed(
            server_url=server_url,
            wallet=wallet,
            private_key=private_key,
            session_nonce=session_nonce,
        )

    output = {
        "wallet": _wallet_summary(wallet_created, include_secrets=bool(args.show_secrets)),
        "session": session,
        "invoke": invoke,
        "balance": balance,
    }
    _print_json(output)


def _cmd_market_e2e(args: argparse.Namespace) -> None:
    server_url = _normalize_server_url(args.server)
    wallet, private_key, wallet_created = _resolve_wallet_with_key(args, server_url)
    parameters = _load_parameters(args)

    tools_payload = _fetch_tools(server_url)
    tools_list = tools_payload.get("tools") if isinstance(tools_payload.get("tools"), list) else []

    selected_tool = None
    for tool in tools_list:
        if not isinstance(tool, dict):
            continue
        if str(tool.get("product_id") or "").strip() == str(args.product_id).strip():
            selected_tool = tool
            break

    purchase_result = None
    if not args.skip_purchase:
        purchase_result = _buy_credits_x402(
            server_url=server_url,
            wallet=wallet,
            private_key=private_key,
            credits=int(args.credits),
            request_id=f"purchase-{uuid.uuid4()}",
            validity_seconds=int(args.validity_seconds),
            submit=True,
        )

    session = _create_session_nonce(server_url, wallet)
    session_nonce = str(session.get("session_nonce") or "")
    if not session_nonce:
        _fatal("Session response missing session_nonce")

    invoke = _invoke_tool_signed(
        server_url=server_url,
        wallet=wallet,
        private_key=private_key,
        session_nonce=session_nonce,
        product_id=args.product_id,
        parameters=parameters,
        request_id=f"invoke-{uuid.uuid4()}",
    )

    balance = _check_balance_signed(
        server_url=server_url,
        wallet=wallet,
        private_key=private_key,
        session_nonce=session_nonce,
        request_id=f"balance-{uuid.uuid4()}",
    )

    output = {
        "wallet": _wallet_summary(wallet_created, include_secrets=bool(args.show_secrets)),
        "marketplace": {
            "tools_count": len(tools_list),
            "selected_tool": selected_tool,
        },
        "purchase": purchase_result,
        "session": session,
        "invoke": invoke,
        "balance": balance,
    }
    _print_json(output)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AgentPMT paid marketplace quickstart",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Environment variables supported:\n"
            "  AGENT_ADDRESS=0x...\n"
            "  AGENT_KEY=0x...\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    wallet_create = subparsers.add_parser("wallet-create", help="Create a new AgentAddress wallet")
    wallet_create.add_argument("--server", default=DEFAULT_SERVER_URL, help="AgentPMT base URL")
    wallet_create.add_argument("--show-secrets", action="store_true", help="Include private key and mnemonic in output")
    wallet_create.set_defaults(func=_cmd_wallet_create)

    buy_credits = subparsers.add_parser("buy-credits", help="Buy credits with x402")
    buy_credits.add_argument("--server", default=DEFAULT_SERVER_URL, help="AgentPMT base URL")
    buy_credits.add_argument("--address", help="Wallet address (or AGENT_ADDRESS)")
    buy_credits.add_argument("--key", help="Private key (or AGENT_KEY)")
    buy_credits.add_argument("--create-wallet", action="store_true", help="Create wallet first and use it")
    buy_credits.add_argument("--show-secrets", action="store_true", help="Include private key and mnemonic in output")
    buy_credits.add_argument("--credits", type=int, required=True, help="Credits to buy (500-credit increments)")
    buy_credits.add_argument("--request-id", help="Optional request id")
    buy_credits.add_argument("--validity-seconds", type=int, default=1800, help="x402 authorization validity window")
    buy_credits.add_argument("--no-submit", action="store_true", help="Only generate PAYMENT-SIGNATURE; do not submit purchase")
    buy_credits.set_defaults(func=_cmd_buy_credits)

    invoke_e2e = subparsers.add_parser(
        "invoke-e2e",
        help="Create session -> sign invoke -> POST invoke",
    )
    invoke_e2e.add_argument("--server", default=DEFAULT_SERVER_URL, help="AgentPMT base URL")
    invoke_e2e.add_argument("--address", help="Wallet address (or AGENT_ADDRESS)")
    invoke_e2e.add_argument("--key", help="Private key (or AGENT_KEY)")
    invoke_e2e.add_argument("--create-wallet", action="store_true", help="Create wallet first and use it")
    invoke_e2e.add_argument("--show-secrets", action="store_true", help="Include private key and mnemonic in output")
    invoke_e2e.add_argument("--product-id", required=True, help="Product ID to invoke")
    invoke_e2e.add_argument("--request-id", help="Optional request id")
    invoke_e2e.add_argument("--parameters-json", help="Inline JSON object for parameters")
    invoke_e2e.add_argument("--parameters-file", help="Path to JSON file for parameters")
    invoke_e2e.add_argument("--check-balance", action="store_true", help="Also run signed balance check after invoke")
    invoke_e2e.set_defaults(func=_cmd_invoke_e2e)

    market_e2e = subparsers.add_parser(
        "market-e2e",
        help="One command marketplace flow: list tools -> buy credits -> session -> invoke -> balance",
    )
    market_e2e.add_argument("--server", default=DEFAULT_SERVER_URL, help="AgentPMT base URL")
    market_e2e.add_argument("--address", help="Wallet address (or AGENT_ADDRESS)")
    market_e2e.add_argument("--key", help="Private key (or AGENT_KEY)")
    market_e2e.add_argument("--create-wallet", action="store_true", help="Create wallet first and use it")
    market_e2e.add_argument("--show-secrets", action="store_true", help="Include private key and mnemonic in output")
    market_e2e.add_argument("--product-id", required=True, help="Paid marketplace product ID")
    market_e2e.add_argument("--credits", type=int, default=500, help="Credits to buy before invoke")
    market_e2e.add_argument("--skip-purchase", action="store_true", help="Skip credit purchase and just invoke")
    market_e2e.add_argument("--validity-seconds", type=int, default=1800, help="x402 authorization validity window")
    market_e2e.add_argument("--parameters-json", help="Inline JSON object for parameters")
    market_e2e.add_argument("--parameters-file", help="Path to JSON file for parameters")
    market_e2e.set_defaults(func=_cmd_market_e2e)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
