"""Recover the finalize Z-call witness (swapped roles): kernel(HX) search
under CLI convention = commutes with H_Z. Usage: replay_zside.py <trials>"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

import numpy as np
from surrogate import distance_rand_witness

trials = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
doc = json.load(open(ROOT / "research/candidates/a1-kasai-1120/684-18-106.json",
                     encoding="utf-8"))
n = doc["n"]
def dense(rows):
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, sup in enumerate(rows):
        m[i, list(sup)] = 1
    return m
hx, hz = dense(doc["checks"]["X"]), dense(doc["checks"]["Z"])
seed = 71235  # finalize pass-1 Z-call seed (deterministic)
w = distance_rand_witness(HX=hz, HZ=hx, trials=trials, seed=seed,
                          backend="fast", pair_depth=12)
print(f"recovered: weight={w.weight} rejected={w.rejected!r}")
v = np.zeros(n, dtype=np.uint8); v[list(w.support)] = 1
print("commutes_with_HZ:", (hz @ v % 2).sum() == 0,
      "| commutes_with_HX:", (hx @ v % 2).sum() == 0)
out = {"side": "Z", "weight": int(w.weight),
       "support": sorted(int(x) for x in w.support),
       "seed": seed, "trials": trials, "pair_depth": 12}
json.dump(out, open(Path(__file__).parent / "replay-zside-71235.json", "w",
                    encoding="utf-8"), indent=1)
print("saved replay-zside-71235.json")
