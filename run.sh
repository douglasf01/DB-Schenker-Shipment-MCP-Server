#!/bin/bash
# Install everything and open the server in MCP Inspector.
set -e
cd "$(dirname "$0")"

# Install Python dependencies into .venv
uv sync

# Download the Chromium browser used by Playwright (skipped if already installed)
uv run playwright install chromium

# Start MCP Inspector with the server
npx @modelcontextprotocol/inspector uv run fastmcp run server.py
