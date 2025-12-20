from schenker import get_soup_from_url, details, history
from fastmcp import FastMCP

mcp = FastMCP(name="Local MCP")

LINK = "https://www.dbschenker.com/app/tracking-public/?refNumber="

@mcp.tool
async def soup_cleaning(trackingNum):
    if not isinstance(trackingNum, int):
        raise ValueError("Tracking number is an integer")
    if not str(trackingNum)[:3] == "180":
        raise ValueError("Tracking number starts with 180")
    if not  len(str(trackingNum)) == 10:
        raise ValueError("Tracking number is 10 digits")
        
    full_link = LINK + str(trackingNum)
    soup = await get_soup_from_url(full_link)
    
    if soup is not None:

        soup_details= soup.select(".tracking-details-header, .tracking-details-value, [data-test='service_name_value']")
        details_out = details(soup_details)

        soup_history = soup.select_one(".pt-table")
        history_out = history(soup_history)

        return details_out  + "\n" + history_out;
    else:
        raise ValueError("Failed to retrieve the webpage content.")


# Run the server
if __name__ == "__main__":
    mcp.run()
