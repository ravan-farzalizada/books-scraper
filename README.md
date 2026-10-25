# Books Scraper

A Python tool that collects book data from every page of a website and saves it to clean CSV and Excel files.

It is built to show a typical web-scraping job: following pagination, handling errors, and delivering a ready-to-use spreadsheet.

**Demo video:** https://youtu.be/h6kdXdWn_kM

## What it collects

For each book:

| Column | Description |
|---|---|
| title | Book title |
| price_gbp | Price as a number, in British pounds |
| rating | Star rating from 1 to 5 |
| availability | Stock status |
| url | Link to the book page |

Example run: **1,000 books from 50 pages in about 1-2 minutes.**

## Features

- Follows the "next page" button automatically until the last page
- Waits between requests so it doesn't overload the website
- Retries failed requests up to 3 times
- Skips a broken item instead of crashing the whole run
- Writes a log file (`scraper.log`) so you can see what happened
- Removes duplicate books
- Saves results as both CSV and Excel

## Requirements

- Python 3.9 or newer
- Windows, Mac, or Linux

## Installation

```
git clone https://github.com/ravan-farzalizada/books-scraper.git
cd books-scraper
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Mac or Linux, use `source venv/bin/activate` instead of `venv\Scripts\activate`.

## Usage

Scrape every page:

```
python scraper.py
```

Test with just 2 pages:

```
python scraper.py --max-pages 2
```

Choose a different output file name:

```
python scraper.py --output my_books
```

Results are saved as `books.csv` and `books.xlsx` in the same folder.

## Sample output

The repository includes `books.csv` and `books.xlsx`, the result of a full run.

## Notes

- This project scrapes [books.toscrape.com](https://books.toscrape.com/), a website made for practicing web scraping.
- Prices are saved as plain numbers (in British pounds) so they can be sorted and calculated in Excel. A currency column or symbol can be added on request.
- Always check a website's terms of service and `robots.txt` before scraping it.

## Need something similar?

I build custom scrapers and Excel/report automation for businesses.

- Fiverr: [YOUR GIG LINK]
- Contact: [YOUR EMAIL OR UPWORK LINK]
