"""API-channel push for the submit-684-16-110 branch + PR open (inline)."""
import base64
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOK = (ROOT / "research/candidates/.pat").read_text(encoding="utf-8").strip()
OWNER = "Ming-yuan-Liang"
UPSTREAM = "unitaryfoundation/qldpc-challenge"
TITLE = ("Add [[684,16,110]] Kasai affine 2BGA over Aff(F_19) at "
         "kd^2/n 283.0, n=684, k=16, d<=110")


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.github.com" + path,
                                 data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "contribution-script")
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def git_show(path, rev="submit-684-16-110"):
    import subprocess
    return subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                          capture_output=True, check=True).stdout


base = api("GET", f"/repos/{UPSTREAM}/git/ref/heads/main")
base_sha = base["object"]["sha"]
base_tree = api("GET", f"/repos/{UPSTREAM}/git/commits/{base_sha}")["tree"]["sha"]
blobs = {}
for p in ("codes/684-16-110.json", "notes/684-16-110.md"):
    b = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/blobs", {
        "content": base64.b64encode(git_show(p)).decode(),
        "encoding": "base64"})
    blobs[p] = b["sha"]
tree = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/trees", {
    "base_tree": base_tree,
    "tree": [{"path": k, "mode": "100644", "type": "blob", "sha": v}
             for k, v in blobs.items()]})
commit = api("POST", f"/repos/{OWNER}/qldpc-challenge/git/commits", {
    "message": TITLE, "tree": tree["sha"], "parents": [base_sha]})
try:
    api("POST", f"/repos/{OWNER}/qldpc-challenge/git/refs", {
        "ref": "refs/heads/submit-684-16-110", "sha": commit["sha"]})
    print("ref created @", commit["sha"][:9])
except Exception as e:
    api("PATCH", f"/repos/{OWNER}/qldpc-challenge/git/refs/heads/submit-684-16-110",
        {"sha": commit["sha"], "force": True})
    print("ref force-updated @", commit["sha"][:9])
body = (ROOT / "research/candidates/pr-body-684-16-110.md").read_text(encoding="utf-8")
pr = api("POST", f"/repos/{UPSTREAM}/pulls", {
    "title": TITLE, "body": body, "head": f"{OWNER}:submit-684-16-110",
    "base": "main"})
print("PR:", pr["html_url"], "| number:", pr["number"])
