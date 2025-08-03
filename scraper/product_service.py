import asyncio
from scraper.login_page import init_browser, login_flow
from scraper.product_page import scrape_product_details

CATALOG_URL = "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_meatseafood"

async def product_worker(
    worker_id: int,
    queue: asyncio.Queue,
    failed_queue: asyncio.Queue,
    results: list,
    delay_before_scraping: float = 0.0  # Add delay param (default = no delay)
):
    """Scrape products from the queue."""
    from scraper.utils import get_random_user_agent

    user_agent = get_random_user_agent()
    browser, context, page = await init_browser(user_agent)

    idle_time = 0
    try:
        await login_flow(page, CATALOG_URL)

        while True:
            try:
                sku = await asyncio.wait_for(queue.get(), timeout=3)
            except asyncio.TimeoutError:
                idle_time += 3

                found = await login_flow(page, CATALOG_URL, silent=True)
                if found:
                    idle_time = 0

                # Kill worker if idle for 10s
                if idle_time >= 10:
                    print(f"[WORKER-{worker_id}] Idle for too long, killing self...")
                    break
                continue

            idle_time = 0

            if sku is None:
                queue.task_done()
                break

            url = f"https://shop.sysco.com/app/product-details/opco/052/product/{sku}?seller_id=USBL"
            try:
                # Delay if set (for retrying failed SKUs)
                if delay_before_scraping > 0:
                    await asyncio.sleep(delay_before_scraping)

                data = await scrape_product_details(context, url, sku)
                results.append(data)

                if len(results) % 50 == 0:
                    print(f"[INFO] {len(results)} products scraped...")

                print(f"[WORKER-{worker_id}] Scraped SKU: {sku}")

            except Exception as e:
                print(
                    f"[ERROR] Worker-{worker_id}: Failed SKU {sku}, moving to failed queue. Error: {e}"
                )
                await failed_queue.put(sku)
            finally:
                queue.task_done()

    finally:
        await browser.close()
