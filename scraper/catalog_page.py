async def go_to_category_url(page, category_url):
    """Navigate directly to category URL after login."""
    print(f"[INFO] Navigating to category URL: {category_url}")
    await page.goto(category_url, wait_until="domcontentloaded")
    await page.wait_for_selector("div.catalog-cards-wrapper div.product-card-container", timeout=15000)


async def collect_skus(page):
    """Collect all product SKUs from the current category page."""
    print("[INFO] Collecting product SKUs from category...")
    await page.wait_for_selector("div.catalog-cards-wrapper div.product-card-container", timeout=15000)

    elements = await page.query_selector_all("div.catalog-cards-wrapper div.product-card-container")
    skus = []

    for element in elements:
        sku_span = await element.query_selector("div.selectable-supc-label span")
        sku = await sku_span.inner_text()
        skus.append(sku.strip())

    return skus
