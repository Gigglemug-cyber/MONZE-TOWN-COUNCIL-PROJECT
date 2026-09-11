"""
CSC 4792 Mini Project — Team #41: Monze Town Council
Starter scraper: pulls all WordPress posts + pages via the REST API,
falls back to nothing fancy — just gets you raw structured JSON to
inspect, then clean/filter into your CSV datasets.

Usage:
    pip install requests beautifulsoup4
    python monze_scraper.py
"""

import requests
import json
import time
import os
import urllib3

# The site's pretty-permalink REST routes (e.g. /wp-json/wp/v2/posts) 404 —
# confirmed working format is the query-string route below instead.
# The site also has an expired SSL cert, so we disable verification for
# this specific known/trusted government domain and silence the warning.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.monzecouncil.gov.zm/?rest_route=/wp/v2"
OUTPUT_DIR = "raw_data"
HEADERS = {
    "User-Agent": "UNZA-CSC4792-Team41-ResearchBot/1.0 (academic mini project; contact: <your_email>)"
}
DELAY_SECONDS = 1.0  # be polite — don't hammer the server


def fetch_all(endpoint: str, per_page: int = 100):
    """Fetch every item from a paginated WP REST API endpoint."""
    all_items = []
    page = 1
    while True:
        url = f"{BASE_URL}/{endpoint}"
        params = {"per_page": per_page, "page": page}
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20, verify=False)

        if resp.status_code == 400:
            # WP returns 400 once you page past the last page
            break
        resp.raise_for_status()

        items = resp.json()
        if not items:
            break

        all_items.extend(items)
        print(f"  {endpoint}: fetched page {page} ({len(items)} items, {len(all_items)} total)")

        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break

        page += 1
        time.sleep(DELAY_SECONDS)

    return all_items


def save_json(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} records to {path}")


def main():
    print("Fetching posts (news articles — likely where most CDF/project data lives)...")
    try:
        posts = fetch_all("posts")
        save_json(posts, "monze_posts.json")
    except requests.exceptions.RequestException as e:
        print(f"  Posts endpoint failed: {e}")
        posts = []

    print("\nFetching pages (About, Contact, static council info)...")
    try:
        pages = fetch_all("pages")
        save_json(pages, "monze_pages.json")
    except requests.exceptions.RequestException as e:
        print(f"  Pages endpoint failed: {e}")
        pages = []

    if not posts and not pages:
        print("\nREST API appears unavailable. Fall back to HTML scraping with")
        print("requests + BeautifulSoup against individual page URLs (e.g. ?p=2424,")
        print("?page_id=1819) collected from the sitemap or by crawling nav links.")

    print("\nDone. Next: inspect raw_data/*.json, extract fields you need")
    print("(title, date, rendered content -> strip HTML -> pull CDF amounts,")
    print("project names, constituencies, statuses), then write out as")
    print("pipe-separated CSVs named db-unza26-csc4792-<description>.csv")


if __name__ == "__main__":
    main()