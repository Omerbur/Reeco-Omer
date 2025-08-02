import sys
import os

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.page import Page
from scraper.website import xpaths
from utils import setup_driver
from utils.exporter import save_to_csv


if __name__ == "__main__":
    driver = setup_driver()
    try:
        page = Page(driver, xpaths, max_products=24)
        products = page.get_products()
        save_to_csv(products, "products.csv")
    finally:
        driver.quit()
