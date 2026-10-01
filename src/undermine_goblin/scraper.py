from decimal import Decimal

from playwright.sync_api import Locator, sync_playwright


def parse_item_price(cell: Locator) -> Decimal:
    gold_locator = cell.locator("span span.gold")
    silver_locator = cell.locator("span span.silver")

    gold = (
        int(gold_locator.inner_text().strip().replace(",", ""))
        if gold_locator.count() > 0 and gold_locator.inner_text().strip()
        else 0
    )

    silver = (
        int(silver_locator.inner_text().strip())
        if silver_locator.count() > 0 and silver_locator.inner_text().strip()
        else 0
    )

    return Decimal(f"{gold}.{silver:02d}")


with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False, executable_path="/usr/bin/chromium-browser"
    )

    page = browser.new_page()
    page.goto("https://undermine.exchange/#us-akama/856")

    print("The page has been loaded")

    page.wait_for_selector("div.list table")

    servers_rows: list[Locator] = page.locator(
        "div.list table tr:not([data-connected-realm])"
    ).all()  # Connected realms are filtered out as irrelevant.
    servers_data = []

    extractors = [
        lambda cell: cell.inner_text().strip(),
        lambda cell: cell.inner_text().strip(),
        parse_item_price,
        lambda cell: cell.inner_text().strip(),
    ]

    # Get data from the servers table.
    for row in servers_rows[1:]:
        cells: list[Locator] = row.locator("td, th").all()

        row_values = [
            extractor(cell) for extractor, cell in zip(extractors, cells, strict=False)
        ]

        if row_values:
            servers_data.append(row_values)

    has_items_servers_data = [server for server in servers_data if server[3].isdigit()]

    print(has_items_servers_data)

    best_price_server = min(has_items_servers_data, key=lambda row: row[2])
    price = int(best_price_server[2]), int(best_price_server[2] % 1 * 100)

    print(
        f"Item: {page.locator('a[href*="wowhead"]').inner_text()}\n"
        + f"The best server to buy is {best_price_server[0]}\n"
        + f"Price: {price[0]}g {price[1]}s\n"
        + f"Count: {best_price_server[3]}"
    )

    browser.close()
