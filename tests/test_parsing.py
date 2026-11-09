from pathlib import Path

from bs4 import BeautifulSoup

from schenker import HISTORY_SELECTOR, history, parse_tracking_page

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> BeautifulSoup:
    return BeautifulSoup((FIXTURES / name).read_text(), "html.parser")


def test_full_page_report():
    report = parse_tracking_page(load("shipment.html"))
    assert "| Consignment Number/Waybill Number | 1806203236/12345678 |" in report
    assert "| Product | DB SCHENKER system |" in report
    assert "| Shipper Reference | REF-1 |" in report
    assert "| Date | Event | Location |" in report
    assert "| --- | --- | --- |" in report
    assert "| 2025-01-02 | Delivered | Stockholm |" in report
    # Empty cells become "-".
    assert "| 2025-01-01 | Collected | - |" in report


def test_history_stops_at_package_row():
    table = load("shipment.html").select_one(HISTORY_SELECTOR)
    out = history(table)
    assert isinstance(out, str)
    assert "Package" not in out
    assert "Malmo" not in out
    assert len(out.strip().splitlines()) == 4  # header, separator, two events


def test_history_missing_table():
    assert history(None) == ""


def test_history_empty_table():
    table = load("empty_table.html").select_one(HISTORY_SELECTOR)
    assert table is not None
    assert history(table) == ""


def test_not_found_page_returns_none():
    assert parse_tracking_page(load("not_found.html")) is None
    assert parse_tracking_page(load("empty_table.html")) is None
