import asyncio
import csv
from scraper.login_page import init_browser, login_flow
from scraper.pagination import get_total_pages
from scraper.catalog_service import catalog_worker
from scraper.product_service import product_worker
from scraper.exporter import export_to_csv
from scraper.utils import get_random_user_agent

CATEGORIES = [
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_meatseafood",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_bakerybread",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_beverages",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_canneddry",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_chemicals",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_dairyeggs",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_disposables",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_equipmentsupplies",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_frozenfoods",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_fruitvegetables",
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_produce"
]

def export_failed_skus(failed_skus, filename="failed_skus.csv"):
    """Export failed SKUs to a separate CSV."""
    if not failed_skus:
        print("[INFO] No failed SKUs to export.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["sku"])
        for sku in failed_skus:
            writer.writerow([sku])

    print(f"[INFO] Failed SKUs successfully exported to {filename}")


async def run_scraper():
    queue = asyncio.Queue()
    failed_queue = asyncio.Queue()
    results = []
    catalog_done = asyncio.Event()

    # Step 1: Iterate through categories and scrape SKUs
    for category_url in CATEGORIES:
        print(f"\n[INFO] Starting category: {category_url}")
        user_agent = get_random_user_agent()
        browser, context, page = await init_browser(user_agent)
        await login_flow(page, category_url)
        total_pages = await get_total_pages(page)
        await browser.close()

        # Spawn catalog workers
        chunk_size = 10
        catalog_tasks = []
        for start_page in range(1, total_pages + 1, chunk_size):
            end_page = min(start_page + chunk_size - 1, total_pages)
            catalog_tasks.append(
                asyncio.create_task(catalog_worker(queue, start_page, end_page, category_url))
            )

        print(f"[INFO] Launching {len(catalog_tasks)} catalog workers for this category...")
        await asyncio.gather(*catalog_tasks)
        print(f"[INFO] Finished category {category_url}, total SKUs in queue so far: {queue.qsize()}")

    catalog_done.set()

    # Step 2: Launch product workers
    print("\n[INFO] Launching product workers...")
    workers = [
        asyncio.create_task(product_worker(i + 1, queue, failed_queue, results, catalog_done))
        for i in range(8)
    ]
    await queue.join()

    # Export products after queue is done
    export_to_csv(results, "products.csv")
    print(f"[INFO] Exported {len(results)} products to products.csv")

    # Stop workers
    for _ in workers:
        await queue.put(None)
    await asyncio.gather(*workers)

    # Step 3: Retry failed SKUs and export them
    failed_skus = []
    while not failed_queue.empty():
        failed_skus.append(await failed_queue.get())

    export_failed_skus(failed_skus, "failed_skus.csv")
    print(f"[INFO] Scraping completed. {len(results)} products scraped, {len(failed_skus)} failed SKUs.")
