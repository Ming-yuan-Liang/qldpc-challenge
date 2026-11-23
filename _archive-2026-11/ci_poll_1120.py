import json, urllib.request
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
for n in (6930, 6931, 6932, 6933, 6934, 6935, 6936, 6937, 6938):
    p = api(f"/repos/unitaryfoundation/qldpc-challenge/pulls/{n}")
    head = p["head"]["sha"][:9]
    flags = []
    if p["merged"]:
        flags.append("MERGED")
    if p["state"] == "closed" and not p["merged"]:
        flags.append("CLOSED")
    line = f"#{n} {head} {' '.join(flags) or 'open'}  {p['title'][:70]}"
    print(line)
    if not flags:
        runs = api(f"/repos/unitaryfoundation/qldpc-challenge/commits/{p['head']['sha']}/check-runs")["check_runs"]
        latest = {}
        for c in sorted(runs, key=lambda x: x["id"]):
            latest[c["name"]] = (c["status"], c.get("conclusion"))
        for name, (st, cc) in sorted(latest.items()):
            print(f"    {name}: {st}/{cc}")
