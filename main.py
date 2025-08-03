import asyncio
from scraper.worker_manager import run_scraper

if __name__ == "__main__":
    asyncio.run(run_scraper())
