import asyncio
from scraper.login_page import init_browser, login_as_guest
from scraper.catalog_page import navigate_to_category, collect_skus
from scraper.pagination import paginate_and_collect_skus
from scraper.product_page import scrape_product_details
from scraper.exporter import export_to_csv
from scraper.utils import get_random_user_agent

CATALOG_URL = "https://shop.sysco.com/app/catalog"

async def scrape_category(category_name, user_agent, export_filename):
    print(f"[INFO] Starting browser for {category_name}...")
    browser, context, page = await init_browser(user_agent)

    try:
        # Login
        await login_as_guest(page, CATALOG_URL)

        # Navigate to category and collect initial SKUs
        await navigate_to_category(page, category_name)
        skus = await collect_skus(page)
        print(f"[INFO] ({category_name}) Found initial {len(skus)} SKUs")

        results = []

        async def paginate_task():
            await paginate_and_collect_skus(page, skus, max_pages=2)

        async def scrape_products_task():
            processed = set()
            while True:
                if not skus:
                    await asyncio.sleep(0.5)
                    continue

                for sku in list(skus):
                    if sku in processed:
                        continue
                    url = f"https://shop.sysco.com/app/product-details/opco/052/product/{sku}?seller_id=USBL"
                    data = await scrape_product_details(context, url, sku)
                    results.append(data)
                    processed.add(sku)

                if len(processed) >= len(skus):
                    break
                await asyncio.sleep(0.2)

        await asyncio.gather(paginate_task(), scrape_products_task())

        print(f"[INFO] ({category_name}) Scraped {len(results)} products total.")
        export_to_csv(results, filename=export_filename)

    finally:
        await browser.close()

async def run_scraper():
    ua1 = get_random_user_agent()
    ua2 = get_random_user_agent()
    ua3 = get_random_user_agent()

    await asyncio.gather(
        scrape_category("Meat & Seafood", ua1, "meat_seafood.csv"),
        scrape_category("Dairy & Eggs", ua2, "dairy_eggs.csv"),
        scrape_category("Canned & Dry", ua3, "canned_dry.csv")
    )

if __name__ == "__main__":
    asyncio.run(run_scraper())
