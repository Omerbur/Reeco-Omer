import csv

def export_to_csv(data, filename="products.csv"):
    """Export scraped data to CSV."""
    if not data:
        print("[INFO] No data to export.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["sku", "brand", "name", "image", "description", "packaging"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"[INFO] Data successfully exported to {filename}")
