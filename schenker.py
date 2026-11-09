"""Fetch a DB Schenker tracking page and turn it into markdown tables."""

import logging

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

TRACKING_URL = "https://www.dbschenker.com/app/tracking-public/?refNumber="

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
)

# Time limits for the browser, in milliseconds.
PAGE_TIMEOUT_MS = 30_000
CLICK_TIMEOUT_MS = 5_000

# CSS selectors for the parts of the page we read.
DETAILS_SELECTOR = (
    ".tracking-details-header, .tracking-details-value, "
    "[data-test='service_name_value'], [data-test='consignee_reference_value'], "
    "[data-test='shipper_reference_value']"
)
HISTORY_SELECTOR = ".pt-table.ng-star-inserted"


async def get_soup_from_url(url: str) -> BeautifulSoup | None:
    """Open the page in a headless browser and return the parsed HTML.

    The page builds its content with JavaScript, so a real browser is needed.
    The "See more" button is clicked so the full shipment history is shown.
    Returns None if the page could not be loaded.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            context = await browser.new_context(user_agent=USER_AGENT)
            page = await context.new_page()
            page.set_default_timeout(PAGE_TIMEOUT_MS)
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            # Show the full history. The button is missing when the shipment is not found.
            try:
                await page.get_by_text("See more").first.click(timeout=CLICK_TIMEOUT_MS)
                await page.wait_for_load_state("networkidle")
            except Exception as e:
                logger.warning("Could not click 'See more': %s", e)

            return BeautifulSoup(await page.content(), "html.parser")
        except Exception as e:
            logger.error("Failed to load %s: %s", url, e)
            return None
        finally:
            await browser.close()


def details(elements) -> str:
    """Turn a flat list of key and value elements into a two column markdown table.

    The page lists keys and values one after another. The consignment number is
    a special case, since it is followed by both a consignment and a waybill number.
    """
    rows = ["| Key | Value |", "| --- | --- |"]
    texts = [el.get_text(strip=True) for el in elements]
    i = 0
    while i < len(texts):
        key = texts[i]
        value = texts[i + 1] if i + 1 < len(texts) else ""
        if (
            key == "Consignment Number/Waybill Number"
            and i + 2 < len(texts)
            and texts[i + 2].isdigit()
        ):
            rows.append(f"| {key} | {value}/{texts[i + 2]} |")
            i += 3
            continue
        rows.append(f"| {key} | {value} |")
        i += 2
    return "\n".join(rows) + "\n"


def history(table) -> str:
    """Turn the shipment history table into a markdown table.

    The first cell of each row is an empty icon column and is skipped.
    Reading stops at the first row with a cell that starts with "Package",
    because that row and the rows after it belong to the per package section.
    Returns an empty string if there is no table or it has no rows.
    """
    if table is None:
        return ""

    table_data = []
    for row in table.find_all("tr"):
        row_data = []
        stop = False
        for cell in row.find_all(["th", "td"])[1:]:
            text = cell.get_text(strip=True)
            if text.startswith("Package"):
                stop = True
                break
            row_data.append(text or "-")
        if stop:
            break
        if row_data:
            table_data.append(row_data)

    if not table_data:
        return ""

    header, *body = table_data
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    lines += ["| " + " | ".join(row) + " |" for row in body]
    return "\n".join(lines) + "\n"


def parse_tracking_page(soup: BeautifulSoup) -> str | None:
    """Build the markdown report from a tracking page.

    Returns None if the page has no shipment details and no history,
    which usually means the tracking number was not found.
    """
    detail_elements = soup.select(DETAILS_SELECTOR)
    history_out = history(soup.select_one(HISTORY_SELECTOR))
    if not detail_elements and not history_out:
        return None

    parts = []
    if detail_elements:
        parts.append(details(detail_elements))
    if history_out:
        parts.append(history_out)
    return "\n".join(parts)
