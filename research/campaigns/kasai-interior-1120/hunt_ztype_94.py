"""ker(HX)\rsp(HZ) logical hunt for 544-16-94 (Z-TYPE witness for distance.Z).

The replay's rung9 witness (w=79) is X-type (commutes HZ) and the ker(HZ)
hunt (w=85) is also X-type — both bound d_X. The claim is min(d_X, d_Z);
if the Z-type distance is < 76 the code is dominated by 544-20-76. This
hunt (swapped _search_lightest(hz, hx) = ker(HX)\rsp(HZ)) bounds d_Z.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

import numpy as np
from surrogate import _search_lightest, validate_logical

trials = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
doc = json.load(open(ROOT / "research/candidates/a1-kasai-1120/544-16-94.json",
                     encoding="utf-8"))
n = doc["n"]
def dense(rows):
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, sup in enumerate(rows):
        m[i, list(sup)] = 1
    return m
hx, hz = dense(doc["checks"]["X"]), dense(doc["checks"]["Z"])
seed = 88004
w, sup = _search_lightest(hz, hx, trials, np.random.SeedSequence(seed),
                          pair_depth=10)
print(f"ker(HX)-side (Z-type) search (544-16-94): weight={w} at {trials} trials (numpy, seed {seed})")
if w == float("inf"):
    raise SystemExit("no ker(HX) logical found - raise trials")
ok, why = validate_logical(hz, hx, "Z", int(w), list(sup))
print("validate_logical(Z):", ok, why)
v = np.zeros(n, dtype=np.uint8); v[list(sup)] = 1
print("commutes_with_HX:", (hx @ v % 2).sum() == 0,
      "| commutes_with_HZ:", (hz @ v % 2).sum() == 0)
out = {"side": "Z", "weight": int(w), "support": sorted(int(q) for q in sup),
       "seed": seed, "trials": trials, "pair_depth": 10, "backend": "numpy"}
json.dump(out, open(Path(__file__).parent / "hunt-ztype-94-88004.json", "w",
                    encoding="utf-8"), indent=1)
print("saved hunt-ztype-94-88004.json")
