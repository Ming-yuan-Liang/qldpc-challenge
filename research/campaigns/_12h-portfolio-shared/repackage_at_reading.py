"""Re-measure a staged candidate with the witness-returning search and, if a
lighter logical is found, repackage the document at the reading.

Usage: python repackage_at_reading.py <doc.json> <trials> <seed>

Writes <stem>-repack.json (the corrected doc at the lower reading, with the
new witness) and prints the old/new readings. Refuses to touch the original.
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

from surrogate import distance_rand_witness  # noqa: E402


def dense(rows, n):
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, sup in enumerate(rows):
        m[i, list(sup)] = 1
    return m


def main():
    doc_path, trials, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    with open(doc_path, encoding="utf-8") as f:
        doc = json.load(f)
    n = doc["n"]
    hx = dense(doc["checks"]["X"], n)
    hz = dense(doc["checks"]["Z"], n)
    res = distance_rand_witness(hx, hz, trials=trials, seed=seed,
                                backend="numpy")
    old_d = doc["distance"]["d"]
    if not res:
        print(f"old claim d={old_d}; no lighter logical found; nothing to "
              "repackage")
        return
    new_d = int(res.weight)
    side = res.side
    sup = sorted(int(q) for q in res.support)
    print(f"old claim d={old_d}; re-measured {side}<={new_d} "
          f"(weight {len(sup)})")
    if new_d >= old_d:
        print("found logical not lighter than the claim; nothing to repackage")
        return
    doc["distance"][side] = {"value": new_d, "confidence": "upper_bound",
                             "witness": sup}
    doc["distance"]["d"] = new_d
    doc["name"] = doc["name"].replace(f"[[{n},", f"[[{n},")  # k unchanged
    doc["name"] = f"[[{n},{doc['k']},{new_d}]] " + doc["name"].split("]] ", 1)[1]
    out = doc_path.replace(".json", "-repack.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print(f"repackaged at d={new_d} (side {side}, weight {len(sup)}) -> {out}")


if __name__ == "__main__":
    main()
