"""
Refresh the profession.hu snapshot: rewrites ../data/prof_rows.json

WHY THIS IS A SCRIPT AND NOT A LIVE FETCH IN THE APP
profession.hu sends no `access-control-allow-origin` header, so a web page can
never read it — the browser blocks it. Only zyntern.com can be fetched live.
So profession.hu, like cvonline.hu, is collected by a program that is not a web
page (this one), and the result is built into the app.

FULL REFRESH:
    python scripts/refresh_all.py        # both portals + rebuild
or step by step:
    python scripts/scrape_profession.py
    python src/build_english.py

Needs:  pip install requests beautifulsoup4

HOW IT FINDS THE JOBS
profession.hu encodes its filters as numbers in the URL path. The three below
were read off the site's own filter UI. In each, the FIRST number is the page
number and 23 is Budapest; the trailing number is the employment-type filter.
There is no single filter for "finance OR sales OR marketing OR management", so
we pull every Budapest entry-level advert and keep the matching ones here.

Each advert carries Google-Analytics `data-*` attributes holding the id, title,
company and category — far more reliable than reading the visible text.
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
OUT = os.path.join(ROOT, "data", "prof_rows.json")
META = os.path.join(ROOT, "data", "snapshot_meta.json")

BASE = "https://www.profession.hu"

SOURCES = [
    (BASE + "/allasok/budapest/{page},0,23,0,0,0,0,0,0,0,0,0,0,7",
     "Szakmai gyakorlat", 8),
    (BASE + "/allasok/budapest/{page},0,23,0,0,0,0,0,0,0,0,0,0,10",
     "Diákmunka", 25),
    (BASE + "/allasok/budapest/{page},0,23,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1",
     "Nincs tapasztalat", 20),
]

# Only these four top-level categories are kept (exact match, case-insensitive).
TARGET = {
    "cégvezetés, menedzsment",
    "értékesítés, kereskedelem",
    "marketing, média, pr",
    "pénzügy, könyvelés",
}

CAP = 120
DELAY = 0.7
# Refuse to overwrite a good snapshot with a suspiciously small one. If the
# connection drops halfway, or profession.hu changes its markup and we suddenly
# parse almost nothing, yesterday's jobs are better than a nearly empty app.
MIN_ROWS = 40
HEADERS = {"User-Agent": "Mozilla/5.0 (university project scraper; contact: student)"}

MONTHS = {
    "január": 1, "február": 2, "március": 3, "április": 4, "május": 5, "június": 6,
    "július": 7, "augusztus": 8, "szeptember": 9, "október": 10, "november": 11,
    "december": 12,
}


def text_of(node, selector):
    found = node.select_one(selector)
    return re.sub(r"\s+", " ", found.get_text()).strip() if found else ""


def parse_posted(raw):
    """'feladva: Augusztus 17.' -> '2026-08-17 09:00:00'

    The site shows this under a 'start date' element, but it is the date the
    advert was posted. No year is given, so assume this year and step back one
    if that would put it in the future.
    """
    m = re.search(r"([A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]+)\s+(\d{1,2})\.", raw or "")
    if not m:
        return ""
    month = MONTHS.get(m.group(1).lower())
    if not month:
        return ""
    today = datetime.date.today()
    try:
        d = datetime.date(today.year, month, int(m.group(2)))
    except ValueError:
        return ""
    if d > today + datetime.timedelta(days=1):
        d = datetime.date(today.year - 1, month, int(m.group(2)))
    return d.strftime("%Y-%m-%d") + " 09:00:00"


def group(n):
    return re.sub(r"\B(?=(\d{3})+(?!\d))", " ", str(n))


def parse_pay(raw):
    """'Br. 2 400 - 2 650 Ft/óra bér' -> (2400, '2 400 – 2 650 Ft', '/ óra', 'bruttó')"""
    raw = raw or ""
    if not raw:
        return 0, "", "", ""
    nums = re.findall(r"\d[\d  ]*", raw)
    first = int(re.sub(r"[\s ]", "", nums[0])) if nums else 0
    second = int(re.sub(r"[\s ]", "", nums[1])) if len(nums) > 1 else 0
    pay_type = "nettó" if re.match(r"\s*net", raw, re.I) else (
        "bruttó" if re.match(r"\s*(br|brutt)", raw, re.I) else "")
    period = "/ óra" if re.search(r"óra", raw, re.I) else (
        "/ hó" if re.search(r"hó|hónap", raw, re.I) else (
            "/ nap" if re.search(r"nap", raw, re.I) else ""))
    if not first:
        return 0, "", period, pay_type
    fmt = ("%s – %s Ft" % (group(first), group(second))) if second > first else ("%s Ft" % group(first))
    return first, fmt, period, pay_type


def row_from_anchor(anchor, soup, bucket):
    """Turn one listing anchor into the 16-column row the app reads, or None."""
    job_id = anchor.get("data-item-id")
    cat1 = (anchor.get("data-category1") or "").strip()
    if not job_id or cat1.lower() not in TARGET:
        return None

    card = anchor.find_parent(class_="dsx-card") or soup
    pre = "#detailed-job-card-%s-" % job_id

    location = text_of(card, pre + "details-location")
    remote = 1 if re.search(r"hibrid|távmunka|home ?office", location, re.I) else 0
    clean = re.sub(r"^(Hibrid|Távmunka|Home ?office)[^•]*•\s*", "", location, flags=re.I).strip()
    city = "Budapest" if re.search(r"budapest", clean, re.I) else (
        re.split(r"[,•]", clean)[0].strip() or "Egyéb")
    pay_num, pay_fmt, pay_period, pay_type = parse_pay(text_of(card, pre + "details-salary"))

    return [
        job_id,
        (anchor.get("data-item-name") or "").strip(),
        (anchor.get("data-affiliation") or "").strip(),
        city,
        clean or location,
        cat1,
        (anchor.get("data-category2") or "").strip(),
        bucket,
        remote,
        pay_num, pay_fmt, pay_period, pay_type,
        parse_posted(text_of(card, pre + "details-start-date")),
        anchor.get("href") or "",
        text_of(card, pre + "details-classificationType"),
    ]


def scrape():
    session = requests.Session()
    session.headers.update(HEADERS)

    seen = set()
    rows = []

    for template, bucket, max_page in SOURCES:
        if len(rows) >= CAP:
            break
        for page in range(1, max_page + 1):
            if len(rows) >= CAP:
                break

            print("Fetching [%s] page %d ..." % (bucket, page), flush=True)
            try:
                resp = session.get(template.format(page=page), timeout=20)
            except requests.RequestException as err:
                # A plain message, not a traceback — this runs unattended.
                print("  -> could not reach profession.hu (%s). Check the"
                      " internet connection." % err.__class__.__name__)
                return rows
            if resp.status_code != 200:
                print("  -> HTTP %d, moving on." % resp.status_code)
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            anchors = soup.select("a[data-item-id]")
            if not anchors:
                print("  -> no more adverts in this filter.")
                break

            for anchor in anchors:
                if anchor.get("data-item-id") in seen:
                    continue
                row = row_from_anchor(anchor, soup, bucket)
                if row:
                    seen.add(row[0])
                    rows.append(row)

            print("  -> %d kept so far" % len(rows), flush=True)
            time.sleep(DELAY)

    return rows


def record_snapshot_date(source_name):
    """Stamp today's date so the app can show when this snapshot was taken."""
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
    collected = scrape()
    if len(collected) < MIN_ROWS:
        print("\nOnly %d jobs collected (expected at least %d) — leaving the"
              " existing snapshot alone." % (len(collected), MIN_ROWS))
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in collected) + "\n]\n")
    record_snapshot_date("profession.hu")

    by_cat = {}
    for r in collected:
        by_cat[r[5]] = by_cat.get(r[5], 0) + 1

    print("\nWrote %d jobs to %s" % (len(collected), os.path.relpath(OUT, ROOT)))
    for name, n in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print("   %-30s %d" % (name, n))
