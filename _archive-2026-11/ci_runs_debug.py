import json, urllib.request, datetime, sys
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
p = api("/repos/unitaryfoundation/qldpc-challenge/pulls/6936")
head = p["head"]["sha"]
print("PR6936 head:", head[:9], "repo:", p["head"]["repo"]["full_name"])
d = api(f"/repos/Ming-yuan-Liang/qldpc-challenge/actions/runs?head_sha={head}&per_page=10")
print("total_count:", d["total_count"])
for r in d["workflow_runs"]:
    age = now - datetime.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
    print(f'{r["name"]:18s} {r["status"]:10s} concl={r["conclusion"]} age={int(age.total_seconds()//60)}min started={r["run_started_at"]} id={r["id"]}')
