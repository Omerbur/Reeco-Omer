import csv


def save_to_csv(products, filename):
    print(f"[INFO] Saving {len(products)} products to {filename}")
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Brand", "Name", "SKU", "Image URL", "Product URL", "Description"])
        for p in products:
            writer.writerow([p.brand, p.name, p.sku, p.image_url, p.product_url, p.description])
