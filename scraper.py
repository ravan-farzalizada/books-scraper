"""
Book scraper - Portfolio Project A

Collects title, price, rating, availability and URL for every book on
books.toscrape.com (a website built for scraping practice) and saves
the results to CSV and Excel.

Usage:
    python scraper.py
    python scraper.py --max-pages 3
    python scraper.py --url https://books.toscrape.com/ --output my_books
"""

import argparse
import logging
import re
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://books.toscrape.com/"
DEFAULT_OUTPUT = "books"          # creates books.csv and books.xlsx
DELAY_SECONDS = 1.5               # polite pause between requests
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PortfolioScraper/1.0)"}

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("scraper")


def fetch(url):
    """Download a page. Retries a few times if something goes wrong.
    Returns the HTML text, or None if every attempt failed."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = "utf-8"  # avoids broken symbols like "Â£"
            return response.text
        except requests.RequestException as error:
            log.warning("Attempt %d/%d failed for %s: %s", attempt, MAX_RETRIES, url, error)
            time.sleep(DELAY_SECONDS * attempt)  # wait longer after each failure
    log.error("Giving up on %s", url)
    return None


def parse_price(text):
    """Turn '£51.77' into the number 51.77."""
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def parse_page(html, page_url):
    """Read one page of results.
    Returns (list of book dicts, URL of the next page or None)."""
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for item in soup.select("article.product_pod"):
        try:
            link = item.select_one("h3 a")
            rating_tag = item.select_one("p.star-rating")
            rating_class = [c for c in rating_tag.get("class", []) if c != "star-rating"]
            books.append(
                {
                    "title": link["title"],
                    "price_gbp": parse_price(item.select_one("p.price_color").get_text()),
                    "rating": RATING_WORDS.get(rating_class[0] if rating_class else "", None),
                    "availability": item.select_one("p.availability").get_text(strip=True),
                    "url": urljoin(page_url, link["href"]),
                }
            )
        except (AttributeError, KeyError, TypeError) as error:
            # One broken item should not stop the whole run
            log.warning("Skipped an item on %s: %s", page_url, error)

    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return books, next_url


def scrape(start_url, max_pages=None):
    """Walk through every page, following the 'next' button."""
    all_books = []
    url = start_url
    page_number = 0

    while url:
        page_number += 1
        log.info("Page %d: %s", page_number, url)

        html = fetch(url)
        if html is None:
            log.error("Stopping early because a page could not be downloaded.")
            break

        books, url = parse_page(html, url)
        all_books.extend(books)
        log.info("  found %d books (total so far: %d)", len(books), len(all_books))

        if max_pages and page_number >= max_pages:
            log.info("Reached the page limit (%d).", max_pages)
            break

        if url:
            time.sleep(DELAY_SECONDS)

    return all_books


def save(books, output_name):
    """Save results as CSV and Excel."""
    if not books:
        log.error("No data collected, nothing to save.")
        return

    table = pd.DataFrame(books).drop_duplicates(subset="url")
    # utf-8-sig makes Excel open the CSV with correct characters
    table.to_csv(f"{output_name}.csv", index=False, encoding="utf-8-sig")
    table.to_excel(f"{output_name}.xlsx", index=False)
    log.info("Saved %d books to %s.csv and %s.xlsx", len(table), output_name, output_name)


def main():
    parser = argparse.ArgumentParser(description="Scrape books from books.toscrape.com")
    parser.add_argument("--url", default=DEFAULT_URL, help="first page to scrape")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="output file name without extension")
    parser.add_argument("--max-pages", type=int, default=None, help="stop after this many pages (good for testing)")
    args = parser.parse_args()

    books = scrape(args.url, args.max_pages)
    save(books, args.output)
    print(f"\nDone. Collected {len(books)} books.")


if __name__ == "__main__":
    main()
