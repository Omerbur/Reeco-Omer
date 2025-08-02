import asyncio
import time
from scraper.login_page import init_browser, login_flow
from scraper.catalog_page import go_to_category_url, collect_skus
from scraper.pagination import paginate_and_collect_skus
from scraper.product_page import scrape_product_details
from scraper.exporter import export_to_csv
from scraper.utils import get_random_user_agent

CATALOG_URL = "https://shop.sysco.com/app/catalog"
CATEGORY_URL = "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_meatseafood"


async def catalog_worker(queue: asyncio.Queue):
    user_agent = get_random_user_agent()
    browser, context, page = await init_browser(user_agent)

    try:
        # Full login flow and go to category URL directly
        await asyncio.sleep(1)
        await login_flow(page, CATALOG_URL)
        await go_to_category_url(page, CATEGORY_URL)

        skus = await collect_skus(page)
        skus = await paginate_and_collect_skus(page, skus, max_pages=5)

        print(f"[INFO] Catalog collected {len(skus)} SKUs")
        for sku in skus:
            await queue.put(sku)

    finally:
        await browser.close()
        print("[INFO] Catalog worker finished!")


async def product_worker(worker_id: int, queue: asyncio.Queue, failed_queue: asyncio.Queue, results: list):
    user_agent = get_random_user_agent()
    browser, context, page = await init_browser(user_agent)

    try:
        # Initial login
        await asyncio.sleep(1)
        await login_flow(page, CATALOG_URL)

        while True:
            try:
                sku = await asyncio.wait_for(queue.get(), timeout=4)
            except asyncio.TimeoutError:
                # Idle check -> re-login
                print(f"[WORKER-{worker_id}] Idle - checking login...")
                await login_flow(page, CATALOG_URL, silent=True)
                continue

            if sku is None:
                queue.task_done()
                break

            url = f"https://shop.sysco.com/app/product-details/opco/052/product/{sku}?seller_id=USBL"
            try:
                data = await scrape_product_details(context, url, sku)
                results.append(data)
                print(f"[WORKER-{worker_id}] Scraped SKU: {sku}")
            except Exception as e:
                print(f"[ERROR] Worker-{worker_id}: Failed SKU {sku}, moving to failed queue. Error: {e}")
                await failed_queue.put(sku)
            finally:
                queue.task_done()

    finally:
        await browser.close()


async def run_scraper():
    queue = asyncio.Queue()
    failed_queue = asyncio.Queue()
    results = []

    start_time = time.time()

    # Start catalog worker
    catalog = asyncio.create_task(catalog_worker(queue))

    # Delay to allow SKUs to queue up, then start product workers
    await asyncio.sleep(10)
    workers = [asyncio.create_task(product_worker(i + 1, queue, failed_queue, results)) for i in range(8)]

    # Wait for catalog worker to finish
    await catalog
    await queue.join()

    # Retry failed SKUs
    print(f"[INFO] Retrying {failed_queue.qsize()} failed SKUs...")
    while not failed_queue.empty():
        await queue.put(await failed_queue.get())

    await queue.join()

    # Signal workers to stop
    for _ in workers:
        await queue.put(None)
    await asyncio.gather(*workers)

    # Export CSV and stats
    export_to_csv(results, filename="products.csv")

    total_time = time.time() - start_time
    avg_time = total_time / len(results) if results else 0
    print(f"[INFO] Scraping completed. {len(results)} products scraped.")
    print(f"[INFO] Total time: {total_time:.2f}s | Avg per product: {avg_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(run_scraper())
