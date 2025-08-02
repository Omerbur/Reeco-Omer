import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Product:
    def __init__(self, brand, name, sku, image_url, product_url, description):
        self.brand = brand
        self.name = name
        self.sku = sku
        self.image_url = image_url
        self.product_url = product_url
        self.description = description

    @classmethod
    def from_card(cls, card, driver):
        wait = WebDriverWait(driver, 10)

        # Extract basic details from product card
        try:
            brand = card.find_element(By.XPATH, ".//div[contains(@class,'brand')]").text.strip()
        except:
            brand = "Unknown"

        try:
            name = card.find_element(By.XPATH, ".//div[contains(@class,'description')]").text.strip()
        except:
            name = "Unknown"

        try:
            sku = card.get_attribute("data-sku") or \
                  card.find_element(By.XPATH, ".//*[contains(text(),'SKU')]").text.strip()
            sku = sku.replace("SKU:", "").strip()
        except:
            sku = "Unknown"

        try:
            image_url = card.find_element(By.XPATH, ".//img").get_attribute("src")
        except:
            image_url = ""

        try:
            product_url = card.find_element(By.XPATH, ".//a").get_attribute("href")
        except:
            product_url = ""

        # Navigate into product page for description
        description = "No description found"
        if product_url:
            print(f"[INFO] Navigating to product page: {product_url}")
            driver.get(product_url)
            try:
                desc_element = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.description-detail-wrapper")
                    )
                )
                description = desc_element.text.strip()
            except TimeoutException:
                print("[WARN] Description not found, using fallback")
            finally:
                driver.back()
                time.sleep(1)

        return cls(brand, name, sku, image_url, product_url, description)

    def to_dict(self):
        return {
            "Brand": self.brand,
            "Name": self.name,
            "SKU": self.sku,
            "Image URL": self.image_url,
            "Product URL": self.product_url,
            "Description": self.description,
        }
