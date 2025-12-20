from fastmcp import FastMCP
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright 
import logging
import requests
import asyncio

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169 Safari/537.36"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def get_soup_from_url(url) -> str:
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
    markdown_table = "| Key | Value |\n| --- | --- |\n"
    i = 0
    while i < len(soup):
        key = soup[i].get_text(strip=True)
        if i + 1 < len(soup):
            value = soup[i + 1].get_text(strip=True)
            # Check if the key is "Consignment Number/Waybill Number" and the next value is a number
            if key == "Consignment Number/Waybill Number" and i + 2 < len(soup) and soup[i + 2].get_text(strip=True).isdigit():
                next_value = soup[i + 2].get_text(strip=True)
                markdown_table += f"| {key} | {value}/{next_value} |\n"
                i += 3  # Skip the next two elements since we've already processed them
                continue
        else:
            value = ""
        markdown_table += f"| {key} | {value} |\n"
        i += 2
    return markdown_table

def history(soup):
    table_data = []
    # Iterate over the rows of the table
    for row in soup.find_all("tr"):
        row_data = []
        for cell in row.find_all(["th", "td"]):
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
