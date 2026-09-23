"""
Match engine: scores each job listing against your CV and ranks them.

WHAT THIS DOES, IN PLAIN WORDS:
1. It reads your CV (cv.json) and turns it into a list of "keywords that matter"
   with a weight each — e.g. "kontrolling" is worth more than "marketing", because
   your CV is actually a controlling/finance background, not a marketing one.
   These weights are just a Python dictionary at the top of the file — you can
   open this script and change the numbers any time you disagree with them.
2. It reads a jobs file (a JSON list with the fields we've been using: id, job,
   position, industry, title, salary, url).
3. For every job, it checks the job's position + industry text for each keyword.
   Every keyword found adds its weight to that job's score. A job that matches
   "kontrolling" AND "pénzügy" AND "excel" scores higher than one that only
   matches "értékesítés".
4. It sorts all jobs by score, highest first, and saves the ranked list — with
   the score and WHICH keywords matched, so you can see why a job ranked where
   it did (not just a black-box number).

HOW TO RUN THIS:
    python match_engine.py cv.json profession_jobs_100.json matched_profession.json

(No extra libraries needed — just Python's built-in json module.)
"""

import json
import sys


# --- Keyword weights, derived from the CV ------------------------------------
# Higher weight = stronger signal that a job fits this CV.
# Feel free to tune these numbers, or add/remove keywords, based on what you
# actually want to prioritize.
CV_KEYWORDS = {
    # Core professional background: controlling / finance.
    "kontrolling": 10,
    "controlling": 10,
    "pénzügy": 8,
    "finance": 8,
    "financial": 7,
    "elemző": 7,
    "analyst": 7,
    "üzleti elemző": 8,
    "business analyst": 8,
    "könyvelés": 5,
    "accounting": 5,
    "számviteli": 4,

    # Sector specialization: agricultural finance / investment analysis.
    "agrár": 6,
    "agro": 6,
    "agri": 6,
    "mezőgazdasági": 6,

    # Skills explicitly listed on the CV.
    "excel": 4,

    # Some leadership evidence, but not the CV's main thrust, so lower
    # weight than finance/controlling.
    "menedzsment": 3,
    "management": 3,
    "vezető": 2,

    # Originally-stated interest fields with weak/no direct CV evidence —
    # kept, but weighted low so they don't outrank the actual finance
    # background unless a job title is a very strong match.
    "értékesítés": 2,
    "sales": 2,
    "marketing": 1,
    "business development": 1,
    "üzletfejlesztés": 1,
}


def score_job(job: dict) -> tuple[int, list[str]]:
    """Return (score, matched_keywords) for one job."""
    text = f"{job.get('position', '')} {job.get('industry', '')}".lower()
    score = 0
    matched = []
    for keyword, weight in CV_KEYWORDS.items():
        if keyword in text:
            score += weight
            matched.append(keyword)
    return score, matched


def main():
    if len(sys.argv) != 4:
        print("Usage: python match_engine.py <cv.json> <jobs.json> <output.json>")
        sys.exit(1)

    cv_path, jobs_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(cv_path, "r", encoding="utf-8") as f:
        cv = json.load(f)  # not currently used beyond documenting intent —
        # the real "CV" the scorer uses is the CV_KEYWORDS dict above, which
        # was written by reading the CV. Loading it here anyway so this script
        # is easy to extend into reading the CV's fields directly later.

    with open(jobs_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    ranked = []
    for job in jobs:
        score, matched = score_job(job)
        ranked.append({
            **job,
            "match_score": score,
            "matched_keywords": matched,
        })

    ranked.sort(key=lambda j: j["match_score"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)

    top = ranked[:5]
    print(f"Scored {len(ranked)} jobs from {jobs_path}.")
    print(f"Saved ranked list to {output_path}.\n")
    print("Top 5 matches:")
    for j in top:
        print(f"  [{j['match_score']:>2}] {j['position']} — {j['title']} ({', '.join(j['matched_keywords']) or 'no keyword match'})")


if __name__ == "__main__":
    main()
