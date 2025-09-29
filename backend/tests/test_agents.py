"""Smoke tests for AI agents hitting real services."""

import asyncio
import os
import sys
from pathlib import Path
import re

from dotenv import load_dotenv
import requests

# Ensure backend package is on sys.path when invoked from repo root
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ai_agents import AgentConfig, ImageAgent, SearchAgent


load_dotenv()


async def test_search_agent():
    os.environ.setdefault("AI_MODEL_NAME", "gemini-2.5-pro")
    config = AgentConfig()
    agent = SearchAgent(config)

    prompt = "Use web search to find today's weather in Tokyo"
    response = await agent.execute(prompt, use_tools=True)

    assert response.success, response.error
    assert response.metadata.get("tools_used"), "Expected MCP tools to be invoked"
    assert "tokyo" in response.content.lower()


async def test_image_agent():
    os.environ.setdefault("AI_MODEL_NAME", "gemini-2.5-pro")
    config = AgentConfig()
    agent = ImageAgent(config)

    prompt = "Generate an image of a sunset over mountains"
    response = await agent.execute(prompt, use_tools=True)

    assert response.success, response.error
    assert response.metadata.get("tools_used"), "Expected MCP tools to be invoked"

    urls = re.findall(r"https?://[^\s)]+", response.content)
    assert urls, "Expected the response to include at least one URL"

    head = requests.head(urls[0], timeout=10)
    assert head.status_code == 200, f"Image URL not reachable: HTTP {head.status_code}"


async def main():
    await test_search_agent()
    await test_image_agent()


if __name__ == "__main__":
    asyncio.run(main())
