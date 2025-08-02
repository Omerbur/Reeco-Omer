from playwright.async_api import async_playwright
import asyncio

async def init_browser(user_agent):
    """Initialize WebKit browser, context, and page with user agent."""
    print("[INFO] Initializing browser...")
    await asyncio.sleep(1)
    playwright = await async_playwright().start()
    browser = await playwright.webkit.launch(headless=False)
    context = await browser.new_context(user_agent=user_agent)
    page = await context.new_page()
    return browser, context, page


async def login_flow(page, catalog_url, silent=False):
    """
    Full login flow:
    - Go to catalog
    - Wait for Continue as Guest
    - Enter ZIP code and press Start Shopping
    If silent=True, only click continue as guest if detected (for idle workers)
    """
    try:
        if not silent:
            
            print("[INFO] Starting guest login...")
            await page.goto(catalog_url, wait_until="domcontentloaded")

        # Check if Continue as Guest is visible
        await page.wait_for_selector("button:has-text('Continue as Guest')", timeout=15000)
        btn = await page.query_selector("button:has-text('Continue as Guest')")
        if btn:
            print("[INFO] Clicking Continue as Guest")
            await btn.click()

            await page.wait_for_selector("input[data-id='initial_zipcode_modal_input']", timeout=15000)
            await page.fill("input[data-id='initial_zipcode_modal_input']", "97229")

            await page.click("button[data-id='initial_zipcode_modal_start_shopping_button']")
            print("[INFO] Entered ZIP and clicked Start Shopping")

            # Wait to ensure page transition
            await asyncio.sleep(2)

        elif not silent:
            print("[WARN] Continue as Guest not found on login flow")

    except Exception as e:
        print(f"[WARN] Login flow exception (silent={silent}): {e}")
