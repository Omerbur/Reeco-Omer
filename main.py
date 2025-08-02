import asyncio
from playwright.async_api import async_playwright
from scraper.utils import get_random_user_agent
from scraper.login_page import login_as_guest
from scraper.catalog_page import scrape_catalog_page
from scraper.product_page import scrape_product_details

async def run_scraper():
    async with async_playwright() as p:
        print("[INFO] Starting scraper with WebKit...")
        browser = await p.webkit.launch(headless=False, slow_mo=300)
        context = await browser.new_context(user_agent=get_random_user_agent())
        page = await context.new_page()

        await page.goto("https://shop.sysco.com/app/catalog")

        # Login flow
        await login_as_guest(page)

        # Go to catalog and get SKUs
        skus = await scrape_catalog_page(page)
        if not skus:
            print("[ERROR] No SKUs found, stopping...")
            await browser.close()
            return

        # Scrape first product for test
        product_data = await scrape_product_details(page, skus[0])
        print("[INFO] Sample product:", product_data)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
