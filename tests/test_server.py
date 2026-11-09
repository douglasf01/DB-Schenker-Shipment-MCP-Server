import pytest
from bs4 import BeautifulSoup
from fastmcp import Client
from fastmcp.exceptions import ToolError

import server


async def test_tool_is_listed_with_schema():
    async with Client(server.mcp) as client:
        tools = await client.list_tools()
    assert [t.name for t in tools] == ["track_shipment"]
    schema = tools[0].inputSchema
    assert schema["required"] == ["tracking_number"]
    assert schema["properties"]["tracking_number"]["type"] == "string"


@pytest.mark.parametrize("bad", ["12345", "1906203236", "18062032366", "abc"])
async def test_invalid_tracking_number(bad, monkeypatch):
    async def fail(url):
        raise AssertionError("should not fetch the page")

    monkeypatch.setattr(server, "get_soup_from_url", fail)
    async with Client(server.mcp) as client:
        with pytest.raises(ToolError, match="Invalid tracking number"):
            await client.call_tool("track_shipment", {"tracking_number": bad})


async def test_page_could_not_load(monkeypatch):
    async def fake(url):
        return None

    monkeypatch.setattr(server, "get_soup_from_url", fake)
    async with Client(server.mcp) as client:
        with pytest.raises(ToolError, match="Could not load the DB Schenker tracking page"):
            await client.call_tool("track_shipment", {"tracking_number": "1806203236"})


async def test_shipment_not_found(monkeypatch):
    async def fake(url):
        assert url.endswith("1806203236")
        return BeautifulSoup("<html><body>Nothing here</body></html>", "html.parser")

    monkeypatch.setattr(server, "get_soup_from_url", fake)
    async with Client(server.mcp) as client:
        with pytest.raises(ToolError, match="No shipment found"):
            await client.call_tool("track_shipment", {"tracking_number": " 1806203236 "})
