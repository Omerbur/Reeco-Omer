from utils import setup_driver
from scraper.page import Page
from utils import random_delay

if __name__ == "__main__":
    print("[INFO] Starting scraper...")
    driver = setup_driver()

    driver.get("https://shop.sysco.com/app/catalog")
    page = Page(driver, max_products=5)

    products = page.get_products()

    for p in products:
        print(f"{p.brand} | {p.name} | {p.sku} | {p.product_url}")

    driver.quit()
