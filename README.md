# **Sysco Catalog Scraper**

This project scrapes product data (SKUs and product details) from Sysco's catalog across multiple categories.  
It uses **Playwright**, **asyncio**, and a **queue-based worker system** for concurrency and fault-tolerance.

---

## **1. Categories**

The scraper runs **category-by-category**. Categories are predefined URLs:

- Meat & Seafood  
- Bakery & Bread  
- Beverages  
- Canned & Dry  
- Chemicals  
- Dairy & Eggs  
- Disposables  
- Equipment & Supplies  
- Frozen Foods  
- Fruits & Vegetables  
- Produce  

Example category URL:
https://shop.sysco.com/app/catalog?BUSINESS_CENTER_ID=syy_cust_tax_meatseafood

---

## **2. Catalog Workers (SKU Collection)**

- Before scraping products, we gather **all SKUs from all categories**.
- We first determine **total pages** for the category using the proper html element.
- Then divide by **24 products/page** to get the total pages, thats the logic of the website, 24 items per page.

- **Pages are split into chunks of 10**:
- Each catalog worker scrapes one chunk.
- Example: Worker 1 → pages 1–10, Worker 2 → pages 11–20, etc.

- SKUs are added to the **global queue**.
- After all categories are fully scraped, catalog workers close.

---

## **3. Product Workers (Product Details)**

- Once all SKUs are collected, **8 product workers** launch.  
- Each product worker:
1. Pulls a SKU from the queue.  
2. Logs in as guest (if required).  
3. Scrapes product details:  
   - brand  
   - name  
   - image  
   - description  
   - packaging  
   - category  
4. Marks SKU as done and moves to the next.

**User Agent**:
- This is how we handle multiple users, we use different user agents to make sure we are not detected.
- We use different zip codes, all based in oregon, and mimic a scroll to make sure we have human like attributes.

- **Idle detection**:
- If a product worker is idle for **10 seconds** and *does not* see the "Continue as Guest" button:
  - It kills itself.
  - Supervisor restarts a fresh worker.

- **Failed SKUs** are moved to a separate `failed_queue` for retry.

---

## **4. Retry & Export**

- After the main queue is empty:
- Failed SKUs are retried.
- Any that still fail are written to **`failed_skus.csv`**.

- **Products** are exported to **`products.csv`** with columns.

---

## **5. Workflow Summary**

1. For each category:
 - Calculate total pages.
 - Start multiple **catalog workers** (10 pages each) to gather SKUs.
2. After all categories finish:
 - Start **15 product workers** to scrape product details. (15 work well, trying to add more might start to overload my machine)
3. Retry failed SKUs.
4. Export all data to CSV.

---

## **Key Features**

- **Asynchronous** using `asyncio` for high concurrency.
- **Fault-tolerant** with automatic worker restarts.
- **Scalable** by splitting catalog scraping into page chunks.
- **Multi-category** support (runs all categories sequentially).

---

## **Run Instructions**

1. Install dependencies:
 ```bash
 pip install -r requirements.txt
 playwright install


