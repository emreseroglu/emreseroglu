"""Scrape the public GitHub contribution calendar (no token needed) -> data/contributions.json"""
import json, os, re, sys
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "emreseroglu")
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def main():
    r = requests.get(f"https://github.com/users/{USER}/contributions",
                     headers={"User-Agent": "profile-art-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # tooltips: <tool-tip for="contribution-day-component-0-0">3 contributions on May 1st.</tool-tip>
    tips = {}
    for t in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d[\d,]*) contribution", t.get_text())
        if t.get("for") and m:
            tips[t["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": tips.get(td.get("id"), 0),
        })
    if len(days) < 300:
        sys.exit(f"Parsed only {len(days)} days - GitHub markup may have changed; not writing.")
    days.sort(key=lambda d: d["date"])

    # streaks (today may still be 0 -> don't break current streak on it)
    cur = longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
        elif d["date"] == date.today().isoformat() and cur == 0:
            continue
        else:
            break
    best = max(days, key=lambda d: d["count"])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "user": USER,
        "total": sum(d["count"] for d in days),
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": best,
        "days": days,
    }, indent=1))
    print(f"{len(days)} days, total {sum(d['count'] for d in days)}")


if __name__ == "__main__":
    main()
