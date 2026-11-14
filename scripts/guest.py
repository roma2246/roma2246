#!/usr/bin/env python3
"""Adds the author of a "👋" issue to the guest list in README.md.

Only the GitHub login is used (validated), never the issue title or body,
so nothing a visitor types ends up in the README.
"""
import json
import os
import re
import sys

MAX_GUESTS = 24
START, END = "<!-- guests:start -->", "<!-- guests:end -->"
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md")


def main():
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as f:
        event = json.load(f)
    user = event["issue"]["user"]
    login = user["login"]
    if user.get("type") != "User" or not LOGIN_RE.match(login):
        print(f"skip: {login!r}")
        return

    with open(README, encoding="utf-8") as f:
        text = f.read()
    head, rest = text.split(START, 1)
    block, tail = rest.split(END, 1)

    guests = re.findall(r'<a href="https://github\.com/([A-Za-z0-9-]+)"', block)
    guests = [login] + [g for g in guests if g.lower() != login.lower()]
    guests = guests[:MAX_GUESTS]

    links = "\n".join(f'<a href="https://github.com/{g}"><img src="https://github.com/{g}.png?size=80" '
                      f'width="40" height="40" alt="{g}" title="{g}"></a>' for g in guests)
    with open(README, "w", encoding="utf-8") as f:
        f.write(f"{head}{START}\n{links}\n{END}{tail}")
    print(f"added {login}, total {len(guests)}")


if __name__ == "__main__":
    sys.exit(main())
