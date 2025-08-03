import asyncio
from scraper.login_page import init_browser, login_flow
from scraper.pagination import get_total_pages
from scraper.catalog_service import catalog_worker
from scraper.product_service import product_worker
from scraper.exporter import export_to_csv
from scraper.utils import get_random_user_agent

# All categories to scrape
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
    "https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_produce",
]

async def run_scraper():
    queue = asyncio.Queue()
    failed_queue = asyncio.Queue()
    results = []

    # Step 1: Collect all SKUs from all categories
    for category_url in CATEGORIES:
        user_agent = get_random_user_agent()
        browser, context, page = await init_browser(user_agent)
        await login_flow(page, category_url)
        total_pages = await get_total_pages(page)
        await browser.close()

        # Create catalog workers: each handles 10 pages
        chunk_size = 10
        catalog_tasks = []
        for start_page in range(1, total_pages + 1, chunk_size):
            end_page = min(start_page + chunk_size - 1, total_pages)
            catalog_tasks.append(
                asyncio.create_task(catalog_worker(queue, start_page, end_page, category_url))
            )

        print(f"[INFO] Launching {len(catalog_tasks)} catalog workers for category: {category_url}")
        await asyncio.gather(*catalog_tasks)

    print(f"[INFO] Finished collecting SKUs from all categories. Total SKUs in queue: {queue.qsize()}")

    # Step 2: Start product workers
    workers = [
        asyncio.create_task(product_worker(i + 1, queue, failed_queue, results, delay_before_scraping=0.2))
        for i in range(15)
    ]
    await queue.join()

    # Stop workers
    for _ in workers:
        await queue.put(None)
    await asyncio.gather(*workers)

    # Step 3: Retry failed SKUs
    if not failed_queue.empty():
        print(f"[INFO] Retrying {failed_queue.qsize()} failed SKUs...")
        retry_results = []
        retry_failed_queue = asyncio.Queue()

        # Put failed SKUs into a retry queue
        retry_queue = asyncio.Queue()
        while not failed_queue.empty():
            await retry_queue.put(await failed_queue.get())

        retry_workers = [
            asyncio.create_task(
                product_worker(
                    i + 1, retry_queue, retry_failed_queue, retry_results, delay_before_scraping=0.2
                )
            )
            for i in range(5)
        ]

        await retry_queue.join()

        for _ in retry_workers:
            await retry_queue.put(None)
        await asyncio.gather(*retry_workers)

        print(f"[INFO] Retry pass complete. {len(retry_results)} products scraped on retry.")

        # Export any remaining failed SKUs
        if not retry_failed_queue.empty():
            with open("failed_skus.csv", "w") as f:
                f.write("sku\n")
                while not retry_failed_queue.empty():
                    f.write(f"{await retry_failed_queue.get()}\n")
            print(f"[INFO] {retry_failed_queue.qsize()} SKUs still failed. Saved to failed_skus.csv.")

    # Step 4: Export products
    export_to_csv(results, "products.csv")
    print(f"[INFO] Scraping completed. {len(results)} products scraped successfully.")

if __name__ == "__main__":
    asyncio.run(run_scraper())
