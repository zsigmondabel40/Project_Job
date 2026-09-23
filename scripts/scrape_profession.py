"""
Scraper for profession.hu — Budapest, entry-level/internship jobs, in our 5 target fields.

WHAT THIS DOES, IN PLAIN WORDS:
1. profession.hu has a page that lists ONLY internship jobs in Budapest, and another
   page that lists ONLY "student work" (diákmunka) jobs in Budapest, and another for
   "no experience required" jobs in Budapest. We found these exact filtered URLs by
   clicking through the site's own filters.
2. Each of those pages shows ~20 job listings per "page" (like page 1, page 2, ...).
   We loop through the pages of all three URLs.
3. On each page, every job listing conveniently already carries hidden data (used by
   the site's own analytics) that tells us: the job id, job title, company name,
   category/industry, and salary if it's public. We just read that instead of trying
   to parse the visible text, which is much more reliable.
4. profession.hu doesn't have a single filter for "marketing OR finance OR sales OR
   management OR business development" all at once — so instead we grab every
   internship/entry-level Budapest job, and keep only the ones whose category matches
   one of our 5 fields (checked with simple keyword matching, in Python, not on the
   website).
5. We stop once we've collected 100 matching jobs (or run out of pages).

HOW TO RUN THIS:
1. Install the two libraries this needs (one-time):
       pip install requests beautifulsoup4
2. Run the script:
       python scrape_profession.py
3. It creates a file called profession_jobs.json next to this script.

NOTE: I can't test this against the live site from my side (my environment can't
make normal web requests), so if profession.hu changes something and this breaks,
that's expected/normal in scraping — tell me the error message and we'll fix it
together.
"""

import json
import time

import requests
from bs4 import BeautifulSoup

# --- Known-good filtered listing URLs (Budapest only), with {page} as a placeholder ---
# We found these by using profession.hu's own filters for location=Budapest combined
# with each of these three "entry level / intern" filters, then reading off the URL.
FILTERED_LISTING_URLS = {
    "szakmai_gyakorlat (internship)": (
        "https://www.profession.hu/allasok/budapest/{page},0,23,0,0,0,0,0,0,0,0,0,0,7"
    ),
    "diakmunka (student work)": (
        "https://www.profession.hu/allasok/budapest/{page},0,23,0,0,0,0,0,0,0,0,0,0,10"
    ),
    "nincs_tapasztalat (no experience required)": (
        "https://www.profession.hu/allasok/budapest/{page},0,23,0,0,0,0,0,1,0,0,0,0,0,"
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1"
    ),
}

# Our 5 target fields, matched against the job's category text (which profession.hu
# gives us in Hungarian). Add more keywords here any time you notice a relevant job
# that got missed.
TARGET_FIELDS = {
    "management": ["cégvezetés", "menedzsment", "menedzser"],
    "finance": ["pénzügy", "könyvelés", "controlling"],
    "business_development": ["üzletfejlesztés", "business development"],
    "marketing": ["marketing", "média", " pr"],
    "sales": ["értékesítés", "kereskedelem"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (university project scraper; contact: student)"
}

MAX_RESULTS = 100
DELAY_SECONDS = 1.5   # politeness delay between requests
MAX_PAGES_PER_FILTER = 30  # safety limit so we never loop forever


def matches_target_field(cat1: str, cat2: str) -> str | None:
    """Return the name of the target field this job belongs to, or None if it
    doesn't match any of our 5 fields."""
    text = f"{cat1} {cat2}".lower()
    for field, keywords in TARGET_FIELDS.items():
        if any(keyword in text for keyword in keywords):
            return field
    return None


def scrape_profession(max_results: int = MAX_RESULTS) -> list[dict]:
    results = []
    seen_ids = set()

    for filter_label, url_template in FILTERED_LISTING_URLS.items():
        if len(results) >= max_results:
            break

        page = 1
        while len(results) < max_results and page <= MAX_PAGES_PER_FILTER:
            url = url_template.format(page=page)
            print(f"Fetching [{filter_label}] page {page} ...")

            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"  -> got status {response.status_code}, stopping this filter.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("a[data-item-id]")
            if not cards:
                print("  -> no more listings, moving to next filter.")
                break

            for card in cards:
                job_id = card.get("data-item-id")
                if not job_id or job_id in seen_ids:
                    continue

                cat1 = card.get("data-category1", "") or ""
                cat2 = card.get("data-category2", "") or ""
                field = matches_target_field(cat1, cat2)
                if field is None:
                    continue  # not one of our 5 target fields, skip it

                seen_ids.add(job_id)

                salary_value = card.get("data-value", "") or ""
                currency = card.get("data-currency", "") or ""
                salary = f"{salary_value} {currency}".strip() if salary_value else "Nincs megadva"

                results.append({
                    "id": job_id,
                    "job": "profession.hu",
                    "position": (card.get("data-item-name") or "").strip(),
                    "industry": f"{cat1} / {cat2}".strip(" /"),
                    "title": (card.get("data-affiliation") or "").strip(),
                    "salary": salary,
                    "url": card.get("href"),
                })

                if len(results) >= max_results:
                    break

            page += 1
            time.sleep(DELAY_SECONDS)

    return results


if __name__ == "__main__":
    jobs = scrape_profession(MAX_RESULTS)

    with open("profession_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(jobs)} jobs to profession_jobs.json")
    if len(jobs) < MAX_RESULTS:
        print(
            f"Note: only found {len(jobs)} matching jobs out of the {MAX_RESULTS} "
            "target. That can happen if there simply aren't enough Budapest "
            "internship/entry-level listings right now in these 5 fields."
        )
