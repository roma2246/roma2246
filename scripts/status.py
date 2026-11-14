#!/usr/bin/env python3
"""Rebuilds assets/status.svg (dark, own background) from real commits.

Only counts are rendered: no repo names, no commit messages.

Env:
  GH_USER     GitHub login (default: roma2246)
  GH_NAMES    comma-separated author names that are also me (commits made
              with an email that is not linked to the account)
  GH_TOKEN    API token. GITHUB_TOKEN sees public repos only; a classic PAT
              with `repo` scope plus GH_PRIVATE=1 also counts private ones.
  GH_PRIVATE  "1" to list repos via /user/repos
  TZ_NAME     timezone used for days and "night" (default: Asia/Almaty)
"""
import json
import os
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, time, timedelta, timezone
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

USER = os.environ.get("GH_USER", "roma2246")
NAMES = {n.strip().lower() for n in os.environ.get("GH_NAMES", "Ramazan Gabdulgumarov,roma2246").split(",") if n.strip()}
TOKEN = os.environ.get("GH_TOKEN", "")
PRIVATE = os.environ.get("GH_PRIVATE") == "1"
TZ = ZoneInfo(os.environ.get("TZ_NAME", "Asia/Almaty"))
DAYS = 45
NIGHT_HOURS = range(0, 5)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

ALIASES = {"JavaScript": "TypeScript / JS", "TypeScript": "TypeScript / JS", "Jupyter Notebook": "Python"}
IGNORED = {"HTML", "CSS", "SCSS", "Shell", "Dockerfile", "Makefile", "Batchfile", "PowerShell", "PLpgSQL",
           "TSQL", "Procfile", "CMake", "C++", "C", "Swift", "Kotlin", "Objective-C", "Ruby", "Roff", "MDX"}
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
          "сентября", "октября", "ноября", "декабря"]


# ------------------------------------------------------------------ api
def api(url):
    if not url.startswith("http"):
        url = "https://api.github.com" + url
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-status-svg"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        data = json.load(r)
        nxt = None
        for part in r.headers.get("Link", "").split(","):
            if 'rel="next"' in part:
                nxt = part[part.find("<") + 1:part.find(">")]
    return data, nxt


def paged(url, pages=10):
    out = []
    for _ in range(pages):
        data, url = api(url)
        out += data
        if not url:
            break
    return out


def is_mine(c):
    if (c.get("author") or {}).get("login", "").lower() == USER.lower():
        return True
    return c["commit"]["author"]["name"].strip().lower() in NAMES


def collect():
    today = datetime.now(TZ).date()
    start = today - timedelta(days=DAYS - 1)
    since = datetime.combine(start, time.min, TZ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if PRIVATE:
        repos = paged("/user/repos?affiliation=owner,collaborator,organization_member&per_page=100")
    else:
        repos = paged(f"/users/{USER}/repos?type=owner&per_page=100")

    seen = set()
    total = Counter()
    nights = Counter()
    lang_days = defaultdict(Counter)
    lang_last = {}
    for repo in repos:
        if not repo.get("pushed_at") or repo["pushed_at"] < since:
            continue
        name = repo["full_name"]
        try:
            commits = paged(f"/repos/{name}/commits?since={since}&per_page=100")
            raw_langs, _ = api(f"/repos/{name}/languages")
        except urllib.error.HTTPError:  # empty repo, blocked, no access
            continue

        langs = Counter()
        for lang, size in raw_langs.items():
            if lang not in IGNORED:
                langs[ALIASES.get(lang, lang)] += size
        weight = sum(langs.values()) or 1
        langs = [lang for lang, size in langs.items() if size / weight >= 0.15]

        for c in commits:
            if c["sha"] in seen or not is_mine(c):
                continue
            seen.add(c["sha"])
            when = datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00")).astimezone(TZ)
            day = when.date()
            if day < start:
                continue
            total[day] += 1
            if when.hour in NIGHT_HOURS:
                nights[day] += 1
            for lang in langs:
                lang_days[lang][day] += 1
                lang_last[lang] = max(lang_last.get(lang, day), day)

    days = [start + timedelta(days=i) for i in range(DAYS)]
    top = sorted(lang_days, key=lambda lang: -sum(lang_days[lang].values()))[:5]
    return dict(today=today, days=days, total=total, nights=nights,
                langs=[(lang, lang_days[lang], lang_last[lang]) for lang in top])


# ------------------------------------------------------------------ svg
THEME = dict(bg="#0d1117", border="#30363d", fg="#e6edf3", dim="#7d8590", line="#21262d", empty="#161b22",
             green=["#0e4429", "#006d32", "#26a641", "#39d353"], red="#f85149", yellow="#d29922")
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def ago(today, day):
    d = (today - day).days
    return "сегодня" if d == 0 else "вчера" if d == 1 else f"{d} дн. назад"


def level(n):
    return 0 if n <= 1 else 1 if n <= 3 else 2 if n <= 6 else 3


def render(data, t):
    W, X, BX, CELL, GAP = 960, 24, 268, 9, 3
    RH, top = 46, 112
    today, days = data["today"], data["days"]
    rows = []  # (title, subtitle, cells[(color or None)], right text, right color)

    commits = sum(data["total"].values())
    active = sum(1 for d in days if data["total"][d])
    rows.append(("Все коммиты", f"{commits} {plural(commits, 'коммит', 'коммита', 'коммитов')} · {active} акт. дней",
                 [t["green"][level(data["total"][d])] if data["total"][d] else None for d in days],
                 f"{commits / DAYS:.1f} в день", t["dim"]))

    for lang, per_day, last in data["langs"]:
        n = sum(per_day.values())
        idle = (today - last).days
        state, color = (("работает", t["green"][2]) if idle <= 7 else
                        ("пауза", t["yellow"]) if idle <= 21 else ("спит", t["dim"]))
        rows.append((lang, f"{n} {plural(n, 'коммит', 'коммита', 'коммитов')} · последний {ago(today, last)}",
                     [t["green"][level(per_day[d])] if per_day[d] else None for d in days], state, color))

    nights = sum(1 for d in days if data["nights"][d])
    rows.append(("Сон", f"коммиты с 00:00 до 05:00 · {nights} {plural(nights, 'ночь', 'ночи', 'ночей')} из {DAYS}",
                 [t["red"] if data["nights"][d] else None for d in days],
                 "сбой" if nights >= 10 else "есть вопросы" if nights >= 4 else "в норме",
                 t["red"] if nights >= 10 else t["yellow"] if nights >= 4 else t["green"][2]))

    H = top + RH * len(rows) + 40
    overall_bad = nights >= 10
    stamp = f"{today.day} {MONTHS[today.month - 1]} {today.year}"

    cells_svg, text_svg = [], []
    for r, (title, sub, cells, right, rcolor) in enumerate(rows):
        y = top + r * RH
        text_svg.append(f'<text x="{X}" y="{y - 3}" font-size="14" font-weight="600" fill="{t["fg"]}">{escape(title)}</text>'
                        f'<text x="{X}" y="{y + 14}" font-size="12" fill="{t["dim"]}">{escape(sub)}</text>'
                        f'<text x="{W - X}" y="{y + 5}" text-anchor="end" font-size="13" fill="{rcolor}">{escape(right)}</text>')
        for i, color in enumerate(cells):
            delay = i * 0.012 + r * 0.05
            cells_svg.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{BX + i * (CELL + GAP)}" '
                             f'y="{y - CELL // 2 - 1}" width="{CELL}" height="{CELL}" rx="2" fill="{color or t["empty"]}"/>')
        if r < len(rows) - 1:
            text_svg.append(f'<line x1="{X}" x2="{W - X}" y1="{y + RH / 2 + 2}" y2="{y + RH / 2 + 2}" stroke="{t["line"]}"/>')

    if len(rows) == 2:
        text_svg.append(f'<text x="{BX}" y="{top + RH + 30}" font-size="12" fill="{t["dim"]}">'
                        f'по языкам пусто: за {DAYS} дней не нашлось доступных коммитов</text>')

    status_color = t["red"] if overall_bad else t["green"][2]
    status_text = "частичный сбой (сон)" if overall_bad else "всё работает"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}" role="img" aria-label="Статус roma2246: {commits} коммитов за {DAYS} дней, {nights} ночных">
  <style>.c{{animation:in .4s ease-out both}}@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <text x="{X}" y="38" font-size="20" font-weight="600" fill="{t["fg"]}">{USER}<tspan fill="{t["dim"]}" font-weight="400"> / status</tspan></text>
  <circle cx="{W - X - 6}" cy="32" r="5" fill="{status_color}"/>
  <text x="{W - X - 20}" y="37" text-anchor="end" font-size="14" fill="{t["fg"]}">{status_text}</text>
  <text x="{X}" y="64" font-size="12" fill="{t["dim"]}">последние {DAYS} дней · обновлено {stamp} · считается GitHub Action'ом раз в сутки</text>
  <g font-family="{MONO}" font-size="11" fill="{t["dim"]}">
    <text x="{BX}" y="{top - 30}">{days[0].day:02d}.{days[0].month:02d}</text>
    <text x="{BX + (DAYS - 1) * (CELL + GAP) + CELL}" y="{top - 30}" text-anchor="end">сегодня</text>
  </g>
  {"".join(text_svg)}
  {"".join(cells_svg)}
</svg>
'''


def main():
    data = collect()
    with open(os.path.join(ROOT, "assets", "status.svg"), "w", encoding="utf-8") as f:
        f.write(render(data, THEME))
    print(f"{sum(data['total'].values())} commits, langs: {[lang for lang, *_ in data['langs']]}")


if __name__ == "__main__":
    main()
