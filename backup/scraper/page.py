import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from .product import Product


class Page:
    def __init__(self, driver, xpaths, max_products=24):
        self.driver = driver
        self.xpaths = xpaths
        self.max_products = max_products

    def handle_guest_login(self):
        wait = WebDriverWait(self.driver, 30)

        print("[DEBUG] Looking for 'Continue as Guest' button...")
        try:
            guest_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.xpaths["guest_button"]))
            )
            guest_button.click()
            print("[INFO] Clicked 'Continue as Guest'")
            time.sleep(1)
        except TimeoutException:
            print("[WARN] 'Continue as Guest' button not found (maybe already skipped)")

        print("[DEBUG] Looking for ZIP input by data-id='initial_zipcode_modal_input'...")
        zip_input = None
        attempts = 0

        while attempts < 3:
            try:
                # Directly use CSS selector for the data-id attribute
                zip_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-id='initial_zipcode_modal_input']"))
                )

                self.driver.execute_script("arguments[0].scrollIntoView(true);", zip_input)
                time.sleep(0.5)

                zip_input.clear()
                zip_input.send_keys("97229")
                print("[INFO] ZIP code entered successfully: 97229")
                break
            except (TimeoutException, ElementNotInteractableException) as e:
                attempts += 1
                print(f"[WARN] ZIP input failed (attempt {attempts}) -> {e}")
                time.sleep(1)

        if not zip_input:
            print("[ERROR] Unable to type ZIP code after multiple attempts")
            return

        print("[DEBUG] Looking for 'Start Shopping' button...")
        try:
            start_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.xpaths["start_shopping"]))
            )
            start_button.click()
            print("[INFO] Clicked 'Start Shopping'")
            time.sleep(2)
        except TimeoutException:
            print("[ERROR] Start Shopping button not found")

    def get_products(self):
        print("[INFO] Starting guest login flow...")
        self.handle_guest_login()

        wait = WebDriverWait(self.driver, 20)
        products = []
        idx = 0

        while len(products) < self.max_products:
            print("[DEBUG] Refreshing product list...")
            try:
                product_cards = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, self.xpaths["product_cards"]))
                )
                print(f"[INFO] Found {len(product_cards)} product cards")
            except TimeoutException:
                print("[ERROR] No product cards found")
                break

            if idx >= len(product_cards):
                break

            print(f"\n[INFO] Processing product {idx + 1}/{self.max_products}")
            card = product_cards[idx]

            start_time = time.time()
            product = Product.from_card(card, self.driver)

            if product:
                products.append(product)
                print(f"[INFO] Product {idx + 1} processed successfully")
            else:
                print(f"[WARN] Product {idx + 1} failed")

            end_time = time.time()
            print(f"[TIMER] Product {idx + 1} took {end_time - start_time:.2f} seconds")

            idx += 1

        return products
