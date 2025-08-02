from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scraper.product import Product
from utils import random_delay

class Page:
    def __init__(self, driver, max_products=24):
        self.driver = driver
        self.max_products = max_products

        # Xpaths
        self.xpaths = {
            "guest_button": "//button[contains(., 'Continue as Guest')]",
            "zip_input": "//input[@data-id='initial_zipcode_modal_input']",
            "start_shopping": "//button[contains(., 'Start Shopping')]",
            "product_cards": "//div[contains(@class, 'product-card-wrapper')]"
        }

    def handle_guest_login(self):
        wait = WebDriverWait(self.driver, 15)

        print("[DEBUG] Looking for 'Continue as Guest' button...")
        try:
            guest_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.xpaths["guest_button"]))
            )
            guest_button.click()
            print("[INFO] Clicked 'Continue as Guest'")
            random_delay()
        except TimeoutException:
            print("[WARN] 'Continue as Guest' button not found")

        print("[DEBUG] Looking for ZIP input...")
        try:
            zip_input = wait.until(
                EC.presence_of_element_located((By.XPATH, self.xpaths["zip_input"]))
            )
            zip_input.clear()
            zip_input.send_keys("97229")
            print("[INFO] Entered ZIP code: 97229")
        except TimeoutException:
            print("[ERROR] ZIP input field not found")
            return

        print("[DEBUG] Looking for 'Start Shopping' button...")
        try:
            start_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.xpaths["start_shopping"]))
            )
            start_button.click()
            print("[INFO] Clicked 'Start Shopping'")
            random_delay()
        except TimeoutException:
            print("[ERROR] Start Shopping button not found")

    def get_products(self):
        print("[INFO] Starting guest login flow...")
        self.handle_guest_login()

        wait = WebDriverWait(self.driver, 15)
        products = []
        idx = 0

        while len(products) < self.max_products:
            print("[DEBUG] Refreshing product list...")
            product_cards = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, self.xpaths["product_cards"]))
            )
            print(f"[INFO] Found {len(product_cards)} product cards")

            if idx >= len(product_cards):
                break

            print(f"\n[INFO] Processing product {idx+1}/{self.max_products}")
            card = product_cards[idx]
            product = Product.from_card(card, self.driver)

            if product:
                products.append(product)
                print(f"[INFO] Product {idx+1} processed successfully")
            else:
                print(f"[WARN] Product {idx+1} failed")

            idx += 1
            random_delay()

        return products
