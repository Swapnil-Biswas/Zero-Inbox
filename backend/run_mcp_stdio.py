"""
ZERO-INBOX: MCP STDIO Runner for Local Clients (Claude Desktop / Cursor)
"""

import asyncio
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp.server import mcp_server


async def main():
    # Run the official MCP server over STDIO
    await mcp_server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
