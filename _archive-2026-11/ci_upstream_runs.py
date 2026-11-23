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
p = api("/repos/unitaryfoundation/qldpc-challenge/pulls/6936")
head = p["head"]["sha"]
d = api(f"/repos/unitaryfoundation/qldpc-challenge/actions/runs?head_sha={head}&per_page=12")
print("upstream runs for", head[:9], "total:", d["total_count"])
for r in d["workflow_runs"]:
    age = now - datetime.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
    st = r["run_started_at"] or ""
    print(f'{r["name"]:12s} {r["status"]:10s} concl={str(r["conclusion"]):9s} age={int(age.total_seconds()//60):4d}min started={st[11:19]} id={r["id"]}')
