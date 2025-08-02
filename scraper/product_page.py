from playwright.async_api import Page
from .utils import random_delay

async def scrape_product_details(page: Page, sku: str):
    url = f"https://shop.sysco.com/app/product-details/opco/052/product/{sku}?seller_id=USBL"
    print(f"[INFO] Navigating to product: {url}")
    await page.goto(url)
    await random_delay()

    brand = await page.inner_text("button[data-id='product_brand_link']")
    name = await page.inner_text("div.product-name[data-id='product_name']")
    img = await page.get_attribute("img[data-id='main-product-img-v2']", "src")
    description = await page.inner_text("div[data-id='product_description_section']")
    packaging = await page.inner_text("div.product-label[data-id='pack_size']")

    return {
        "sku": sku,
        "brand": brand,
        "name": name,
        "image": img,
        "description": description,
        "packaging": packaging
    }
