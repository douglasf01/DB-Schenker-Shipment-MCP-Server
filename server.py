"""MCP server that tracks DB Schenker shipments."""

import re

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from schenker import TRACKING_URL, get_soup_from_url, parse_tracking_page

mcp = FastMCP(name="DB Schenker Shipment Tracker")

TRACKING_NUMBER = re.compile(r"180\d{7}")


@mcp.tool
async def track_shipment(tracking_number: str) -> str:
    """Look up a DB Schenker shipment and return its details and history.

    Args:
        tracking_number: The DB Schenker tracking number. It is 10 digits
            long and starts with 180, for example 1806203236.

    Returns:
        Markdown tables with the shipment details and the tracking history.
    """
    tracking = tracking_number.strip().replace(" ", "")
    if not TRACKING_NUMBER.fullmatch(tracking):
        raise ToolError(
            f"Invalid tracking number '{tracking_number}'. A DB Schenker tracking "
            "number is 10 digits and starts with 180, for example 1806203236. "
            "Ask the user to check the number."
        )

    soup = await get_soup_from_url(TRACKING_URL + tracking)
    if soup is None:
        raise ToolError(
            "Could not load the DB Schenker tracking page. The site may be down "
            "or blocking the request. Try again later."
        )

    report = parse_tracking_page(soup)
    if report is None:
        raise ToolError(
            f"No shipment found for tracking number {tracking}. "
            "Ask the user to check the number."
        )
    return report


if __name__ == "__main__":
    mcp.run()
