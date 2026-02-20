#!/usr/bin/env python3
"""
MCP Skill Executor
==================
Handles dynamic communication with the MCP server.
"""

import json
import sys
import asyncio
import argparse
import socket
from pathlib import Path

# Check if mcp package is available
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: mcp package not installed. Install with: pip install mcp", file=sys.stderr)


def _check_futu_port(env: dict, timeout: float = 3.0) -> None:
    """Best-effort runtime check: ensure FutuOpenD TCP 端口真的在监听.

    直接用 socket 建立一次 TCP 连接，而不是只看日志，避免“日志说监听了但进程已经挂了”的情况。
    """
    host = (env or {}).get("FUTU_HOST") or "127.0.0.1"
    port_str = (env or {}).get("FUTU_PORT") or "11111"
    try:
        port = int(port_str)
    except ValueError:
        print(f"Error: invalid FUTU_PORT value: {port_str}", file=sys.stderr)
        sys.exit(1)

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return
    except OSError as e:
        print(f"Error: FutuOpenD not listening on {host}:{port} ({e})", file=sys.stderr)
        sys.exit(1)


async def list_tools_from_server(server_config):
    """Get list of available tools from MCP server.

    在真正连 MCP 之前，先实时检查一下 FutuOpenD 端口是否在监听，避免死等。
    """
    _check_futu_port(server_config.get("env"))

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config.get("args", []),
        env=server_config.get("env")
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in response.tools
            ]


async def describe_tool_from_server(server_config, tool_name: str):
    """Get detailed schema for a specific tool from MCP server."""
    _check_futu_port(server_config.get("env"))

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config.get("args", []),
        env=server_config.get("env")
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()

            for tool in response.tools:
                if tool.name == tool_name:
                    return {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
            return None


async def call_tool_on_server(server_config, tool_name: str, arguments: dict):
    """Execute a tool call on MCP server."""
    _check_futu_port(server_config.get("env"))

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config.get("args", []),
        env=server_config.get("env")
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.call_tool(tool_name, arguments)
            return response.content


async def main():
    parser = argparse.ArgumentParser(description="MCP Skill Executor")
    parser.add_argument("--call", help="JSON tool call to execute")
    parser.add_argument("--describe", help="Get tool schema")
    parser.add_argument("--list", action="store_true", help="List all tools")

    args = parser.parse_args()

    # Load server config
    config_path = Path(__file__).parent / "mcp-config.json"
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    if not HAS_MCP:
        print("Error: mcp package not installed", file=sys.stderr)
        print("Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)

    try:
        if args.list:
            tools = await list_tools_from_server(config)
            print(json.dumps(tools, indent=2))

        elif args.describe:
            schema = await describe_tool_from_server(config, args.describe)
            if schema:
                print(json.dumps(schema, indent=2))
            else:
                print(f"Tool not found: {args.describe}", file=sys.stderr)
                sys.exit(1)

        elif args.call:
            call_data = json.loads(args.call)
            result = await call_tool_on_server(
                config,
                call_data["tool"],
                call_data.get("arguments", {})
            )

            # Format result
            if isinstance(result, list):
                for item in result:
                    if hasattr(item, 'text'):
                        print(item.text)
                    else:
                        print(json.dumps(item.__dict__ if hasattr(item, '__dict__') else item, indent=2))
            else:
                print(json.dumps(result.__dict__ if hasattr(result, '__dict__') else result, indent=2))
        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
