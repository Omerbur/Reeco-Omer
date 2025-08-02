from playwright.async_api import Page
from .utils import random_delay

async def login_as_guest(page: Page):
    print("[INFO] Starting guest login...")
    await page.wait_for_selector("button:has-text('Continue as Guest')")
    await page.click("button:has-text('Continue as Guest')")
    await random_delay()

    print("[INFO] Entering ZIP Code...")
    await page.fill("input[data-id='initial_zipcode_modal_input']", "97229")
    await random_delay()

    await page.click("button[data-id='initial_zipcode_modal_start_shopping_button']")
    print("[INFO] Clicked Start Shopping")
    await random_delay()
