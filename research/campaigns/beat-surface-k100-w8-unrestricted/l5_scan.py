"""L5 board scan: refresh cache (board ff 7ea802a1f), derive dominance floors
for the lane cell (k 95-105, n 500-1000, w<=8, unrestricted), pull provenance
of the entries that set the floors.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "research", "campaigns",
                                "beat-surface-k50-w8-unrestricted"))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))

import numpy as np  # noqa: E402
from l4_board import Board, load_board  # noqa: E402

CACHE = os.path.join(HERE, "l5_board_cache.json")

rows = load_board(CACHE)   # rebuild from codes/ if cache missing
print(f"board CSS entries: {len(rows)}")

b = Board(CACHE)

# --- dominating set for the lane cell ------------------------------------
# candidate axes: n in [500,1000], k in [95,105], w=8; d unknown -> an entry
# dominates candidates with d <= entry.d.  For each n, the floor is
# max(d_e + 1) over entries with n_e <= n, k_e >= 105 (the safest: covers all
# k in the band), w_e <= 8; also track the k_e >= 95 case for k<=102 cands.
kmin, kmax = 95, 105
ksec = 95   # use k=95 as the binding candidate k (entries with k_e >= 105
            # dominate every k in band; k_e in [95,105) only dominate k<=k_e)

def floor_at(n, kc):
    best = None
    setter = None
    for (en, ek, ed, ew, name) in b.entries:
        if ew > 8:
            continue
        if ek < kc:
            continue
        if en <= n:
            if best is None or ed > best:
                best, setter = ed, (en, ek, ed, ew, name)
    return (best + 1 if best is not None else None), setter

print("\ndominance floors (w=8, need d strictly above the max entry d):")
print("n_band  k_e>=105 floor   setter            | k_e>=95 floor   setter")
bands = [(500, 567), (568, 631), (632, 711), (712, 903), (904, 927),
         (928, 1000)]
flo = {}
for lo, hi in bands:
    f1, s1 = floor_at(hi, 105)
    f2, s2 = floor_at(hi, 95)
    flo[(lo, hi)] = (f1, f2)
    print(f"{lo}-{hi}:  d>={f1}  {s1[4] if s1 else '-'}  ({s1[:4] if s1 else ''})"
          f"  |  d>={f2}  {s2[4] if s2 else '-'} ({s2[:4] if s2 else ''})")

# --- sample verdicts ------------------------------------------------------
print("\nsample verdicts (dominated_by count / advances):")
for (n, k, d) in [(500, 100, 16), (500, 100, 17), (700, 100, 19),
                  (700, 100, 20), (900, 100, 22), (900, 100, 23),
                  (960, 100, 23), (960, 105, 23), (560, 103, 17)]:
    dom, adv = b.verdict(n, k, d, 8)
    print(f"({n},{k},{d},w8): dominated_by={len(dom)} {dom[:2]} advances={len(adv)} {adv[:2]}")

# --- provenance of floor setters and family references --------------------
print("\nprovenance snippets:")
want = ["392-102-14", "288-76-12", "336-28-16", "300-36-13", "904-230-22",
        "928-238-22", "488-126-16", "568-146-18", "960-20-40", "432-112-14",
        "472-122-16", "330-34-14"]
codes = os.path.join(ROOT, "codes")
for fn in sorted(os.listdir(codes)):
    base = os.path.splitext(fn)[0]
    for w in want:
        if w in fn:
            doc = json.load(open(os.path.join(codes, fn), encoding="utf-8"))
            prov = doc.get("provenance", {})
            wmax = doc.get("weight_class") or ""
            checks = doc.get("checks", {})
            xs, zs = checks.get("X") or [], checks.get("Z") or []
            wcheck = max((len(s) for s in xs + zs), default=0)
            print(f"--- {base}  (n={doc.get('n')} k={doc.get('k')} "
                  f"d={doc.get('distance',{}).get('d')} w={wcheck} class={wmax} "
                  f"locality={doc.get('locality')})")
            for key in ("construction", "references", "notes"):
                v = prov.get(key)
                if v:
                    print(f"  {key}: {str(v)[:600]}")
            break

# top w<=8 entries with k>=95 (the whole competition in my cell)
print("\nall board entries with w<=8 and k>=95 (n<=1000), sorted by n:")
sel = sorted([e for e in b.entries if e[3] <= 8 and e[1] >= 95 and e[0] <= 1000])
for e in sel:
    print(f"  {e[0]}-{e[1]}-{e[2]} w{e[3]}  {e[4]}")
