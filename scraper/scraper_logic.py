import re

async def scrape_product_details(context, url, sku):
    """Scrape product details including category."""
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded")

    brand = await page.inner_text("button[data-id='product_brand_link']")
    name = await page.inner_text("div[data-id='product_name']")
    image = await page.get_attribute("img[data-id='main-product-img-v2']", "src")

    # Scrape category from breadcrumb button
    category_element = await page.query_selector("button[data-id='breadcrumb_category_level1']")
    category = await category_element.inner_text() if category_element else "N/A"

    # Scrape description
    description_element = await page.query_selector("div.description-detail-wrapper")
    description = await description_element.inner_text() if description_element else ""
    description = re.sub(r"\s+", " ", description).strip()

    packaging = await page.inner_text("div[data-id='pack_size']")

    await page.close()

    return {
        "sku": sku,
        "brand": brand.strip(),
        "name": name.strip(),
        "image": image.strip() if image else "",
        "description": description,
        "packaging": packaging.strip(),
        "category": category.strip()
    }
