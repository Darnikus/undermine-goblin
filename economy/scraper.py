import logging
import os
import re
from contextlib import contextmanager
from decimal import Decimal
from enum import StrEnum
from typing import Any
from urllib.parse import urlparse, urlunparse

from playwright.sync_api import Page, sync_playwright

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scraper.log"), logging.StreamHandler()],
)


def _parse_item_price(price: list[str]) -> Decimal:
    gold = price[0].replace(",", "").strip()
    silver = price[1].replace(",", "").strip()

    return Decimal(f"{gold}.{silver}")


class Region(StrEnum):
    """Defines the regions available on Undermine.exchange."""

    US = "#us-akama"
    """North America (includes US, Oceania, and Latin American realms)"""
    EU = "#eu-arathi"
    """Europe"""
    TW = "#tw-menethil"
    """Taiwan"""
    KR = "#kr-azshara"
    """South Korea"""


@contextmanager
def managed_browser(headless=True):
    """Handles only the management of the browser lifecycle.

    Args:
        headless (bool, optional): True to open the browser in headless mode.
        Defaults to True.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            executable_path="/usr/bin/chromium-browser",
            args=[
                "--disable-blink-features=AutomationControled",
                "--start-maximized",
            ],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        try:
            yield page
        finally:
            context.close()
            browser.close()


class Scraper:
    EXTRACTORS = (
        lambda data: data.strip() if isinstance(data, str) else data,
        lambda data: data.strip() if isinstance(data, str) else data,
        _parse_item_price,
        lambda data: data.strip() if isinstance(data, str) else data,
    )

    def __init__(self, page: Page, region: Region = Region.EU) -> None:
        self.page: Page = page
        self._region = region
        self._update_base_url()

        # Optimization, only html
        self.page.route(
            "**/*.{png,jpg,jpeg,gif,svg,css,font,woff,woff2}",
            lambda route: route.abort(),
        )

    @property
    def region(self) -> Region:
        return self._region

    @region.setter
    def region(self, new_region: Region) -> None:
        self._region = new_region
        self._update_base_url()

    def scrape_item(self, item_id: str) -> dict[str, Any]:

        target_url = f"{self._base_url}/{item_id}"

        try:
            self.page.goto(target_url, wait_until="domcontentloaded")

            name_locator = self.page.locator('a[href*="wowhead"]')
            name_locator.first.wait_for(state="visible", timeout=5000)
            icon_locator = self.page.locator("span.title span.icon")

            self.page.wait_for_timeout(300)

            if self.page.locator("div.list").count() > 0:
                scraped_data = self._scrape_realm_specific_item()
            else:
                scraped_data = self._scrape_region_wide_item()

            icon_css_url = icon_locator.evaluate(
                "element => getComputedStyle(element)['background-image']"
            )

            scraped_data.update(
                {
                    "region": self.region.value[1:3],
                    "item_id": item_id,
                    "name": name_locator.inner_text(),
                    "url": target_url,
                    "icon_url": self._update_icon_url(icon_css_url),
                    "status": "success",
                }
            )
            return scraped_data

        except Exception as e:
            logging.error(f"Failed to scrap item (ID: `{item_id}`): {e}", exc_info=True)
            raise RuntimeError(f"Failed to scrap item {item_id}") from e

    def _scrape_realm_specific_item(self) -> dict[str, Any]:
        self.page.wait_for_selector("div.list table tbody tr", timeout=5000)
        servers_rows = self.page.evaluate("""
            () => {
                const rows = document.querySelectorAll(
                    'div.list table tbody tr:not([data-connected-realm])'
                );
                return Array.from(rows).map(row => {
                    const cells = row.querySelectorAll('td, th');
                    return Array.from(cells).map(cell => {
                        // Check for gold and silver spans
                        const goldSpan = cell.querySelector('.gold');
                        const silverSpan = cell.querySelector('.silver');

                        if (goldSpan || silverSpan) {
                            return [
                                goldSpan ? goldSpan.innerText.trim() : "0",
                                silverSpan ? silverSpan.innerText.trim() : "0"
                            ];
                        }
                        return cell.innerText.trim();
                    });
                });
            }
        """)  # Connected realms are filtered out as irrelevant.
        servers_data = []

        for row in servers_rows:
            row_values = [
                extractor(cell)
                for extractor, cell in zip(self.EXTRACTORS, row, strict=False)
            ]

            if row_values:
                servers_data.append(row_values)

        has_items_servers_data = [
            server for server in servers_data if server[3].isdigit()
        ]

        best_price_server = min(has_items_servers_data, key=lambda row: row[2])
        # price = int(best_price_server[2]), int(best_price_server[2] % 1 * 100)

        return {
            "server": best_price_server[0],
            "price": best_price_server[2],
            "count": best_price_server[3],
        }

    def _scrape_region_wide_item(self) -> dict[str, Any]:
        details_table = self.page.locator("table.hidden-region-details")

        count_locator = details_table.locator(
            "xpath=.//td[contains(., 'Available')]/following-sibling::td[1]"
        )
        price_locator = details_table.locator(
            "xpath=.//td[contains(., 'Current')]/following-sibling::td[1]"
        )

        not_parsed_price = price_locator.locator("span > span").all_inner_texts()
        price = _parse_item_price(not_parsed_price)

        return {
            "server": "Region-Wide",
            "price": price,
            "count": count_locator.inner_text(),
        }

    def _update_base_url(self) -> None:
        self._base_url = f"https://undermine.exchange/{self.region.value}"

    @staticmethod
    def _update_icon_url(
        css_value: str, target_size: str = "large", new_size: str = "medium"
    ) -> str:
        """Extracts the icon's URL from the CSS `background-image` value, then resizes
        it.

        Args:
            css_value (str): CSS `background-image` value.
            target_size (str, optional): Current icon's size. Defaults to "large".
            new_size (str, optional): Desired icon's size. Defaults to "medium".

        Raises:
            ValueError: Failed to excract the url.

        Returns:
            str: An icon's URL.
        """
        match = re.search(r'url\((?:[\'"]?)(.*?)(?:[\'"]?)\)', css_value)

        if match is None:
            raise ValueError(f"No background image URL in CSS: '{css_value}'")

        raw_url = match.group(1)
        parsed = urlparse(raw_url)
        parts = list(parsed)
        parts[2] = parts[2].replace(f"/{target_size}/", f"/{new_size}/")
        new_url = urlunparse(parts)

        return new_url
