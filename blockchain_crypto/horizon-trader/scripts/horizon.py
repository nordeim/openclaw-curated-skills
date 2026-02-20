#!/usr/bin/env python3
"""OpenClaw CLI entry point for Horizon SDK.

Usage: python3 horizon.py <command> [args...]

All output is JSON printed to stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys

# Remove this script's directory from sys.path to prevent self-shadowing
# (this file is named horizon.py, which would shadow the horizon package).
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p) != _script_dir]


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

# Identifiers: market IDs, order IDs, feed names, slugs, tickers.
# Allow alphanumeric, hyphens, underscores, dots, colons. Max 256 chars.
_ID_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,256}$")

# Hex addresses (Ethereum-style): 0x followed by hex digits. Max 66 chars
# (covers condition IDs which can be longer than 42).
_HEX_RE = re.compile(r"^0x[0-9a-fA-F]{1,64}$")

# Allowed exchanges (whitelist).
_VALID_EXCHANGES = {"polymarket", "kalshi", "paper"}

# Allowed side values (whitelist).
_VALID_SIDES = {"yes", "no"}

# Allowed order side values (whitelist).
_VALID_ORDER_SIDES = {"buy", "sell"}

# Allowed sort-by values for wallet-positions.
_VALID_SORT_BY = {"TOKENS", "CURRENT", "INITIAL", "CASHPNL", "PERCENTPNL", "PRICE", "AVGPRICE"}

# Allowed feed types for start-feed (no arbitrary-URL feeds to prevent SSRF).
_SAFE_FEED_TYPES = {"binance_ws", "polymarket_book", "kalshi_book", "predictit", "manifold", "espn", "nws"}


def _validate_id(value: str, label: str) -> str:
    """Validate an identifier string (market ID, order ID, feed name, etc.)."""
    if not _ID_RE.match(value):
        _print({"error": f"invalid {label}: must be 1-256 alphanumeric/dash/underscore/dot/colon characters"})
        sys.exit(1)
    return value


def _validate_hex_or_id(value: str, label: str) -> str:
    """Validate a value that can be either a hex address or an identifier."""
    if value.startswith("0x") or value.startswith("0X"):
        if not _HEX_RE.match(value):
            _print({"error": f"invalid {label}: malformed hex address"})
            sys.exit(1)
    elif not _ID_RE.match(value):
        _print({"error": f"invalid {label}: must be alphanumeric or hex address"})
        sys.exit(1)
    return value


def _validate_exchange(value: str) -> str:
    """Validate exchange name against whitelist."""
    if value.lower() not in _VALID_EXCHANGES:
        _print({"error": f"invalid exchange: {value!r}. Must be one of: {', '.join(sorted(_VALID_EXCHANGES))}"})
        sys.exit(1)
    return value.lower()


def _validate_side(value: str) -> str:
    """Validate side (yes/no) against whitelist."""
    if value.lower() not in _VALID_SIDES:
        _print({"error": f"invalid side: {value!r}. Must be 'yes' or 'no'"})
        sys.exit(1)
    return value.lower()


def _validate_order_side(value: str) -> str:
    """Validate order side (buy/sell) against whitelist."""
    if value.lower() not in _VALID_ORDER_SIDES:
        _print({"error": f"invalid order_side: {value!r}. Must be 'buy' or 'sell'"})
        sys.exit(1)
    return value.lower()


def _validate_sort_by(value: str) -> str:
    """Validate sort_by against allowed values."""
    if value.upper() not in _VALID_SORT_BY:
        _print({"error": f"invalid sort_by: {value!r}. Must be one of: {', '.join(sorted(_VALID_SORT_BY))}"})
        sys.exit(1)
    return value.upper()


def _safe_int(value: str, label: str) -> int:
    """Parse a string to int with error handling."""
    try:
        return int(value)
    except ValueError:
        _print({"error": f"invalid {label}: {value!r} is not an integer"})
        sys.exit(1)


def _safe_float(value: str, label: str) -> float:
    """Parse a string to float with error handling."""
    try:
        result = float(value)
    except ValueError:
        _print({"error": f"invalid {label}: {value!r} is not a number"})
        sys.exit(1)
    if result != result:  # NaN check
        _print({"error": f"invalid {label}: NaN is not allowed"})
        sys.exit(1)
    return result


def _safe_float_list(value: str, label: str) -> list[float]:
    """Parse a comma-separated string to list of floats."""
    try:
        return [float(x) for x in value.split(",")]
    except ValueError:
        _print({"error": f"invalid {label}: must be comma-separated numbers"})
        sys.exit(1)


def _validate_text(value: str, label: str, max_len: int = 500) -> str:
    """Validate free-text input: length-cap only (no shell metacharacters needed
    since this never touches a shell)."""
    if len(value) > max_len:
        _print({"error": f"{label} too long (max {max_len} chars)"})
        sys.exit(1)
    return value


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _print(data: object) -> None:
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args:
        _print({"error": "no command. try: status, positions, orders, fills, quote, cancel, cancel-all, cancel-market, discover, discover-events, top-markets, kelly, kill-switch, stop-loss, take-profit, feed, feeds, feed-health, feed-metrics, parity, contingent, wallet-trades, market-trades, wallet-positions, wallet-value, wallet-profile, top-holders, market-flow, simulate, arb, entropy, kl-divergence, hurst, variance-ratio, cf-var, greeks, deflated-sharpe, signal-diagnostics, market-efficiency, stress-test, start-feed"})
        sys.exit(1)

    cmd = args[0]

    from horizon import tools

    if cmd == "status":
        _print(tools.engine_status())

    elif cmd == "positions":
        _print(tools.list_positions())

    elif cmd == "orders":
        market_id = _validate_id(args[1], "market_id") if len(args) > 1 else None
        _print(tools.list_open_orders(market_id))

    elif cmd == "fills":
        limit = _safe_int(args[1], "limit") if len(args) > 1 else 20
        _print(tools.list_recent_fills(limit))

    elif cmd == "quote":
        if len(args) < 5:
            _print({"error": "usage: quote <market_id> <side> <price> <size> [market_side]"})
            sys.exit(1)
        market_id = _validate_id(args[1], "market_id")
        side = _validate_order_side(args[2])
        price = _safe_float(args[3], "price")
        size = _safe_float(args[4], "size")
        market_side = _validate_side(args[5]) if len(args) > 5 else "yes"
        _print(tools.submit_order(market_id, side, price, size, market_side))

    elif cmd == "cancel":
        if len(args) < 2:
            _print({"error": "usage: cancel <order_id>"})
            sys.exit(1)
        _print(tools.cancel_order(_validate_id(args[1], "order_id")))

    elif cmd == "cancel-all":
        _print(tools.cancel_all_orders())

    elif cmd == "cancel-market":
        if len(args) < 2:
            _print({"error": "usage: cancel-market <market_id>"})
            sys.exit(1)
        _print(tools.cancel_market_orders(_validate_id(args[1], "market_id")))

    elif cmd == "discover":
        exchange = _validate_exchange(args[1]) if len(args) > 1 else "polymarket"
        query = _validate_text(args[2], "query") if len(args) > 2 else ""
        limit = _safe_int(args[3], "limit") if len(args) > 3 else 10
        _print(tools.discover(exchange, query, limit))

    elif cmd == "kelly":
        if len(args) < 4:
            _print({"error": "usage: kelly <prob> <price> <bankroll> [fraction] [max_size]"})
            sys.exit(1)
        prob = _safe_float(args[1], "prob")
        price = _safe_float(args[2], "price")
        bankroll = _safe_float(args[3], "bankroll")
        fraction = _safe_float(args[4], "fraction") if len(args) > 4 else 0.25
        max_size = _safe_float(args[5], "max_size") if len(args) > 5 else 100.0
        _print(tools.kelly_sizing(prob, price, bankroll, fraction, max_size))

    elif cmd == "kill-switch":
        if len(args) < 2:
            _print({"error": "usage: kill-switch <on|off> [reason]"})
            sys.exit(1)
        if args[1] == "on":
            reason = _validate_text(args[2], "reason", 200) if len(args) > 2 else "manual"
            _print(tools.activate_kill_switch(reason))
        elif args[1] == "off":
            _print(tools.deactivate_kill_switch())
        else:
            _print({"error": "usage: kill-switch <on|off> [reason]"})
            sys.exit(1)

    elif cmd == "stop-loss":
        if len(args) < 6:
            _print({"error": "usage: stop-loss <market_id> <side> <order_side> <size> <trigger_price>"})
            sys.exit(1)
        _print(tools.add_stop_loss(
            _validate_id(args[1], "market_id"),
            _validate_side(args[2]),
            _validate_order_side(args[3]),
            _safe_float(args[4], "size"),
            _safe_float(args[5], "trigger_price"),
        ))

    elif cmd == "take-profit":
        if len(args) < 6:
            _print({"error": "usage: take-profit <market_id> <side> <order_side> <size> <trigger_price>"})
            sys.exit(1)
        _print(tools.add_take_profit(
            _validate_id(args[1], "market_id"),
            _validate_side(args[2]),
            _validate_order_side(args[3]),
            _safe_float(args[4], "size"),
            _safe_float(args[5], "trigger_price"),
        ))

    elif cmd == "feed":
        if len(args) < 2:
            _print({"error": "usage: feed <name>"})
            sys.exit(1)
        _print(tools.get_feed_snapshot(_validate_id(args[1], "feed_name")))

    elif cmd == "feeds":
        _print(tools.list_all_feeds())

    elif cmd == "parity":
        if len(args) < 2:
            _print({"error": "usage: parity <market_id> [feed_name]"})
            sys.exit(1)
        market_id = _validate_id(args[1], "market_id")
        feed_name = _validate_id(args[2], "feed_name") if len(args) > 2 else None
        _print(tools.check_parity(market_id, feed_name))

    elif cmd == "contingent":
        _print(tools.list_contingent_orders())

    # --- Feed health ---

    elif cmd == "feed-metrics":
        if len(args) < 2:
            _print(tools.all_feed_metrics())
        else:
            _print(tools.feed_metrics(_validate_id(args[1], "feed_name")))

    elif cmd == "feed-health":
        threshold = _safe_float(args[1], "threshold") if len(args) > 1 else 30.0
        _print(tools.check_feed_health(threshold))

    # --- Discovery ---

    elif cmd == "discover-events":
        query = _validate_text(args[1], "query") if len(args) > 1 else ""
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 10
        _print(tools.discover_event(query, limit))

    elif cmd == "top-markets":
        exchange = _validate_exchange(args[1]) if len(args) > 1 else "polymarket"
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 10
        category = _validate_text(args[3], "category", 100) if len(args) > 3 else ""
        _print(tools.get_top_markets(exchange, limit, category))

    # --- Wallet analytics (Polymarket, no auth) ---

    elif cmd == "wallet-trades":
        if len(args) < 2:
            _print({"error": "usage: wallet-trades <address> [limit] [condition_id]"})
            sys.exit(1)
        address = _validate_hex_or_id(args[1], "address")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 50
        cid = _validate_hex_or_id(args[3], "condition_id") if len(args) > 3 else None
        _print(tools.wallet_trades(address, limit, cid))

    elif cmd == "market-trades":
        if len(args) < 2:
            _print({"error": "usage: market-trades <condition_id> [limit] [side] [min_size]"})
            sys.exit(1)
        cid = _validate_hex_or_id(args[1], "condition_id")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 50
        side = _validate_order_side(args[3]) if len(args) > 3 else None
        min_size = _safe_float(args[4], "min_size") if len(args) > 4 else 0.0
        _print(tools.market_trades(cid, limit, side, min_size))

    elif cmd == "wallet-positions":
        if len(args) < 2:
            _print({"error": "usage: wallet-positions <address> [limit] [sort_by]"})
            sys.exit(1)
        address = _validate_hex_or_id(args[1], "address")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 50
        sort_by = _validate_sort_by(args[3]) if len(args) > 3 else "CURRENT"
        _print(tools.wallet_positions(address, limit, sort_by))

    elif cmd == "wallet-value":
        if len(args) < 2:
            _print({"error": "usage: wallet-value <address>"})
            sys.exit(1)
        _print(tools.wallet_value(_validate_hex_or_id(args[1], "address")))

    elif cmd == "wallet-profile":
        if len(args) < 2:
            _print({"error": "usage: wallet-profile <address>"})
            sys.exit(1)
        _print(tools.wallet_profile(_validate_hex_or_id(args[1], "address")))

    elif cmd == "top-holders":
        if len(args) < 2:
            _print({"error": "usage: top-holders <condition_id> [limit]"})
            sys.exit(1)
        cid = _validate_hex_or_id(args[1], "condition_id")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 20
        _print(tools.market_top_holders(cid, limit))

    elif cmd == "market-flow":
        if len(args) < 2:
            _print({"error": "usage: market-flow <condition_id> [trade_limit] [top_n]"})
            sys.exit(1)
        cid = _validate_hex_or_id(args[1], "condition_id")
        trade_limit = _safe_int(args[2], "trade_limit") if len(args) > 2 else 500
        top_n = _safe_int(args[3], "top_n") if len(args) > 3 else 10
        _print(tools.market_flow(cid, trade_limit, top_n))

    # --- Start feed ---

    elif cmd == "start-feed":
        if len(args) < 3:
            _print({"error": "usage: start-feed <name> <feed_type> [config_json]"})
            sys.exit(1)
        name = _validate_id(args[1], "feed_name")
        feed_type = _validate_id(args[2], "feed_type")
        # Block feed types that accept arbitrary URLs (SSRF prevention).
        # Use the Python SDK directly for chainlink, rest, rest_json_path feeds.
        if feed_type not in _SAFE_FEED_TYPES:
            _print({"error": f"feed type {feed_type!r} not allowed via CLI. Allowed: {', '.join(sorted(_SAFE_FEED_TYPES))}. Use the Python SDK for URL-based feeds."})
            sys.exit(1)
        config_json = args[3] if len(args) > 3 else None
        # Validate config_json is valid JSON if provided
        if config_json is not None:
            try:
                json.loads(config_json)
            except json.JSONDecodeError:
                _print({"error": "config_json must be valid JSON"})
                sys.exit(1)
        _print(tools.start_feed(name, feed_type, config_json=config_json))

    # --- Simulation ---

    elif cmd == "simulate":
        scenarios = _safe_int(args[1], "scenarios") if len(args) > 1 else 10000
        seed = _safe_int(args[2], "seed") if len(args) > 2 else None
        _print(tools.simulate_portfolio(scenarios, seed))

    # --- Arbitrage ---

    elif cmd == "arb":
        if len(args) < 7:
            _print({"error": "usage: arb <market_id> <buy_exchange> <sell_exchange> <buy_price> <sell_price> <size>"})
            sys.exit(1)
        _print(tools.execute_arb(
            _validate_id(args[1], "market_id"),
            _validate_exchange(args[2]),
            _validate_exchange(args[3]),
            _safe_float(args[4], "buy_price"),
            _safe_float(args[5], "sell_price"),
            _safe_float(args[6], "size"),
        ))

    # --- Quantitative Analytics ---

    elif cmd == "entropy":
        if len(args) < 2:
            _print({"error": "usage: entropy <probability>"})
            sys.exit(1)
        _print(tools.compute_shannon_entropy(_safe_float(args[1], "probability")))

    elif cmd == "kl-divergence":
        if len(args) < 3:
            _print({"error": "usage: kl-divergence <p_values> <q_values> (comma-separated)"})
            sys.exit(1)
        p = _safe_float_list(args[1], "p_values")
        q = _safe_float_list(args[2], "q_values")
        _print(tools.compute_kl_divergence(p, q))

    elif cmd == "hurst":
        if len(args) < 2:
            _print({"error": "usage: hurst <prices> (comma-separated)"})
            sys.exit(1)
        _print(tools.compute_hurst_exponent(_safe_float_list(args[1], "prices")))

    elif cmd == "variance-ratio":
        if len(args) < 2:
            _print({"error": "usage: variance-ratio <returns> (comma-separated) [period]"})
            sys.exit(1)
        returns = _safe_float_list(args[1], "returns")
        period = _safe_int(args[2], "period") if len(args) > 2 else 2
        _print(tools.compute_variance_ratio(returns, period))

    elif cmd == "cf-var":
        if len(args) < 2:
            _print({"error": "usage: cf-var <returns> (comma-separated) [confidence]"})
            sys.exit(1)
        returns = _safe_float_list(args[1], "returns")
        confidence = _safe_float(args[2], "confidence") if len(args) > 2 else 0.95
        _print(tools.compute_cornish_fisher_var(returns, confidence))

    elif cmd == "greeks":
        if len(args) < 3:
            _print({"error": "usage: greeks <price> <size> [is_yes] [t_hours] [vol]"})
            sys.exit(1)
        price = _safe_float(args[1], "price")
        size = _safe_float(args[2], "size")
        is_yes = args[3].lower() in ("true", "yes", "1") if len(args) > 3 else True
        t_hours = _safe_float(args[4], "t_hours") if len(args) > 4 else 24.0
        vol = _safe_float(args[5], "vol") if len(args) > 5 else 0.2
        _print(tools.compute_prediction_greeks(price, size, is_yes, t_hours, vol))

    elif cmd == "deflated-sharpe":
        if len(args) < 4:
            _print({"error": "usage: deflated-sharpe <sharpe> <n_obs> <n_trials> [skew] [kurt]"})
            sys.exit(1)
        sharpe = _safe_float(args[1], "sharpe")
        n_obs = _safe_int(args[2], "n_obs")
        n_trials = _safe_int(args[3], "n_trials")
        skew = _safe_float(args[4], "skew") if len(args) > 4 else 0.0
        kurt = _safe_float(args[5], "kurt") if len(args) > 5 else 3.0
        _print(tools.compute_deflated_sharpe(sharpe, n_obs, n_trials, skew, kurt))

    elif cmd == "signal-diagnostics":
        if len(args) < 3:
            _print({"error": "usage: signal-diagnostics <predictions> <outcomes> (comma-separated)"})
            sys.exit(1)
        predictions = _safe_float_list(args[1], "predictions")
        outcomes = _safe_float_list(args[2], "outcomes")
        _print(tools.run_signal_diagnostics(predictions, outcomes))

    elif cmd == "market-efficiency":
        if len(args) < 2:
            _print({"error": "usage: market-efficiency <prices> (comma-separated)"})
            sys.exit(1)
        _print(tools.run_market_efficiency(_safe_float_list(args[1], "prices")))

    elif cmd == "stress-test":
        scenarios = _safe_int(args[1], "scenarios") if len(args) > 1 else 10000
        seed = _safe_int(args[2], "seed") if len(args) > 2 else None
        _print(tools.run_stress_test(scenarios, seed))

    else:
        _print({"error": f"unknown command: {args[0][:64]}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
