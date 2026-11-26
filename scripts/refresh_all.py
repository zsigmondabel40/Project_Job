"""Refresh both snapshot portals and rebuild the app. One command.

    python scripts/refresh_all.py                 # both portals, then rebuild
    python scripts/refresh_all.py profession      # just profession.hu
    python scripts/refresh_all.py cvonline        # just cvonline.hu

This is what the daily 10:00 schedule runs. Takes about five minutes, most of
it the deliberate 10-second pause cvonline.hu's robots.txt asks for.

Needs:  pip install requests beautifulsoup4

WHAT IT DOES, AND WHAT IT DELIBERATELY DOES NOT DO

  1. scripts/scrape_profession.py  ->  data/prof_rows.json
  2. scripts/scrape_cvonline.py    ->  data/cvonline_rows.json
  3. src/build_english.py          ->  internship_finder.html

If a portal is down, times out or changes its markup, that scraper exits
non-zero WITHOUT writing anything, so the previous snapshot survives. This
script then carries on to the next step, and the app is rebuilt from whatever
data is on disk. A bad day therefore leaves you with yesterday's jobs, never
with an empty app. The exit code is still non-zero so the schedule reports a
failure rather than pretending everything worked.

zyntern.com is not here on purpose: it is fetched live by the page itself
every time you open it, so there is nothing to refresh in advance.
"""

import datetime
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Each scraper gets its own generous ceiling so one hung request cannot leave
# the scheduled task running forever.
STEPS = {
    "profession": ("profession.hu", os.path.join(HERE, "scrape_profession.py"), 20 * 60),
    "cvonline":   ("cvonline.hu",   os.path.join(HERE, "scrape_cvonline.py"),   20 * 60),
}
BUILD = os.path.join(ROOT, "src", "build_english.py")


def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(label, script, timeout):
    """Run one script. True if it succeeded."""
    print("\n[%s] %s" % (stamp(), label))
    print("-" * 60, flush=True)
    try:
        result = subprocess.run([sys.executable, script], cwd=ROOT, timeout=timeout)
    except subprocess.TimeoutExpired:
        print("!! timed out after %d minutes — previous data kept." % (timeout // 60))
        return False
    except OSError as err:
        print("!! could not start it: %s" % err)
        return False
    if result.returncode != 0:
        print("!! failed (exit code %d) — previous data kept." % result.returncode)
        return False
    return True


def main(argv):
    wanted = [a.lower() for a in argv[1:]] or list(STEPS)
    unknown = [w for w in wanted if w not in STEPS]
    if unknown:
        print("Unknown portal(s): %s" % ", ".join(unknown))
        print("Choose from: %s" % ", ".join(STEPS))
        return 2

    print("=" * 60)
    print("Refreshing: %s" % ", ".join(STEPS[w][0] for w in wanted))
    print("Started %s" % stamp())
    print("=" * 60)

    failed = [STEPS[w][0] for w in wanted if not run(*STEPS[w])]

    # Rebuild whatever happened above: with fresh data if the scrapers worked,
    # with the previous data if they did not. Either way the app stays valid.
    print("\n[%s] rebuilding the app" % stamp())
    print("-" * 60, flush=True)
    build_ok = subprocess.run([sys.executable, BUILD], cwd=ROOT).returncode == 0

    print("\n" + "=" * 60)
    if failed:
        print("DONE WITH PROBLEMS — these portals were not refreshed: %s" % ", ".join(failed))
        print("Their previous jobs are still in the app.")
    if not build_ok:
        print("THE REBUILD FAILED — internship_finder.html was not updated.")
    if not failed and build_ok:
        print("DONE — everything refreshed and the app rebuilt.")
    print("Finished %s" % stamp())
    print("=" * 60)

    return 0 if (build_ok and not failed) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
