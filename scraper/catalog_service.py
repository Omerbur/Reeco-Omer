import asyncio
from scraper.catalog_page import collect_skus
from scraper.pagination import paginate_chunk
from scraper.login_page import init_browser, login_flow
from scraper.utils import get_random_user_agent

async def catalog_worker(queue: asyncio.Queue, start_page: int, end_page: int, catalog_url: str):
    """Scrape SKUs from assigned pages and push to queue."""
    user_agent = get_random_user_agent()
    browser, context, page = await init_browser(user_agent)

    try:
        await login_flow(page, catalog_url)

        # Jump directly to start page
        if start_page > 1:
            url = f"{catalog_url}&page={start_page}"
            print(f"[INFO] Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")

        # Initial SKUs
        skus = await collect_skus(page)
        for sku in skus:
            await queue.put(sku)
            print(f"[CATALOG] Added SKU: {sku}")

        # Paginate
        skus = await paginate_chunk(page, skus, start_page, end_page)
        for sku in skus:
            await queue.put(sku)
            print(f"[CATALOG] Added SKU: {sku}")

        print(f"[INFO] Catalog worker finished pages {start_page}-{end_page} -> {len(skus)} SKUs")

    finally:
        await browser.close()