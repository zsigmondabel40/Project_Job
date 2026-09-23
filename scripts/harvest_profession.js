/* =====================================================================
   Refresh the profession.hu snapshot (data/prof_rows.json)

   WHY THIS IS A BROWSER SCRIPT AND NOT A PYTHON ONE
   profession.hu has no API and sends no CORS headers, so nothing outside
   a profession.hu page can read it. This script therefore runs INSIDE a
   profession.hu tab, where its fetches count as same-origin.

   HOW TO RUN IT
   1. Open  https://www.profession.hu/allasok/budapest/1,0,23  in Chrome.
   2. Press F12 → "Console" tab.
   3. Paste this whole file, press Enter. It prints progress as it goes.
   4. When it prints "DONE", run:      copy(JSON.stringify(window.__profRows))
      (`copy` is a Chrome console helper — it puts the result on your clipboard.)
   5. Paste over the contents of data/prof_rows.json.
   6. Rebuild:   python src/build_english.py

   It takes a couple of minutes: there is a deliberate 650 ms pause between
   page requests so we are not hammering their server.
   ===================================================================== */

(async () => {
  "use strict";

  /* Only these four top-level categories are kept. profession.hu has ~23;
     these are the ones this project targets. Compared case-insensitively. */
  const TARGET = new Set([
    "cégvezetés, menedzsment",
    "értékesítés, kereskedelem",
    "marketing, média, pr",
    "pénzügy, könyvelés",
  ]);

  /* Three filtered listing URLs. All are Budapest (location code 23).
     The FIRST number in the comma list is the page number.
     The trailing code is the employment-type / experience filter:
       7  = Szakmai gyakorlat   (accredited internship)
       10 = Diákmunka           (student job)
       the long one            = Nincs tapasztalat (no experience required) */
  const SOURCES = [
    ["https://www.profession.hu/allasok/budapest/{p},0,23,0,0,0,0,0,0,0,0,0,0,7",  "Szakmai gyakorlat", 8],
    ["https://www.profession.hu/allasok/budapest/{p},0,23,0,0,0,0,0,0,0,0,0,0,10", "Diákmunka", 25],
    ["https://www.profession.hu/allasok/budapest/{p},0,23,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1", "Nincs tapasztalat", 20],
  ];

  const CAP = 120;          // stop once we have this many jobs
  const DELAY_MS = 650;     // politeness pause between page requests

  const MONTHS = {
    "január": 1, "február": 2, "március": 3, "április": 4, "május": 5, "június": 6,
    "július": 7, "augusztus": 8, "szeptember": 9, "október": 10, "november": 11, "december": 12,
  };

  const text = (root, sel) => {
    const el = root.querySelector(sel);
    return el ? el.textContent.replace(/\s+/g, " ").trim() : "";
  };

  /* "feladva: Augusztus 17." → "2026-08-17 09:00:00"
     (the card shows this under a "start date" id, but it is the POSTED date) */
  function parsePosted(s) {
    const m = String(s || "").match(/([A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]+)\s+(\d{1,2})\./);
    if (!m) return "";
    const mo = MONTHS[m[1].toLowerCase()];
    if (!mo) return "";
    const now = new Date();
    let d = new Date(now.getFullYear(), mo - 1, parseInt(m[2], 10), 9, 0, 0);
    if (d.getTime() > now.getTime() + 864e5) {           // a date in the future means last year
      d = new Date(now.getFullYear() - 1, mo - 1, parseInt(m[2], 10), 9, 0, 0);
    }
    const p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} 09:00:00`;
  }

  const group = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ");

  /* "Br. 2 400 - 2 650 Ft/óra bér" → [2400, "2 400 – 2 650 Ft", "/ óra", "bruttó"] */
  function parsePay(s) {
    s = String(s || "");
    if (!s) return [0, "", "", ""];
    const nums = s.match(/\d[\d  ]*/g) || [];
    const a = nums.length ? parseInt(nums[0].replace(/[\s ]/g, ""), 10) : 0;
    const b = nums[1] ? parseInt(nums[1].replace(/[\s ]/g, ""), 10) : 0;
    const type = /^\s*net/i.test(s) ? "nettó" : (/^\s*(br|brutt)/i.test(s) ? "bruttó" : "");
    const per = /óra/i.test(s) ? "/ óra" : (/(hó|hónap)/i.test(s) ? "/ hó" : (/nap/i.test(s) ? "/ nap" : ""));
    if (!a) return [0, "", per, type];
    const fmt = (b && b > a) ? `${group(a)} – ${group(b)} Ft` : `${group(a)} Ft`;
    return [a, fmt, per, type];
  }

  const rows = {};
  const seen = new Set();

  for (const [tpl, bucket, maxPage] of SOURCES) {
    if (Object.keys(rows).length >= CAP) break;
    let pages = 0;

    for (let page = 1; page <= maxPage; page++) {
      if (Object.keys(rows).length >= CAP) break;

      const res = await fetch(tpl.replace("{p}", page), { credentials: "same-origin" });
      if (!res.ok) break;
      const doc = new DOMParser().parseFromString(await res.text(), "text/html");
      const anchors = doc.querySelectorAll("a[data-item-id]");
      pages++;
      if (!anchors.length) break;

      anchors.forEach((a) => {
        const id = a.getAttribute("data-item-id");
        if (!id || seen.has(id)) return;

        /* The listing cards carry Google-Analytics data-* attributes with
           everything we need — far more reliable than scraping visible text. */
        const cat1 = (a.getAttribute("data-category1") || "").trim();
        if (!TARGET.has(cat1.toLowerCase())) return;
        seen.add(id);

        const card = a.closest(".dsx-card") || doc;
        const pre = `#detailed-job-card-${id}-`;

        const loc = text(card, pre + "details-location");
        const remote = /hibrid|távmunka|home ?office/i.test(loc) ? 1 : 0;
        const clean = loc.replace(/^(Hibrid|Távmunka|Home ?office)[^•]*•\s*/i, "").trim();
        const city = /budapest/i.test(clean) ? "Budapest" : (clean.split(/[,•]/)[0].trim() || "Egyéb");
        const pay = parsePay(text(card, pre + "details-salary"));

        rows[id] = [
          id,
          (a.getAttribute("data-item-name") || "").trim(),
          (a.getAttribute("data-affiliation") || "").trim(),
          city,
          clean || loc,
          cat1,
          (a.getAttribute("data-category2") || "").trim(),
          bucket,
          remote,
          pay[0], pay[1], pay[2], pay[3],
          parsePosted(text(card, pre + "details-start-date")),
          a.getAttribute("href"),
          text(card, pre + "details-classificationType"),
        ];
      });

      console.log(`[${bucket}] page ${page} — ${Object.keys(rows).length} kept so far`);
      await new Promise((r) => setTimeout(r, DELAY_MS));
    }
    console.log(`[${bucket}] finished after ${pages} pages`);
  }

  window.__profRows = Object.values(rows);
  console.log(`DONE — ${window.__profRows.length} jobs.`);
  console.log('Now run:  copy(JSON.stringify(window.__profRows))');
})();
