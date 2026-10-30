"""
ZERO-INBOX: MCP Server Tools, Resources & Prompts Test Suite
"""

import unittest
import asyncio
import json
from app.mcp.server import (
    mcp_server, get_capabilities_resource, get_methodology_resource,
    morning_intelligence_brief
)
from app.core.models import SourceConfig, SourceType
from app.db.database import db


class TestMCPServer(unittest.TestCase):

    def test_mcp_resources(self):
        caps = get_capabilities_resource()
        parsed = json.loads(caps)
        self.assertIn("supported_sources", parsed)
        self.assertIn("rss", parsed["supported_sources"])

        methodology = get_methodology_resource()
        self.assertIn("Methodology", methodology)

    def test_mcp_prompts(self):
        prompt_text = morning_intelligence_brief()
        self.assertIn("morning brief", prompt_text.lower())
        self.assertIn("factual", prompt_text.lower())

    def test_mcp_tools(self):
        loop = asyncio.new_event_loop()

        # Test add_source tool
        add_source_tool = mcp_server._tool_manager.get_tool("add_source")
        self.assertIsNotNone(add_source_tool)
        res_str = loop.run_until_complete(
            add_source_tool.fn(
                name="Test AI Feed",
                url="https://news.ycombinator.com/rss",
                source_type="rss",
                user_id="test_mcp_user"
            )
        )
        res = json.loads(res_str)
        self.assertEqual(res["status"], "success")
        src_id = res["source_id"]

        # Test list_sources tool
        list_tool = mcp_server._tool_manager.get_tool("list_sources")
        list_res = json.loads(loop.run_until_complete(list_tool.fn(user_id="test_mcp_user")))
        self.assertGreaterEqual(list_res["total"], 1)

        # Test get_agent_status tool
        status_tool = mcp_server._tool_manager.get_tool("get_agent_status")
        status_res = json.loads(loop.run_until_complete(status_tool.fn()))
        self.assertEqual(status_res["status"], "operational")

        # Test remove_source tool
        remove_tool = mcp_server._tool_manager.get_tool("remove_source")
        rem_res = json.loads(loop.run_until_complete(remove_tool.fn(source_id=src_id, user_id="test_mcp_user")))
        self.assertEqual(rem_res["status"], "success")

        loop.close()


if __name__ == "__main__":
    unittest.main()
