import asyncio
import re

async def scrape_product_details(context, url, sku):
    """Scrape product details from product page."""
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded")

    print(f"[INFO] Scraping product {sku} -> {url}")

    # Expand description if possible
    read_more_btn = await page.query_selector("button[data-id='ellipsis-read-more-button']")
    if read_more_btn:
        await read_more_btn.click()
        await asyncio.sleep(0.3)

    # Always try the full description first
    description_element = await page.query_selector(
        "div[data-id='product_description_section'] div.description-detail-wrapper:not(.LinesEllipsis)"
    )
    
    if description_element:
        description = await description_element.inner_text()
        print(f"[INFO] SKU {sku}: Full description found.")
    else:
        # Fallback: scrape truncated text (LinesEllipsis)
        print(f"[WARN] SKU {sku}: Full description not found. Using truncated text.")
        fallback_element = await page.query_selector(
            "div[data-id='product_description_text']"
        )
        description = await fallback_element.inner_text() if fallback_element else ""

    # Clean description
    description = re.sub(r"\s+", " ", description).strip()

    # Scrape other product info
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
