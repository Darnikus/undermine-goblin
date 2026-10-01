from playwright.sync_api import Locator, sync_playwright


def parse_item_price(cell: Locator) -> str:
    gold_locator = cell.locator("span span.gold")
    silver_locator = cell.locator("span span.silver")

    price_parts = []

    if gold_locator.count() > 0 and gold_locator.inner_text().strip():
        price_parts.append(f"{gold_locator.inner_text().strip()}g")

    if silver_locator.count() > 0 and silver_locator.inner_text().strip():
        price_parts.append(f"{silver_locator.inner_text().strip()}s")

    return " ".join(price_parts) if price_parts else "0s"


with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False, executable_path="/usr/bin/chromium-browser"
    )

    page = browser.new_page()
    page.goto("https://undermine.exchange/#us-akama/856")

    print("The page has been loaded")

    print(f"Item's name {page.locator('a[href*="wowhead"]').inner_text()}")

    page.wait_for_selector("div.list table")

    servers_rows: list[Locator] = page.locator(
        "div.list table tr:not([data-connected-realm])"
    ).all()
    servers_data = []

    extractors = [
        lambda cell: cell.inner_text().strip(),
        lambda cell: cell.inner_text().strip(),
        parse_item_price,
        lambda cell: cell.inner_text().strip(),
    ]

    for row in servers_rows:
        cells: list[Locator] = row.locator("td, th").all()

        row_values = [
            extractor(cell) for extractor, cell in zip(extractors, cells, strict=False)
        ]

        if row_values and row_values[3].isdigit():
            servers_data.append(row_values)

    for i in servers_data:
        print(i)

    browser.close()
