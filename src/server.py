"""
WHM/cPanel MCP Server — Multi-Account Root Access
Author: Built for Hesham Mahdy
"""

import asyncio
import json
import os
import sys
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from accounts import load_accounts, get_account
from tools import (
    whm_tools, cpanel_tools,
    handle_whm_tool, handle_cpanel_tool
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
log = logging.getLogger("itch-whm-mcp")

app = Server("ItchWHMMCP")


@app.list_tools()
async def list_tools() -> list[Tool]:
    all_tools = []
    all_tools.append(Tool(
        name="list_accounts",
        description="List all configured WHM/cPanel server accounts available in this MCP",
        inputSchema={"type": "object", "properties": {}, "required": []}
    ))
    all_tools.extend(whm_tools())
    all_tools.extend(cpanel_tools())
    return all_tools


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    log.info(f"Tool called: {name} | Args: {json.dumps(arguments)}")

    if name == "list_accounts":
        accounts = load_accounts()
        result = [
            {"alias": a, "host": cfg["host"], "type": cfg.get("type","whm")}
            for a, cfg in accounts.items()
            if isinstance(cfg, dict) and not a.startswith("_")
        ]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    account_alias = arguments.get("account")
    if not account_alias:
        return [TextContent(type="text", text="ERROR: 'account' parameter is required. Use list_accounts to see available accounts.")]

    account = get_account(account_alias)
    if not account:
        return [TextContent(type="text", text=f"ERROR: Account '{account_alias}' not found. Use list_accounts to see configured accounts.")]

    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        if name.startswith("whm_"):
            result = await handle_whm_tool(client, account, name, arguments)
        elif name.startswith("cpanel_"):
            result = await handle_cpanel_tool(client, account, name, arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    log.info("WHM/cPanel MCP Server starting...")
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
