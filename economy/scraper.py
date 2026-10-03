from decimal import Decimal
from enum import StrEnum
from typing import Any

from playwright.sync_api import sync_playwright


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


class Scraper:
    EXTRACTORS = (
        lambda data: data.strip() if isinstance(data, str) else data,
        lambda data: data.strip() if isinstance(data, str) else data,
        _parse_item_price,
        lambda data: data.strip() if isinstance(data, str) else data,
    )

    def __init__(self, region: Region = Region.EU) -> None:
        self._region = region
        self._update_base_url()

    @property
    def region(self) -> Region:
        return self._region

    @region.setter
    def region(self, new_region: Region) -> None:
        self._region = new_region
        self._update_base_url()

    def scrape_item(self, item_id: int) -> dict[str, Any]:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=False, executable_path="/usr/bin/chromium-browser"
            )

            page = browser.new_page()

            # Optimization, only html
            page.route(
                "**/*.{png,jpg,jpeg,gif,svg,css,font,woff,woff2}",
                lambda route: route.abort(),
            )

            target_url = f"{self._base_url}/{item_id}"

            try:
                page.goto(target_url)
                page.wait_for_selector("div.list table tbody tr")

                item_name = page.locator('a[href*="wowhead"]').inner_text()
                servers_rows = page.evaluate("""
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
                price = int(best_price_server[2]), int(best_price_server[2] % 1 * 100)

                return {
                    "region": self.region.value[1:3],
                    "item_id": item_id,
                    "name": item_name,
                    "server": best_price_server[0],
                    "price": f"{price[0]}g {price[1]}s",
                    "count": best_price_server[3],
                    "status": "success",
                }

            except Exception as e:
                raise RuntimeError(f"Failed to scrap item {item_id}") from e
            finally:
                browser.close()

    def _update_base_url(self) -> None:
        self._base_url = f"https://undermine.exchange/{self.region.value}"
