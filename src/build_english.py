# -*- coding: utf-8 -*-
"""Translate the job-search UI from Hungarian to English.

Job titles and company names are left exactly as the portals publish them.
Everything else — interface text plus the closed vocabularies (categories,
job types, languages, schedule terms) — is translated.
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SRC  = os.path.join(HERE, 'template_hu.html')             # Hungarian source template
DATA = os.path.join(ROOT, 'data', 'prof_rows.json')       # profession.hu snapshot
OUT  = os.path.join(ROOT, 'internship_finder.html')       # the finished app
BUILD_DIR = os.path.join(ROOT, 'build')                   # intermediate, gitignored

h = io.open(SRC, encoding='utf-8').read()
missing = []

def sub(old, new, count=1):
    global h
    if old not in h:
        missing.append(old[:70])
        return
    h = h.replace(old, new, count)

# ---------------------------------------------------------------- markup
sub('<html lang="hu">', '<html lang="en">')
sub('<title>Budapest Gyakornokkereső</title>', '<title>Budapest Internship Finder</title>')
sub('<h1>Budapest Gyakornokkereső</h1>', '<h1>Budapest Internship Finder</h1>')
sub('placeholder="Pozíció, cég vagy készség" aria-label="Keresés pozícióra, cégre, készségre"',
    'placeholder="Job title, company or skill" aria-label="Search by job title, company or skill"')
sub('placeholder="Helyszín" aria-label="Keresés helyszínre"',
    'placeholder="Location" aria-label="Search by location"')
sub('>Frissítés</button>', '>Refresh</button>')
sub('<label for="sort">Rendezés</label>', '<label for="sort">Sort</label>')
sub('<option value="relevant">Kiemelt és friss</option>', '<option value="relevant">Featured &amp; newest</option>')
sub('<option value="new">Legfrissebb</option>', '<option value="new">Newest first</option>')
sub('<option value="old">Legrégebbi</option>', '<option value="old">Oldest first</option>')
sub('<option value="pay">Legmagasabb órabér</option>', '<option value="pay">Highest hourly pay</option>')
sub('<option value="company">Cég (A–Z)</option>', '<option value="company">Company (A–Z)</option>')

# ---------------------------------------------------------------- vocabularies
FIELD_EN = {
    # zyntern.com categories
    "HR, vezetés-szervezés": "HR & Organisation",
    "Tanácsadás & stratégia": "Consulting & Strategy",
    "Környezet & energia": "Environment & Energy",
    "Pénzügy & számvitel": "Finance & Accounting",
    "Adminisztratív": "Administration",
    "Logisztika & beszerzés": "Logistics & Procurement",
    "Marketing & kommunikáció": "Marketing & Communications",
    "Agrármérnök": "Agricultural Engineering",
    "Értékesítés & kereskedelem": "Sales & Retail",
    "IT software & webfejlesztés": "IT Software & Web Development",
    "Villamosmérnök": "Electrical Engineering",
    "Gépészmérnök": "Mechanical Engineering",
    "Vegyészmérnök": "Chemical Engineering",
    "Projektmenedzsment": "Project Management",
    "Vendéglátás & turizmus": "Hospitality & Tourism",
    "Mechatronikai mérnök": "Mechatronics Engineering",
    "Építész & építőmérnök": "Architecture & Civil Engineering",
    "IT üzemeltetés": "IT Operations",
    "Fizikai munka": "Manual Work",
    "Ügyfélszolgálat, Support": "Customer Service & Support",
    "Folyamatmérnök": "Process Engineering",
    "Közlekedés & járműmérnök": "Transport & Automotive Engineering",
    "Épületgépész": "Building Services Engineering",
    # profession.hu top-level categories
    "Pénzügy, Könyvelés": "Finance & Accounting",
    "Értékesítés, Kereskedelem": "Sales & Retail",
    "Marketing, Média, PR": "Marketing, Media & PR",
    "Cégvezetés, Menedzsment": "Management & Leadership",
    # profession.hu sub-categories
    "Adótanácsadó, Szakértő": "Tax Advisor",
    "Elemző, Tanácsadó": "Analyst / Advisor",
    "Fotózás": "Photography",
    "Host, Hostess": "Host / Hostess",
    "Interim menedzser": "Interim Manager",
    "Kereskedelmi munkatárs": "Commercial Associate",
    "Kereskedő, Eladó": "Retail Assistant",
    "Kontrolling": "Controlling",
    "Könyvelés": "Bookkeeping",
    "Könyvvizsgáló, Belsőellenőr": "Auditor / Internal Audit",
    "Követelés kezelés, Behajtás": "Receivables & Collections",
    "Külkereskedelmi bonyolító": "Foreign Trade Administrator",
    "Márka- és Termékmenedzser": "Brand & Product Manager",
    "Mérnök, Műszaki értékesítő": "Technical Sales Engineer",
    "Online marketing": "Online Marketing",
    "Pénzügyi asszisztens, Munkatárs": "Finance Assistant",
    "Pénzügyi szolgáltatások értékesítése": "Financial Services Sales",
    "Pénzügyi, Számviteli vezető": "Finance & Accounting Lead",
    "Számlázó, Pénztáros": "Invoicing & Cashier",
    "Számviteli munkatárs": "Accounting Associate",
    "Telefonos értékesítő": "Telesales",
    "Területi képviselő": "Area Sales Representative",
    "Értékesítési munkatárs": "Sales Associate",
    "Értékesítési, Kereskedelmi vezető": "Sales & Commercial Lead",
    "Üzleti elemző": "Business Analyst",
}
TYPE_EN = {
    "Gyakornoki állás": "Internship",
    "Szakmai gyakorlat": "Internship (accredited)",
    "Diákmunka": "Student job",
    "Friss diplomás állás": "Graduate role",
    "Junior, 1-3 év tapasztalat": "Junior (1–3 yrs)",
    "Nincs tapasztalat": "No experience required",
}
LANG_EN = {
    "Magyar": "Hungarian", "Angol": "English", "Német": "German", "Spanyol": "Spanish",
    "Francia": "French", "Olasz": "Italian", "Orosz": "Russian", "Lengyel": "Polish",
    "Cseh": "Czech", "Szlovák": "Slovak", "Román": "Romanian", "Horvát": "Croatian",
    "Szerb": "Serbian", "Szlovén": "Slovenian", "Holland": "Dutch", "Portugál": "Portuguese",
    "Kínai": "Chinese", "Japán": "Japanese", "Koreai": "Korean", "Arab": "Arabic",
    "Görög": "Greek", "Török": "Turkish", "Ukrán": "Ukrainian", "Bolgár": "Bulgarian",
    "Svéd": "Swedish", "Norvég": "Norwegian", "Dán": "Danish", "Finn": "Finnish",
}
LEVEL_EN = {
    "Anyanyelvi": "native",
    "Felsőfokú tárgyalási szint": "advanced / business fluent",
    "Limitált tárgyalási szint": "intermediate / working",
    "Alapszint": "basic",
}
VALUE_EN = {
    "nem szükséges végzettség": "No degree required",
    "szükséges": "Required",
    "nem szükséges": "Not required",
    "amint lehet": "As soon as possible",
    "határozatlan": "Open-ended",
}
SCHED_EN = {
    "Teljes munkaidő": "Full-time", "Részmunkaidő": "Part-time",
    "Kötött munkarend": "fixed schedule", "Kötetlen munkarend": "flexible schedule",
    "Műszakos munkarend": "shift work", "2 műszak": "2 shifts",
    "Alkalmazotti jogviszony": "employment contract", "Diákmunka": "student job",
    "Szakmai gyakorlat": "accredited internship", "Alkalmi munka": "casual work",
    "Vállalkozói": "contractor", "Kisgyermekeseknek": "suitable for parents",
    "Megváltozott munkaképességű": "suitable for reduced work capacity",
    "Nyugdíj mellett végezhető": "can be done alongside a pension",
}
PERIOD_EN = {"/ óra": "/ hour", "/ nap": "/ day", "/ hó": "/ month"}
PAYTYPE_EN = {"bruttó": "gross", "nettó": "net"}

def js(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

DICT_JS = '''
/* ---------- Hungarian → English vocabularies ----------
   Both portals publish in Hungarian. Job titles and company names are left
   exactly as posted — that is the real advert text. The closed vocabularies
   below (categories, job types, languages, schedule terms) are translated so
   the filters read in English. Anything not listed falls through unchanged,
   so a new category appearing in the API still shows up rather than vanishing. */
var FIELD_EN = %s;
var TYPE_EN = %s;
var LANG_EN = %s;
var LEVEL_EN = %s;
var VALUE_EN = %s;
var SCHED_EN = %s;
var PERIOD_EN = %s;
var PAYTYPE_EN = %s;

function tr(map, s){
  s = (s == null ? "" : String(s)).trim();
  return Object.prototype.hasOwnProperty.call(map, s) ? map[s] : s;
}
function trLangLevel(name, level){
  var n = tr(LANG_EN, name);
  return level ? n + " – " + tr(LEVEL_EN, level) : n;
}
/* "Részmunkaidő • Heti 25 óra • Kötött munkarend" →
   "Part-time • 25 h/week • fixed schedule" */
function trSchedule(s){
  if (!s) return "";
  return String(s).split("•").map(function(part){
    var t = part.trim();
    if (!t) return "";
    var m = t.match(/^Heti\\s+(\\d+)(?:\\s*-\\s*(\\d+))?\\s*óra$/i);
    if (m) return m[2] ? m[1] + "–" + m[2] + " h/week" : m[1] + " h/week";
    m = t.match(/^Napi\\s+(\\d+)(?:\\s*-\\s*(\\d+))?\\s*óra$/i);
    if (m) return m[2] ? m[1] + "–" + m[2] + " h/day" : m[1] + " h/day";
    m = t.match(/^(\\d{1,2}:\\d{2})\\s*-\\s*(\\d{1,2}:\\d{2})\\s*között$/);
    if (m) return "between " + m[1] + "–" + m[2];
    return tr(SCHED_EN, t);
  }).filter(Boolean).join(" • ");
}
function group(n){ return String(n).replace(/\\B(?=(\\d{3})+(?!\\d))/g, "\\u00a0"); }

''' % (js(FIELD_EN), js(TYPE_EN), js(LANG_EN), js(LEVEL_EN),
       js(VALUE_EN), js(SCHED_EN), js(PERIOD_EN), js(PAYTYPE_EN))

sub('/* ---------- segédfüggvények ---------- */', DICT_JS + '/* ---------- helpers ---------- */')

# ------------------------------------------------- translate at ingestion
sub('    fields: (j.fields || []).map(function(f){ return f.name; }),',
    '    fields: (j.fields || []).map(function(f){ return tr(FIELD_EN, f.name); }),')
sub('    jobType: (j.job_type && (j.job_type.name || j.job_type.short_name)) || "",',
    '    jobType: tr(TYPE_EN, (j.job_type && (j.job_type.name || j.job_type.short_name)) || ""),')
sub('    degree: j.degree_level_name || "",', '    degree: tr(VALUE_EN, j.degree_level_name || ""),')
sub('    student: j.student_status_name || "",', '    student: tr(VALUE_EN, j.student_status_name || ""),')
sub('    payPeriod: (j.salary_period_name || "").trim(),',
    '    payPeriod: tr(PERIOD_EN, (j.salary_period_name || "").trim()),')
sub('    payType: (j.salary_type_name || "").trim(),',
    '    payType: tr(PAYTYPE_EN, (j.salary_type_name || "").trim()),')
sub('    langs: (j.languages || []).map(function(l){ return l.name + (l.level_name ? " – " + l.level_name : ""); }),',
    '    langs: (j.languages || []).map(function(l){ return trLangLevel(l.name, l.level_name); }),')
sub('    langNames: (j.languages || []).map(function(l){ return l.name; }),',
    '    langNames: (j.languages || []).map(function(l){ return tr(LANG_EN, l.name); }),')
sub('    deadline: j.job_end_date_name || "",', '    deadline: tr(VALUE_EN, j.job_end_date_name || ""),')
sub('    start: j.job_start_date_name || "",', '    start: tr(VALUE_EN, j.job_start_date_name || ""),')

sub('    fields: [r[5], r[6]].filter(Boolean),',
    '    fields: [tr(FIELD_EN, r[5]), tr(FIELD_EN, r[6])].filter(Boolean),')
sub('    jobType: r[7],', '    jobType: tr(TYPE_EN, r[7]),')
sub('    payPeriod: r[11] || "",', '    payPeriod: tr(PERIOD_EN, r[11] || ""),')
sub('    payType: r[12] || "",', '    payType: tr(PAYTYPE_EN, r[12] || ""),')
sub('    schedule: cls,', '    schedule: trSchedule(cls),')

sub('  return first || "Egyéb";', '  return first || "Other";')
sub('  return j.payPeriod === "/ óra" ? (j.pay || 0) : 0;',
    '  return j.payPeriod === "/ hour" ? (j.pay || 0) : 0;')
sub('  if (state.noStudent && j.student !== "nem szükséges") return false;',
    '  if (state.noStudent && j.student !== "Not required") return false;')

# ---------------------------------------------------------------- relative dates
sub('  if (days <= 0) return "ma";\n  if (days === 1) return "tegnap";\n  if (days < 31) return days + " napja";',
    '  if (days <= 0) return "today";\n  if (days === 1) return "yesterday";\n  if (days < 31) return days + " days ago";')
sub('  return m + " hónapja";', '  return m + (m === 1 ? " month ago" : " months ago");')

# ---------------------------------------------------------------- filters
sub('label:"Forrás"', 'label:"Source"')
sub('label:"Szakterület"', 'label:"Field"')
sub('label:"Munka típusa"', 'label:"Job type"')
sub('label:"Helyszín"', 'label:"Location"')
sub('label:"Nyelv"', 'label:"Language"')
sub('{ v:0,    label:"Mindegy" }', '{ v:0,    label:"Any" }')
for v in (2000, 2300, 2500, 2700):
    thousands, rest = ('%d' % v)[:-3], ('%d' % v)[-3:]
    sub('label:"' + thousands + ' ' + rest + ' Ft / \u00f3ra felett"',
        'label:"' + thousands + '\u00a0' + rest + ' Ft / hour or more"')
sub('{ v:0,  label:"Mindegy" }', '{ v:0,  label:"Any" }')
sub('label:"Legfeljebb heti 20 óra" }', 'label:"Max 20 h / week" }')
sub('label:"Legfeljebb heti 25 óra" }', 'label:"Max 25 h / week" }')
sub('label:"Legfeljebb heti 30 óra" }', 'label:"Max 30 h / week" }')
sub('radioPill("minPay", "Fizetés", PAY_STEPS, function(v){\n    return v ? v.toLocaleString("hu-HU") + " Ft+" : null;',
    'radioPill("minPay", "Pay", PAY_STEPS, function(v){\n    return v ? group(v) + " Ft+" : null;')
sub('radioPill("maxHours", "Heti óraszám", HOUR_STEPS, function(v){\n    return v ? "≤ " + v + " óra" : null;',
    'radioPill("maxHours", "Hours / week", HOUR_STEPS, function(v){\n    return v ? "≤ " + v + " h" : null;')
sub('togglePill("remote", "Távmunka")', 'togglePill("remote", "Remote")')
sub('togglePill("noStudent", "Hallgatói jogviszony nélkül")', 'togglePill("noStudent", "No student status needed")')
sub('togglePill("savedOnly", "Mentettek")', 'togglePill("savedOnly", "Saved")')
sub('clear.textContent = "Összes szűrő törlése";', 'clear.textContent = "Clear all filters";')
sub('clr.textContent = "Törlés";', 'clr.textContent = "Clear";')
sub('done.textContent = "Kész";', 'done.textContent = "Done";')

# ---------------------------------------------------------------- active chips
sub('items.push({ label: state.minPay.toLocaleString("hu-HU") + " Ft / óra felett", off',
    'items.push({ label: group(state.minPay) + " Ft / hour or more", off')
sub('items.push({ label: "Legfeljebb heti " + state.maxHours + " óra", off',
    'items.push({ label: "Max " + state.maxHours + " h / week", off')
sub('if (state.remote) items.push({ label: "Távmunka"', 'if (state.remote) items.push({ label: "Remote"')
sub('if (state.noStudent) items.push({ label: "Hallgatói jogviszony nélkül"',
    'if (state.noStudent) items.push({ label: "No student status needed"')
sub('if (state.savedOnly) items.push({ label: "Mentettek"', 'if (state.savedOnly) items.push({ label: "Saved"')
sub('x.setAttribute("aria-label", it.label + " szűrő eltávolítása");',
    'x.setAttribute("aria-label", "Remove filter: " + it.label);')

# ---------------------------------------------------------------- list
sub('e.innerHTML = "<p>Nincs a szűrőknek megfelelő állás.</p>";',
    'e.innerHTML = "<p>No jobs match these filters.</p>";')
sub('b.textContent = "Szűrők törlése";', 'b.textContent = "Clear filters";')
sub('if (j.remote) tags.push(\'<span class="tag remote">Távmunka</span>\');',
    'if (j.remote) tags.push(\'<span class="tag remote">Remote</span>\');')
sub('if (j.hours) tags.push(\'<span class="tag">heti \' + j.hours + " óra</span>");',
    'if (j.hours) tags.push(\'<span class="tag">\' + j.hours + " h/week</span>");')
sub('sv.setAttribute("aria-label", SAVED.has(j.key) ? "Mentés visszavonása" : "Állás mentése");',
    'sv.setAttribute("aria-label", SAVED.has(j.key) ? "Remove from saved" : "Save job");')

# ---------------------------------------------------------------- detail
sub('\'<span class="big">Válassz egy állást</span>\'', '\'<span class="big">Select a job</span>\'')
sub('"<p>A bal oldali listából kattints egy hirdetésre, és itt megjelennek a részletei — fizetés, heti óraszám, nyelvek, elvárt készségek.</p>"',
    '"<p>Pick an advert from the list on the left and its details appear here — pay, weekly hours, languages and the skills asked for.</p>"')
sub('facts.push(["Fizetés", payLabel(j), true]);', 'facts.push(["Pay", payLabel(j), true]);')
sub('facts.push(["Heti óraszám", j.hours + " óra", true]);', 'facts.push(["Hours / week", j.hours + " h", true]);')
sub('facts.push(["Munka típusa", j.jobType, false]);', 'facts.push(["Job type", j.jobType, false]);')
sub('facts.push(["Munkavégzés", j.remote ? "Távmunka / hibrid lehetséges" : "Helyszíni", false]);',
    'facts.push(["Work mode", j.remote ? "Remote / hybrid possible" : "On-site", false]);')
sub('facts.push(["Munkarend", j.schedule, false]);', 'facts.push(["Schedule", j.schedule, false]);')
sub('facts.push(["Hallgatói jogviszony", j.student, false]);', 'facts.push(["Student status", j.student, false]);')
sub('facts.push(["Végzettség", j.degree, false]);', 'facts.push(["Education", j.degree, false]);')
sub('facts.push(["Kezdés", j.start, true]);', 'facts.push(["Start", j.start, true]);')
sub('facts.push(["Jelentkezési határidő", j.deadline, true]);', 'facts.push(["Application deadline", j.deadline, true]);')
sub('facts.push(["Meghirdetve", ago(j.posted), false]);', 'facts.push(["Posted", ago(j.posted), false]);')
sub('facts.push(["Forrás", j.src + (j.src === "profession.hu" ? " · pillanatkép " + PROF_SNAPSHOT_DATE : " · élő"), false]);',
    'facts.push(["Source", j.src + (j.src === "profession.hu" ? " · snapshot " + PROF_SNAPSHOT_DATE : " · live"), false]);')
sub('\'<button class="close" type="button">← Vissza a listához</button>\'',
    '\'<button class="close" type="button">← Back to list</button>\'')
sub('rel="noopener noreferrer">Megnyitás a \' + esc(j.src) + "-on</a>"',
    'rel="noopener noreferrer">Open on \' + esc(j.src) + "</a>"')
sub('(SAVED.has(j.key) ? "★ Mentve" : "☆ Mentés")', '(SAVED.has(j.key) ? "★ Saved" : "☆ Save")')
sub('<h4>Szakterület</h4>', '<h4>Field</h4>')
sub('<h4>Nyelvtudás</h4>', '<h4>Languages</h4>')
sub('<h4>Készségek</h4>', '<h4>Skills</h4>')

# ---------------------------------------------------------------- counts, status, errors
sub('"<b>" + rows.length + "</b> állás" +\n    (rows.length !== JOBS.length ? " a(z) " + JOBS.length + " közül" : "");',
    '"<b>" + rows.length + "</b> " + (rows.length === 1 ? "job" : "jobs") +\n    (rows.length !== JOBS.length ? " of " + JOBS.length : "");')
sub('"<b>A zyntern.com élő állásai most nem érhetők el</b>" +\n'
    '    "A lenti lista így csak a beépített profession.hu állásokat mutatja. " +\n'
    '    "A böngésző ezt a hibát adta: <code>" + esc(err && err.message ? err.message : String(err)) + "</code>. " +\n'
    '    "A leggyakoribb ok, hogy az oldalt olyan helyen nyitottad meg, ahol a külső hálózati hívás tiltott. " +\n'
    '    "Töltsd le a fájlt, és nyisd meg közvetlenül a böngésződben (dupla kattintás), vagy indíts egy helyi szervert a fájl mappájában:<br>" +',
    '"<b>The live zyntern.com jobs can\'t be reached right now</b>" +\n'
    '    "The list below therefore shows only the built-in profession.hu jobs. " +\n'
    '    "The browser reported: <code>" + esc(err && err.message ? err.message : String(err)) + "</code>. " +\n'
    '    "The usual cause is opening this page somewhere that blocks outgoing network calls. " +\n'
    '    "Download the file and open it directly in your browser (double-click it), or start a local server in its folder:<br>" +')
sub('setStatus("p", "snap", "profession.hu · pillanatkép " + PROF_SNAPSHOT_SHORT);',
    'setStatus("p", "snap", "profession.hu · snapshot " + PROF_SNAPSHOT_SHORT);')
sub('setStatus("z", "live", "zyntern.com · élő " +', 'setStatus("z", "live", "zyntern.com · live " +')
sub('setStatus("z", "snap", "zyntern.com · nem elérhető");', 'setStatus("z", "snap", "zyntern.com · unavailable");')
sub('var PROF_SNAPSHOT_DATE = "2026. szeptember 16.";', 'var PROF_SNAPSHOT_DATE = "16 September 2026";')
sub('var PROF_SNAPSHOT_SHORT = "09.16.";', 'var PROF_SNAPSHOT_SHORT = "16 Sep";')
sub('http://localhost:8000/allaskereso.html', 'http://localhost:8000/internship_finder.html')

# ---------------------------------------------------------------- comments
sub('''   1. KÉT ADATFORRÁS

   a) zyntern.com — ÉLŐ. Van nyilvános JSON API-ja, nincs API kulcs és
      nincs bejelentkezés, ráadásul "access-control-allow-origin: *"
      fejlécet küld, ezért ez az oldal közvetlenül le tudja kérni a
      böngészőből, minden megnyitáskor frissen.

   b) profession.hu — PILLANATKÉP. Nincs API-ja, és nem enged
      böngészőből érkező kérést (nincs CORS fejléce), ezért az adatait
      előre begyűjtöttük és bele van építve ebbe a fájlba. Frissítéshez
      a gyűjtést újra le kell futtatni — a "Frissítés" gomb ezt a
      forrást nem tudja újratölteni.''',
'''   1. TWO DATA SOURCES

   a) zyntern.com — LIVE. It has a public JSON API: no key, no login, and
      it sends "access-control-allow-origin: *", so this page can call it
      straight from the browser and gets fresh data on every open.

   b) profession.hu — SNAPSHOT. No API, and it refuses requests coming
      from a browser page (it sends no CORS headers), so its jobs were
      harvested in advance and are built into this file. Refreshing them
      means re-running the harvest — the "Refresh" button cannot reload
      this source.''')
sub('''/* Budapest + gyakornoki / diákmunka / nincs tapasztalat szűrőkkel,
   a négy célterületre szűkítve (pénzügy, értékesítés, marketing, menedzsment).
   Oszlopok: id, cím, cég, város, helyszín, szakterület, alterület, típus,
   távmunka, bér, bér szövegesen, periódus, bruttó/nettó, feladva, link, munkarend */''',
'''/* Budapest, filtered to internship / student job / no-experience adverts and
   narrowed to the four target fields (finance, sales, marketing, management).
   Columns: id, title, company, city, location, field, sub-field, type,
   remote, pay, pay formatted, period, gross/net, posted, link, schedule */''')
sub('''/* a beépített profession.hu sorokat ugyanarra az alakra hozzuk,
   mint amit a Zyntern API ad, hogy egy listában kezelhessük őket */''',
'''/* Reshape the built-in profession.hu rows into exactly the shape the Zyntern
   API returns, so both sources can be handled as one list. */''')
sub('/* ---------- API betöltés ---------- */', '/* ---------- API loading ---------- */')
sub('/* ---------- szűrés ---------- */', '/* ---------- filtering ---------- */')
sub('/* egy facet értékeinek darabszáma úgy, hogy az adott facetet nem szűrjük */',
    '/* Count a facet\'s values while ignoring that facet\'s own selection, so the\n   numbers show what each option would add rather than what is already on. */')
sub('/* ---------- szűrő definíciók ---------- */', '/* ---------- filter definitions ---------- */')
sub('/* ---------- szűrősáv ---------- */', '/* ---------- filter bar ---------- */')
sub('/* a panelt szándékosan nyitva hagyjuk, hogy többet is be lehessen pipálni */',
    '/* deliberately leave the panel open so several boxes can be ticked */')
sub('/* ---------- aktív szűrők chipjei ---------- */', '/* ---------- active filter chips ---------- */')
sub('/* ---------- lista ---------- */', '/* ---------- results list ---------- */')
sub('/* ---------- részletek ---------- */', '/* ---------- detail pane ---------- */')
sub('''/* a találatokat frissíti, a szűrősávot nem bántja — így a nyitott
   legördülő panel nyitva marad több pipálás közben is */''',
'''/* Redraw the results without touching the filter bar, so an open dropdown
   stays open while several boxes are ticked. */''')
sub('/* ---------- fő render ---------- */', '/* ---------- main render ---------- */')
sub('/* ---------- betöltés ---------- */', '/* ---------- loading ---------- */')
sub('/* a beépített profession.hu adat azonnal látszik, nem kell rá várni */',
    '/* the built-in profession.hu data shows immediately — no waiting on the network */')
sub('/* ---------- események ---------- */', '/* ---------- events ---------- */')

# ------------------------------------------------- bilingual search index
# The categories are translated but the advert titles stay Hungarian, so keep
# the original Hungarian category names on the record too and search both.
sub('    fields: (j.fields || []).map(function(f){ return tr(FIELD_EN, f.name); }),',
    '    fields: (j.fields || []).map(function(f){ return tr(FIELD_EN, f.name); }),\n'
    '    fieldsHu: (j.fields || []).map(function(f){ return f.name; }),')
sub('    fields: [tr(FIELD_EN, r[5]), tr(FIELD_EN, r[6])].filter(Boolean),',
    '    fields: [tr(FIELD_EN, r[5]), tr(FIELD_EN, r[6])].filter(Boolean),\n'
    '    fieldsHu: [r[5], r[6]].filter(Boolean),')
sub('    var hay = (j.title + " " + j.company + " " + j.fields.join(" ") + " " +\n'
    '               j.skills.join(" ")).toLowerCase();',
    '    /* search both languages: English categories and the Hungarian originals */\n'
    '    var hay = (j.title + " " + j.company + " " + j.fields.join(" ") + " " +\n'
    '               (j.fieldsHu || []).join(" ") + " " + j.jobType + " " +\n'
    '               j.skills.join(" ")).toLowerCase();')

if missing:
    print("NOT FOUND (%d):" % len(missing))
    for m in missing:
        print("   ", repr(m))

if not os.path.isdir(BUILD_DIR):
    os.makedirs(BUILD_DIR)
io.open(os.path.join(BUILD_DIR, 'template_en.html'), 'w', encoding='utf-8').write(h)

rows = json.load(io.open(DATA, encoding='utf-8'))
lit = "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]"
marker = "var PROF_ROWS = /*__PROF_DATA__*/[];"
assert marker in h, "data marker missing"
io.open(OUT, 'w', encoding='utf-8').write(h.replace(marker, "var PROF_ROWS = " + lit + ";"))
print("built %s  (%d profession.hu jobs embedded)" % (os.path.relpath(OUT, ROOT), len(rows)))
