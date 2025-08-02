from playwright.async_api import async_playwright
import asyncio
from scraper.utils import get_random_user_agent

async def init_browser():
    """Initialize WebKit browser, context, and page with rotating user-agent."""
    playwright = await async_playwright().start()
    user_agent = get_random_user_agent()
    print(f"[INFO] Launching WebKit with User-Agent: {user_agent}")

    browser = await playwright.webkit.launch(headless=False)
    context = await browser.new_context(user_agent=user_agent)
    page = await context.new_page()
    return browser, context, page

async def login_as_guest(page, catalog_url):
    """Handles the guest login flow on the Sysco site."""
    print("[INFO] Starting guest login...")

    await page.goto(catalog_url, wait_until="domcontentloaded")

    # Click Continue as Guest
    await page.wait_for_selector("button:has-text('Continue as Guest')", timeout=15000)
    await page.click("button:has-text('Continue as Guest')")
    
    # Enter ZIP code
    print("[INFO] Entering ZIP Code...")
    await page.wait_for_selector("input[data-id='initial_zipcode_modal_input']", timeout=15000)
    await page.fill("input[data-id='initial_zipcode_modal_input']", "97229")

    # Click Start Shopping
    await page.click("button[data-id='initial_zipcode_modal_start_shopping_button']")

    # Wait for dropdown menu to load
    await asyncio.sleep(1.5)
    print("[INFO] Clicked Start Shopping")
