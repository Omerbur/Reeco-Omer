import asyncio

async def navigate_to_category(page, category_name):
    """Hover over Products dropdown and click a category."""
    print("[INFO] Hovering over Products dropdown...")
    await page.wait_for_selector("div.nav-link.active", timeout=15000)
    await page.hover("div.nav-link.active")

    print(f"[INFO] Clicking {category_name} category...")
    await page.wait_for_selector(f"li.dropdown-item div.products-menu-item:has-text('{category_name}')", timeout=15000)
    await page.click(f"li.dropdown-item div.products-menu-item:has-text('{category_name}')")


async def collect_skus(page):
    """Collect all product SKUs from the category page."""
    print("[INFO] Collecting product SKUs...")
    await page.wait_for_selector("div.catalog-cards-wrapper div.product-card-container", timeout=15000)

    elements = await page.query_selector_all("div.catalog-cards-wrapper div.product-card-container")
    skus = []

    for element in elements:
        sku_span = await element.query_selector("div.selectable-supc-label span")
        sku = await sku_span.inner_text()
        skus.append(sku.strip())

    return skus
