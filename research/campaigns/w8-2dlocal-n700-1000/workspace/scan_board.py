import json, glob, os

rows = []
for f in glob.glob('codes/*.json'):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    loc = d.get('locality')
    if not isinstance(loc, dict):
        continue
    layers = loc.get('layers', 1)
    if layers != 2:
        continue
    n = d.get('n'); k = d.get('k')
    dist = d.get('distance')
    dv = dist if isinstance(dist, int) else (dist or {}).get('d')
    # max check weight from checks block
    ch = d.get('checks') or {}
    wx = max((len(r) for r in ch.get('X', [])), default=0)
    wz = max((len(r) for r in ch.get('Z', [])), default=0)
    rows.append((n, k, dv, max(wx, wz), os.path.basename(f)))

rows.sort()
bil = [r for r in rows]
print(f"{len(bil)} bilayer (layers=2) entries total")
# frontier in and near window
win = [r for r in bil if 350 <= (r[0] or 0) <= 1200]
for r in win:
    print(r)
