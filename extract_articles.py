"""
CSC 4792 Mini Project — Team #41: Monze Town Council
Step 2: Turn raw_data/monze_posts.json + monze_pages.json into clean,
pipe-separated CSV files per the assignment's naming convention.

Usage:
    pip install beautifulsoup4
    python extract_articles.py
"""

import json
import csv
import re
import os
from bs4 import BeautifulSoup

RAW_DIR = "raw_data"
OUT_DIR = "datasets"

CONSTITUENCIES = ["Monze Central", "Moomba", "Bweengwa"]


def html_to_text(html: str) -> str:
    """Strip HTML tags/entities down to clean readable text."""
    soup = BeautifulSoup(html or "", "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_constituencies(text: str) -> str:
    """Return semicolon-joined list of constituencies mentioned in the text."""
    found = [c for c in CONSTITUENCIES if c.lower() in text.lower()]
    return ";".join(found) if found else ""


def load_json(filename):
    path = os.path.join(RAW_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_csv(rows, fieldnames, filename):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def process_posts():
    posts = load_json("monze_posts.json")
    rows = []
    for p in posts:
        content_text = html_to_text(p["content"]["rendered"])
        rows.append({
            "post_id": p["id"],
            "date": p["date"][:10],
            "title": html_to_text(p["title"]["rendered"]),
            "constituencies_mentioned": detect_constituencies(content_text),
            "content_text": content_text,
            "url": p["link"],
        })
    write_csv(
        rows,
        ["post_id", "date", "title", "constituencies_mentioned", "content_text", "url"],
        "db-unza26-csc4792-monze_news_articles.csv",
    )


def process_pages():
    pages = load_json("monze_pages.json")
    rows = []
    for p in pages:
        content_text = html_to_text(p["content"]["rendered"])
        if not content_text:
            continue  # skip empty template/utility pages
        rows.append({
            "page_id": p["id"],
            "title": html_to_text(p["title"]["rendered"]),
            "content_text": content_text,
            "url": p["link"],
        })
    write_csv(
        rows,
        ["page_id", "title", "content_text", "url"],
        "db-unza26-csc4792-monze_static_pages.csv",
    )


if __name__ == "__main__":
    process_posts()
    process_pages()