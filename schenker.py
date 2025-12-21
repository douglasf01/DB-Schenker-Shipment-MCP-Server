from fastmcp import FastMCP
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
import logging
import logging
import requests
import asyncio

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169 Safari/537.36"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_soup_from_url(url, max_retries=3, timeout=20000) -> BeautifulSoup:
    retries = 0
    while retries < max_retries:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(user_agent=USER_AGENT)
            page = await context.new_page()
            try:
                await page.goto(url, timeout=timeout)
                await page.wait_for_load_state("networkidle", timeout=timeout)

                try:
                    locator = page.get_by_text("See more")
                    count = await locator.count()
                    if count:
                        await page.get_by_text('See more').evaluate("element => element.click()")
                        await page.wait_for_load_state("networkidle", timeout=timeout)
                except Exception as e:
                    logging.error(f"Error clicking 'See more' button, some information might be missing: {e}")
                    pass

                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                return soup

            except PlaywrightTimeoutError:
                logging.error(f"Timeout error fetching the URL: {url}")
                retries += 1
                await asyncio.sleep(1) 

            except PlaywrightError as e:
                logging.error(f"Playwright error fetching the URL: {e}")
                retries += 1
                await asyncio.sleep(1)

            except Exception as e:
                logging.error(f"Unexpected error fetching the URL: {e}")
                retries += 1
                await asyncio.sleep(1)

            finally:
                try:
                    if page is not None:
                        await page.close()
                except Exception:
                    logging.debug("Error closing page", exc_info=1)
                try:
                    if context is not None:
                        await context.close()
                except Exception:
                    logging.debug("Error closing context", exc_info=1)
                try:
                    if browser is not None:
                        await browser.close()
                except Exception:
                    logging.debug("Error closing browser", exc_info=1)
                
        logging.error(f"Failed to fetch URL after {max_retries} retries: {url}")
        return None

def details(soup):
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
    table_data = []
    #Iterate over the rows of the table
    for row in soup.find_all("tr"):
        row_data = []
        cells = row.find_all(["th", "td"])
        #Skip the first cell of each row
        if cells:
            cells = cells[1:]
        for cell in cells:
            cell_text = cell.get_text(strip=True)
            if cell_text.startswith("Package"):
                return table_data
            row_data.append(cell_text if cell_text else "-")
        table_data.append(row_data)

    if not table_data:
        logging.ERROR("Table is empty")
        return ""

    markdown_table = ""
    markdown_table += "| " + " | ".join(table_data[0]) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(table_data[0])) + " |\n"

    for row in table_data[1:]:
        markdown_table += "| " + " | ".join(row) + " |\n"

    return markdown_table