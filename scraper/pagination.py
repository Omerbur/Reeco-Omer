import asyncio

async def paginate_and_collect_skus(page, collected_skus, max_pages=2):
    """
    Go through pages of catalog and collect new SKUs.
    Will stop after max_pages for now.
    """
    pages_scraped = 1
    print(f"[INFO] Pagination started. Max pages: {max_pages}")

    while pages_scraped < max_pages:
        # Wait a bit before clicking next page
        await asyncio.sleep(1)

        next_button = await page.query_selector("button[data-id='button_page_next']")
        if not next_button:
            print("[INFO] No next page button found. Ending pagination.")
            break

        print(f"[INFO] Moving to next page: {pages_scraped+1}")
        await next_button.click()
        await page.wait_for_selector("div.catalog-cards-wrapper div.product-card-container", timeout=15000)

        elements = await page.query_selector_all("div.catalog-cards-wrapper div.product-card-container")
        for element in elements:
            sku_span = await element.query_selector("div.selectable-supc-label span")
            sku = (await sku_span.inner_text()).strip()
            if sku not in collected_skus:
                collected_skus.append(sku)
                print(f"[INFO] Added new SKU: {sku}")

        pages_scraped += 1

    print(f"[INFO] Pagination finished. Total SKUs: {len(collected_skus)}")
    return collected_skus
