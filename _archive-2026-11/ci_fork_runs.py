import json, urllib.request, datetime
from pathlib import Path
ROOT = Path(r"C:\Users\Frieren\Documents\QEC\qldpc\qldpc-challenge")
TOK = (ROOT / "research/candidates/.pat").read_text(encoding="utf-8").strip()
def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("User-Agent", "ci-supervision")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())
now = datetime.datetime.now(datetime.timezone.utc)
perm = api("/repos/Ming-yuan-Liang/qldpc-challenge/actions/permissions")
print("actions permissions:", perm)
d = api("/repos/Ming-yuan-Liang/qldpc-challenge/actions/runs?per_page=15")
print("fork total runs:", d["total_count"])
for r in d["workflow_runs"]:
    age = now - datetime.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
    print(f'{r["name"]:18s} {r["status"]:10s} concl={str(r["conclusion"]):9s} branch={r["head_branch"]:22s} head={r["head_sha"][:9]} age={int(age.total_seconds()//60)}min id={r["id"]}')
