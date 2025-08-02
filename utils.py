import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Predefined list of common desktop user agents (no mobile)
DESKTOP_USER_AGENTS = [
    # Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    # macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

def setup_driver():
    chrome_options = Options()

    # Rotate User-Agent (desktop only)
    user_agent = random.choice(DESKTOP_USER_AGENTS)
    print(f"[DEBUG] Using User-Agent: {user_agent}")
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Anti-bot flags
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    return driver


def random_delay(min_seconds=2, max_seconds=5):
    """Wait a random amount of time (default 2-5 seconds)"""
    delay = random.uniform(min_seconds, max_seconds)
    print(f"[DEBUG] Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


def save_to_csv(products, filename="products.csv"):
    import csv

    keys = products[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)
    print(f"[INFO] Saved {len(products)} products to {filename}")
