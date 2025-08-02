from playwright.async_api import Page
from .utils import random_delay

async def scrape_catalog_page(page: Page):
    print("[INFO] Hovering over Products dropdown...")
    await page.wait_for_selector("div.nav-link.active")
    await page.hover("div.nav-link.active")
    await random_delay()

    print("[INFO] Clicking Meat & Seafood category...")
    await page.wait_for_selector("li.dropdown-item a div.products-menu-item:has-text('Meat & Seafood')")
    await page.click("li.dropdown-item a div.products-menu-item:has-text('Meat & Seafood')")
    await random_delay()

    print("[INFO] Collecting product SKUs...")
    await page.wait_for_selector("div.catalog-cards-wrapper div.selectable-supc-label span")
    elements = await page.query_selector_all("div.catalog-cards-wrapper div.selectable-supc-label span")

    skus = [await el.inner_text() for el in elements]
    print(f"[INFO] Found {len(skus)} SKUs")
    return skus
