import asyncio
import math

async def get_total_pages(page):
    """Get total number of pages in category."""
    await asyncio.sleep(1)
    total_results_element = await page.query_selector(
        "span[data-id='ss-searchPage-header-label-searchResultsTotalText']"
    )
    if not total_results_element:
        print("[WARN] Could not find total results element, assuming 1 page")
        return 1

    text = await total_results_element.inner_text()
    total_results = int("".join(filter(str.isdigit, text)))
    pages = math.ceil(total_results / 24)
    print(f"[INFO] Total results: {total_results} -> {pages} pages")
    return pages


async def paginate_chunk(page, collected_skus, start_page, end_page):
    """Paginate only through a specific chunk of pages."""
    current_page = start_page
    while current_page < end_page:
        await asyncio.sleep(1)

        next_button = await page.query_selector("button[data-id='button_page_next']")
        if not next_button:
            print(f"[INFO] No next page found at page {current_page}, stopping chunk.")
            break

        await next_button.click()
        current_page += 1
        await page.wait_for_selector("div.catalog-cards-wrapper div.product-card-container", timeout=15000)

        elements = await page.query_selector_all("div.catalog-cards-wrapper div.product-card-container")
        for element in elements:
            sku_span = await element.query_selector("div.selectable-supc-label span")
            sku = (await sku_span.inner_text()).strip()
            if sku not in collected_skus:
                collected_skus.append(sku)
                print(f"[INFO] Added SKU: {sku} (page {current_page})")

    return collected_skus