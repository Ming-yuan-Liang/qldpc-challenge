"""Open the nine L5+L6 PRs on upstream after promote + push.

Reads titles from promote-real-1120.json (promote's own report) and PR
bodies from research/candidates/pr-body-<slug>.md. Asserts the stored
PAT belongs to Ming-yuan-Liang before touching anything.
Usage: python open_prs_1120.py [--dry-run]
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OWNER = "Ming-yuan-Liang"
UPSTREAM = "unitaryfoundation/qldpc-challenge"

rep = json.loads((ROOT / "promote-real-1120.json").read_text(encoding="utf-8"))
SLUGS = [(r["slug"], r["title"]) for r in rep if r["ok"]]


def token():
    return (ROOT / "research/candidates/.pat").read_text(encoding="utf-8").strip()


def api(method, path, tok, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.github.com" + path, data=data,
                                 method=method)
    req.add_header("Authorization", "Bearer " + tok)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "contribution-script")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise SystemExit(f"API {method} {path} -> HTTP {e.code}: {detail}")


def main():
    dry = "--dry-run" in sys.argv
    tok = token()
    me = api("GET", "/user", tok)
    if me.get("login") != OWNER:
        raise SystemExit(f"credential identity {me.get('login')!r} != {OWNER!r}")
    print("credential identity:", me["login"])
    for slug, title in SLUGS:
        body = (ROOT / "research/candidates" / f"pr-body-{slug}.md").read_text(
            encoding="utf-8")
        if dry:
            print(f"[dry] {slug}: {title}")
            continue
        pr = api("POST", f"/repos/{UPSTREAM}/pulls", tok, body={
            "title": title,
            "head": f"{OWNER}:submit-{slug}",
            "base": "main",
            "body": body,
        })
        print("PR:", pr.get("html_url"))


if __name__ == "__main__":
    main()
