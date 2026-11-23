"""Deterministically replay a rung's search stream to recover its witness.
Usage: replay_witness.py <doc.json> <seed> <trials> <pd>
Rung7 of 16-127: seed 91000+7*101+16 = 91723, 1M trials, pd12 (fast).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

import numpy as np
from surrogate import distance_rand_witness


def dense(rows, n):
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, sup in enumerate(rows):
        m[i, list(sup)] = 1
    return m


def main():
    doc_p, seed, trials, pd = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    doc = json.load(open(doc_p, encoding="utf-8"))
    n = doc["n"]
    hx = dense(doc["checks"]["X"], n)
    hz = dense(doc["checks"]["Z"], n)
    w = distance_rand_witness(HX=hx, HZ=hz, trials=trials, seed=seed,
                              backend="fast", pair_depth=pd)
    print(f"side={w.side} weight={w.weight} rejected={w.rejected!r}")
    if not w.rejected and w.weight is not None:
        out = {"side": w.side, "weight": int(w.weight),
               "support": sorted(int(x) for x in w.support),
               "seed": seed, "trials": trials, "pair_depth": pd}
        p = HERE / f"replay-{Path(doc_p).stem}-seed{seed}.json"
        json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
        print("saved", p.name)


if __name__ == "__main__":
    main()
