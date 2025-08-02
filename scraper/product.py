class Product:
    def __init__(self, brand, name, sku, image_url, product_url, description):
        self.brand = brand
        self.name = name
        self.sku = sku
        self.image_url = image_url
        self.product_url = product_url
        self.description = description

    @staticmethod
    def from_card(card_element, driver):
        try:
            brand = card_element.find_element(By.CLASS_NAME, "brand-name").text
        except:
            brand = "Unknown"

        try:
            name = card_element.find_element(By.CLASS_NAME, "product-name").text
        except:
            name = "Unknown"

        try:
            sku = card_element.get_attribute("data-productid")
        except:
            sku = "Unknown"

        try:
            image_url = card_element.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            image_url = ""

        try:
            product_url = card_element.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            product_url = ""

        # Navigate to details page for description
        description = ""
        if product_url:
            driver.get(product_url)
            try:
                description = driver.find_element(By.CLASS_NAME, "description-detail-wrapper").text
            except:
                description = "No description"
            driver.back()

        return Product(brand, name, sku, image_url, product_url, description)
