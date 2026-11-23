import json, urllib.request, datetime
from pathlib import Path
ROOT = Path(r"C:\Users\Frieren\Documents\QEC\qldpc\qldpc-challenge")
TOK = (ROOT / "research/candidates/.pat").read_text(encoding="utf-8").strip()
def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("User-Agent", "ci-supervision")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())
now = datetime.datetime.now(datetime.timezone.utc)
d = api("/repos/Ming-yuan-Liang/qldpc-challenge/actions/runs?branch=submit-924-29-27&per_page=8")
for r in d["workflow_runs"]:
    age = now - datetime.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
    print(f'{r["name"]:12s} {r["status"]:10s} concl={r["conclusion"]} age={int(age.total_seconds()//60)}min head={r["head_sha"][:9]} run_id={r["id"]}')
