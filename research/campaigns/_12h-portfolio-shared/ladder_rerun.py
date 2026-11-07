"""One fresh-seed confirmation rung for a staged candidate, for the promote
bundles. Usage: python ladder_rerun.py <doc.json> <rung_index> [trials]

Writes <doc>-rung<rung_index>.json beside the doc: {"trials", "d", "seed"}.
Fresh seed derived from the rung index; single-threaded numpy by design.
"""
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from surrogate import distance_rand  # noqa: E402


def dense(rows, n):
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, sup in enumerate(rows):
        m[i, list(sup)] = 1
    return m


def main():
    doc_path, rung = sys.argv[1], int(sys.argv[2])
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 20_000
    with open(doc_path, encoding="utf-8") as f:
        doc = json.load(f)
    n = doc["n"]
    hx = dense(doc["checks"]["X"], n)
    hz = dense(doc["checks"]["Z"], n)
    seed = 91000 + rung * 101 + doc["k"]
    d = distance_rand(hx, hz, trials=trials, seed=seed, backend="numpy")
    out = doc_path.replace(".json", f"-rung{rung}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"doc": os.path.basename(doc_path), "trials": trials,
                   "d": int(d), "seed": seed, "fresh": True,
                   "label": f"rerun {rung}"}, f)
    print(f"{os.path.basename(doc_path)} rung{rung}: d<={d} at {trials} trials")


if __name__ == "__main__":
    main()
