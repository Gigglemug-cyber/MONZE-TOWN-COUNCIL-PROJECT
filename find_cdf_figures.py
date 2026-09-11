"""
CSC 4792 Mini Project — Team #41: Monze Town Council
Helper: scans every post for sentences that contain a Kwacha amount,
a km figure, a percentage, or a year-tagged number — the kind of
sentence that belongs in your CDF projects dataset. Prints them
grouped by post so you can quickly eyeball and copy the real figures
into a spreadsheet/CSV by hand (regex alone won't reliably capture
project name + constituency + sector + status from free-form prose,
so this just narrows down where to look).

Usage:
    python find_cdf_figures.py > cdf_candidates.txt
    (then open cdf_candidates.txt and skim through it)
"""

import json
import re
import os
from bs4 import BeautifulSoup

RAW_DIR = "raw_data"

# Matches: K1,234,567.89 / K3.2 million / 15 km / 75% / (2024 ... K...)
NUMBER_PATTERN = re.compile(
    r"(K\s?[\d,]+(\.\d+)?(\s?(million|billion))?"   # Kwacha amounts
    r"|\d+(\.\d+)?\s?(km|kilometers|kilometres)"     # distances
    r"|\d+(\.\d+)?\s?%"                               # percentages
    r")",
    re.IGNORECASE,
)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str):
    # simple sentence splitter, good enough for scanning purposes
    return re.split(r"(?<=[.!?])\s+", text)


def main():
    path = os.path.join(RAW_DIR, "monze_posts.json")
    with open(path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    total_hits = 0
    for p in posts:
        text = html_to_text(p["content"]["rendered"])
        sentences = split_sentences(text)
        hits = [s for s in sentences if NUMBER_PATTERN.search(s)]
        if hits:
            title = html_to_text(p["title"]["rendered"])
            print(f"\n=== Post #{p['id']} | {p['date'][:10]} | {title} ===")
            print(f"URL: {p['link']}")
            for h in hits:
                print(f"  - {h}")
            total_hits += len(hits)

    print(f"\n\nTotal candidate sentences found: {total_hits}")
    print("Copy the real figures (amount, project, constituency, sector,")
    print("status, year) from these into your CDF projects CSV by hand.")


if __name__ == "__main__":
    main()