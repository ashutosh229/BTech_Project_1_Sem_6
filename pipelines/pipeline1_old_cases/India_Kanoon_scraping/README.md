# Indian Kanoon Scraper

A collection of scripts to scrape legal documents from Indian Kanoon using Playwright and BeautifulSoup.

## Prerequisites

- Python 3.x
- Node.js (required for Playwright)

## Installation

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Usage

The scraping process is divided into three stages:

### 1. Extract Court Information
Run `court_info_scraper.py` to extract court slugs and generate `browse.json`.
```bash
python court_info_scraper.py
```

### 2. Extract Document URLs
Run `site_extrator.py` to search for documents by court and year. This script reads `browse.json` and generates JSON files for each court and year (e.g., `allahabad_2015.json`).
```bash
python site_extrator.py
```

### 3. Scrape Case Data
Run `case_data_scraper.py` to extract detailed content from the documents found in the previous step. It saves the results as individual JSON files in the `docs/` directory.
```bash
python case_data_scraper.py
```

## Project Structure

- `court_info_scraper.py`: Scrapes the list of courts.
- `site_extrator.py`: Scrapes search results to get document URLs.
- `case_data_scraper.py`: Scrapes actual judgment text and metadata.
- `docs/`: Directory where the final scraped case data is stored.
- `browse.json`: List of court slugs.
- `<court>_<year>.json`: Intermediate files containing document URLs.
