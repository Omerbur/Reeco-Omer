from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service()
    return webdriver.Chrome(service=service, options=options)

def save_to_csv(products, filename):
    headers = ["Brand", "Name", "SKU", "Image URL", "Product URL", "Description"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for p in products:
            writer.writerow(p)
