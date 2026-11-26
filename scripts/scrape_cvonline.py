"""
Refresh the cvonline.hu snapshot: rewrites ../data/cvonline_rows.json

WHY THIS IS A SCRIPT AND NOT A LIVE FETCH IN THE APP
cvonline.hu sends no `access-control-allow-origin` header, so a web page can
never read it — the browser blocks it (tested: "TypeError: Failed to fetch").
Only zyntern.com can be fetched live, because it sends that header. So
cvonline, like profession.hu, has to be collected by a program that is not a
web page — this one — and the result built into the app.

FULL REFRESH:
    python scripts/refresh_all.py        # both portals + rebuild
or step by step:
    python scripts/scrape_cvonline.py
    python src/build_english.py

Needs:  pip install requests beautifulsoup4

It takes about three minutes. cvonline's robots.txt asks for
"Crawl-delay: 10", so there is a deliberate 10-second pause between pages.
Please do not lower it.
"""

import datetime
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "cvonline_rows.json")
META = os.path.join(ROOT, "data", "snapshot_meta.json")

BASE = "https://www.cvonline.hu"
# Their own filter for Budapest + "Szakmai gyakorlat, diákmunka"
# (internship / student job). Drupal paging is 0-indexed.
LISTING = BASE + "/hu/allashirdetesek/budapest/apprenticeships?page={page}"

CRAWL_DELAY = 10          # robots.txt: Crawl-delay: 10
MAX_PAGES = 25
# Refuse to overwrite a good snapshot with a suspiciously small one. If the
# connection drops halfway, or cvonline redesigns its cards and we suddenly
# parse almost nothing, yesterday's jobs are better than a nearly empty app.
MIN_ROWS = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (university project scraper; contact: student)"}

# Categories we keep, in priority order: a job tagged both "SSC" and "Finance"
# should read as Finance, not SSC.
PRIORITY = [
    "Pénzügy / Számvitel / Kontrolling",
    "Értékesítés / Kereskedelem",
    "Marketing / Reklám / Média / PR",
    "Szervezés / Menedzsment / Cégvezetés",
    "Üzleti támogató központok, SSC",
]
RANK = {name.lower(): i for i, name in enumerate(PRIORITY)}


def text_of(node, selector):
    found = node.select_one(selector)
    return re.sub(r"\s+", " ", found.get_text()).strip() if found else ""


def parse_date(raw):
    """'21.09.2026' -> '2026-09-21 09:00:00'"""
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", raw or "")
    if not m:
        return ""
    day, month, year = m.group(1), m.group(2), m.group(3)
    return "%s-%02d-%02d 09:00:00" % (year, int(month), int(day))


def scrape():
    session = requests.Session()
    session.headers.update(HEADERS)

    seen = set()
    rows = []

    for page in range(MAX_PAGES):
        url = LISTING.format(page=page)
        print("Fetching page %d ..." % page, flush=True)
        try:
            resp = session.get(url, timeout=20)
        except requests.RequestException as err:
            # A plain message, not a traceback — this runs unattended.
            print("  -> could not reach cvonline.hu (%s). Check the internet"
                  " connection." % err.__class__.__name__)
            break
        if resp.status_code != 200:
            print("  -> HTTP %d, stopping." % resp.status_code)
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("article.node--job-per-template")
        if not cards:
            print("  -> no more adverts, done.")
            break

        for card in cards:
            job_id = (card.get("id") or "").replace("node-", "")
            if not job_id or job_id in seen:
                continue
            seen.add(job_id)

            terms = [t.strip() for t in text_of(card, ".terms").split("|") if t.strip()]
            hits = sorted(
                (t for t in terms if t.lower() in RANK),
                key=lambda t: RANK[t.lower()],
            )
            if not hits:
                continue                      # not one of our target fields

            cat1 = hits[0]
            rest = [t for t in terms if t != cat1]

            link = card.select_one("h2.node__title a")
            title = (link.get("title") or link.get_text()) if link else ""
            about = card.get("about") or ""
            location = text_of(card, ".location") or "Budapest"

            rows.append([
                job_id,
                re.sub(r"\s+", " ", title).strip(),
                text_of(card, ".recruiter-company-profile-job-organization"),
                "Budapest" if "budapest" in location.lower()
                    else (re.split(r"[,(]", location)[0].strip() or "Egyéb"),
                location,
                cat1,
                rest[0] if rest else "",
                "Szakmai gyakorlat, diákmunka",
                0,                            # remote — cvonline cards don't say
                0, "", "", "",                # cvonline publishes no pay on cards
                parse_date(text_of(card, ".description .date")),
                BASE + about if about else "",
                "",                           # no schedule string on the card
            ])

        print("  -> %d kept so far" % len(rows), flush=True)
        time.sleep(CRAWL_DELAY)

    rows.sort(key=lambda r: r[13], reverse=True)      # newest first
    return rows


def record_snapshot_date(source_name):
    """Stamp today's date so the app can show when this snapshot was taken.

    Both scrapers write into the same small file, each under its own key, and
    src/build_english.py reads it. That is why the date in the app is never
    typed in by hand any more.
    """
    meta = {}
    if os.path.exists(META):
        try:
            with open(META, encoding="utf-8") as f:
                meta = json.load(f)
        except ValueError:
            meta = {}
    meta[source_name] = datetime.date.today().isoformat()
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    rows = scrape()
    if len(rows) < MIN_ROWS:
        print("\nOnly %d jobs collected (expected at least %d) — not overwriting"
              " the existing snapshot." % (len(rows), MIN_ROWS))
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n")
    record_snapshot_date("cvonline.hu")

    by_cat = {}
    for r in rows:
        by_cat[r[5]] = by_cat.get(r[5], 0) + 1

    print("\nWrote %d jobs to %s" % (len(rows), os.path.relpath(OUT, ROOT)))
    for name, n in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print("   %-40s %d" % (name, n))
    print("\nNow run:  python src/build_english.py")
