import re

async def scrape_product_details(context, url, sku):
    """Scrape product details from product page."""
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded")

    print(f"[INFO] Scraping product {sku} -> {url}")

    # Scrape directly from description-detail-wrapper
    description_element = await page.query_selector("div.description-detail-wrapper")

    if description_element:
        description = await description_element.inner_text()
        print(f"[INFO] SKU {sku}: Scraped description from description-detail-wrapper.")
    else:
        print(f"[WARN] SKU {sku}: Description element not found.")
        description = ""

    description = re.sub(r"\s+", " ", description).strip()

    # Other product data
    brand = await page.inner_text("button[data-id='product_brand_link']")
    name = await page.inner_text("div[data-id='product_name']")
    image = await page.get_attribute("img[data-id='main-product-img-v2']", "src")
    packaging = await page.inner_text("div[data-id='pack_size']")

    await page.close()

    return {
        "sku": sku,
        "brand": brand.strip(),
        "name": name.strip(),
        "image": image.strip() if image else "",
        "description": description,
        "packaging": packaging.strip()
    }
