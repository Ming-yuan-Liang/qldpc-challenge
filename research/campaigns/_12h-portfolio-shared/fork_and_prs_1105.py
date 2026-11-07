"""Fork the challenge repo under Ming-yuan-Liang and open the four PRs.

Reads the stored GCM credential via `git credential fill` (never printed).
Steps: assert token identity -> create/ensure fork -> (push handled in bash)
-> open one PR per code with the prepared bodies.
Usage: python fork_and_prs_1105.py <fork-only|prs-only>
"""
import json
import subprocess
import sys
import time
import urllib.request

OWNER = "Ming-yuan-Liang"
UPSTREAM = "unitaryfoundation/qldpc-challenge"
SLUGS = [
    ("684-14-115",
     "Add [[684,14,115]] Kasai affine 2BGA (kd^2/n 270.7, weight-9plus unrestricted frontier)"),
    ("684-12-117",
     "Add [[684,12,117]] Kasai affine 2BGA (kd^2/n 240.2, weight-9plus unrestricted frontier)"),
    ("544-18-82",
     "Add [[544,18,82]] Kasai affine 2BGA (kd^2/n 222.5, weight-9plus unrestricted frontier)"),
    ("684-8-116",
     "Add [[684,8,116]] Kasai affine 2BGA (weight-9plus unrestricted frontier extension)"),
]


def token():
    try:
        with open("research/candidates/.pat", encoding="utf-8") as f:
            t = f.read().strip()
        if t:
            return t
    except OSError:
        pass
    out = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True, check=True).stdout
    d = dict(line.split("=", 1) for line in out.strip().split("\n")
             if "=" in line)
    return d["password"]


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
    mode = sys.argv[1] if len(sys.argv) > 1 else "fork-only"
    tok = token()
    me = api("GET", "/user", tok)
    login = me.get("login")
    if login != OWNER:
        raise SystemExit(f"stored credential belongs to {login!r}, "
                         f"expected {OWNER!r}; aborting")
    print("credential identity:", login)

    if mode == "fork-only":
        fork = api("POST", f"/repos/{UPSTREAM}/forks", tok,
                   body={"default_branch_only": True})
        print("fork:", fork.get("full_name"), "|", fork.get("html_url"))
        for _ in range(60):
            try:
                api("GET", f"/repos/{OWNER}/qldpc-challenge", tok)
                print("fork ready")
                return
            except SystemExit:
                time.sleep(5)
        raise SystemExit("fork did not become ready in ~5 min")

    if mode == "prs-only":
        for slug, title in SLUGS:
            with open(f"research/candidates/pr-body-{slug}.md",
                      encoding="utf-8") as f:
                body = f.read()
            pr = api("POST", f"/repos/{UPSTREAM}/pulls", tok, body={
                "title": title,
                "head": f"{OWNER}:submit-{slug}",
                "base": "main",
                "body": body,
            })
            print("PR:", pr.get("html_url"))


if __name__ == "__main__":
    main()
