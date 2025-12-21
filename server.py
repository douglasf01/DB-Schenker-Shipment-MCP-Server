from schenker import get_soup_from_url, details, history
from fastmcp import FastMCP
import re

mcp = FastMCP(name="Local MCP")

LINK = "https://www.dbschenker.com/app/tracking-public/?refNumber="

@mcp.tool
async def soup_cleaning(trackingNum):
    
    """
    Retrieves and cleans tracking information from DB Schenker based on a tracking number.
    
    Args:
        trackingNum (int or str): The tracking number, which must be an integer or a (digit) string starting with '180' and be 10 digits long.
    Returns:
        str: Concatenated details and history of the tracking information.
    Raises:
        ValueError: If the tracking number is invalid or if the webpage content cannot be retrieved.
    """

    if isinstance(trackingNum, int):
        tracking = str(trackingNum)
    elif isinstance(trackingNum, str):
        tracking = trackingNum.strip()
    else:
        raise ValueError("Tracking number must be an integer or a digit string")
    if not re.fullmatch(r"180\d{7}", tracking):
        raise ValueError("Tracking number must starts with '180' and be 10 digits")

    full_link = LINK + tracking
    soup = await get_soup_from_url(full_link)
    
    if soup is not None:
        soup_details= soup.select(".tracking-details-header, .tracking-details-value, [data-test='service_name_value'], [data-test='consignee_reference_value'], [data-test='shipper_reference_value']")
        soup_history = soup.select_one(".pt-table.ng-star-inserted")
        
        details_out = details(soup_details)
        history_out = history(soup_history)
        return details_out  + "\n" + history_out;
    else:
        raise ValueError("Failed to retrieve the webpage content.")

#Run the server
if __name__ == "__main__":
    mcp.run()