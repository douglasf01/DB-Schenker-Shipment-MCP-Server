from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging
import asyncio

USER_AGENT = "Mozilla/5.0 (X11; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169/.170 Safari/537.36"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
async def get_soup_from_url(url) -> BeautifulSoup:

    """
    Retrieves the content of a webpage using playwright, parses it with BeautifulSoup.

    Args:
        url (str): The URL to DB Schenker.
    Returns:
        BeautifulSoup: Parsed HTML content of the webpage, or None if fetching fails.
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(user_agent=USER_AGENT) 
        page = await context.new_page()
        try:
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            #Triggering action handler
            await page.get_by_text('See more').evaluate("element => element.click()")
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            return soup
        except Exception as e:
            logging.info(f"Error fetching the URL: {e}")
            return None
        finally:
            await browser.close()


def details(soup):
    """
    Extracts package details in key-value pairs from parsed HTML content and formats them into a markdown table.

    Args:
        soup (BeautifulSoup): Parsed HTML content containing key-value pairs.
    Returns:
        str: A markdown table with keys and values extracted from the HTML content.

    """
    markdown_table = "| Key | Value |\n| --- | --- |\n"
    i = 0
    while i < len(soup):
        key = soup[i].get_text(strip=True)
        if i + 1 < len(soup):
            value = soup[i + 1].get_text(strip=True)
            #Check if the key is "Consignment Number/Waybill Number" and the next value is a number
            if key == "Consignment Number/Waybill Number" and i + 2 < len(soup) and soup[i + 2].get_text(strip=True).isdigit():
                next_value = soup[i + 2].get_text(strip=True)
                markdown_table += f"| {key} | {value}/{next_value} |\n"
                i += 3  #Skip the next two elements, already processed
                continue
        else:
            value = ""
        markdown_table += f"| {key} | {value} |\n"
        i += 2
    return markdown_table

def history(soup):
    
    """
    Extracts shipping history data from parsed HTML content and formats it as a markdown table

    Args:
        soup (BeautifulSoup): Parsed HTML content containing shipping history.
    Returns:
        str: A markdown table with data extracted from the HTML table.
    """

    table_data = []
    #Iterate over the rows of the table
    for row in soup.find_all("tr"):
        row_data = []
        cells = row.find_all(["th", "td"])
        #Skip the first cell of each row (empty)
        if cells:
            cells = cells[1:]
        for cell in cells:
            cell_text = cell.get_text(strip=True)
            if cell_text.startswith("Package"):
                return table_data
            row_data.append(cell_text if cell_text else "-")
        table_data.append(row_data)

    markdown_table = ""
    markdown_table += "| " + " | ".join(table_data[0]) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(table_data[0])) + " |\n"

    for row in table_data[1:]:
        markdown_table += "| " + " | ".join(row) + " |\n"

    return markdown_table
