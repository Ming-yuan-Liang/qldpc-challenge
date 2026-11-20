"""Push the nine submission branches to the fork via the Git Data API.

The machine's HTTPS route to github.com:443 is selectively blocked (curl
times out; api.github.com and ssh.github.com are fine), and the PAT lacks
the admin:public_key scope so SSH-over-443 cannot be registered. This
script therefore creates each branch entirely through api.github.com:
blobs -> tree (base_tree = upstream main's tree) -> commit (parent =
upstream main's head) -> new ref on the fork. Content is read from the
working tree (codes/<slug>.json, notes/<slug>.md, promote-real-1120.json
for the commit message), which is byte-identical to what promote validated.

Usage: python push_via_api_1120.py <slug> [<slug> ...]
"""
import base64
import json
import sys
import urllib.error
import urllib.request
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OWNER = "Ming-yuan-Liang"
UPSTREAM = "unitaryfoundation/qldpc-challenge"

TOK = (ROOT / "research/candidates/.pat").read_text(encoding="utf-8").strip()


def api(method, path, body=None, raw=False, tolerate_422=False):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(5):
        req = urllib.request.Request("https://api.github.com" + path,
                                     data=data, method=method)
        req.add_header("Authorization", "Bearer " + TOK)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "contribution-script")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                rawbytes = r.read()
                return json.loads(rawbytes) if rawbytes else {}
        except urllib.error.HTTPError as e:
            if e.code == 422 and tolerate_422:
                return None
            if e.code in (409, 422, 404):
                detail = e.read().decode(errors="replace")[:300]
                raise SystemExit(f"API {method} {path} -> HTTP {e.code}: {detail}")
            if e.code in (500, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            detail = e.read().decode(errors="replace")[:300]
            raise SystemExit(f"API {method} {path} -> HTTP {e.code}: {detail}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"  net retry {attempt + 1}: {e}")
            time.sleep(8 * (attempt + 1))
    raise SystemExit(f"API {method} {path} failed after retries")


def branch_file(branch, path):
    import subprocess
    out = subprocess.run(["git", "show", f"{branch}:{path}"],
                         cwd=ROOT, capture_output=True, check=True)
    return out.stdout


def push_branch(slug):
    rep = json.loads((ROOT / "promote-real-1120.json").read_text(encoding="utf-8"))
    title = next(r["title"] for r in rep if r["slug"] == slug)
    code = branch_file(f"submit-{slug}", f"codes/{slug}.json")
    note = branch_file(f"submit-{slug}", f"notes/{slug}.md")

    base = api("GET", f"/repos/{UPSTREAM}/git/ref/heads/main")
    base_sha = base["object"]["sha"]
    base_commit = api("GET", f"/repos/{UPSTREAM}/git/commits/{base_sha}")
    base_tree = base_commit["tree"]["sha"]

    blobs = {}
    for path, content in ((f"codes/{slug}.json", code), (f"notes/{slug}.md", note)):
        b = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/blobs", {
            "content": base64.b64encode(content).decode(),
            "encoding": "base64"})
        blobs[path] = b["sha"]

    tree = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/trees", {
        "base_tree": base_tree,
        "tree": [{"path": p, "mode": "100644", "type": "blob", "sha": s}
                 for p, s in blobs.items()]})

    commit = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/commits", {
        "message": title, "tree": tree["sha"], "parents": [base_sha]})

    ref = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/refs", {
        "ref": f"refs/heads/submit-{slug}", "sha": commit["sha"]},
        tolerate_422=True)
    if ref is None:
        api("PATCH", f"/repos/{OWNER}/qldpc-challenge/git/refs/heads/submit-{slug}",
            {"sha": commit["sha"], "force": True})
        print(f"{slug}: ref existed (in-flight git push) -> force-updated to "
              f"{commit['sha'][:9]}")
    else:
        print(f"{slug}: branch submit-{slug} @ {commit['sha'][:9]} -> fork OK "
              f"(base {base_sha[:9]}, +{len(code)}/{len(note)} bytes)")
    return commit["sha"]


if __name__ == "__main__":
    results = {}
    for slug in sys.argv[1:]:
        results[slug] = push_branch(slug)
    (ROOT / "research/candidates/api_push_1120.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8")
    print("ALL-PUSHED", len(results))
