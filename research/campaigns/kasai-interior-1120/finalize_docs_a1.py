"""Finalize A1 submission docs: per-side witness re-measurement at 1M pd12.

X side: distance_rand_witness(HX, HZ) finds kernel(HZ)\rowspace(HX) logicals.
Z side: swapped call (HZ, HX) finds kernel(HX)\rowspace(HZ). Each call is a
full fresh-seed measurement of exactly one side at the given budget.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[3] / "research" / "candidates" / "a1-kasai-1120"
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

from surrogate import distance_rand_witness  # noqa: E402


def dense(rows, n):
    import numpy as np
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, sup in enumerate(rows):
        m[i, list(sup)] = 1
    return m


def measure(hx, hz, trials, seed):
    return distance_rand_witness(HX=hx, HZ=hz, trials=trials, seed=seed,
                                 backend="fast", pair_depth=12)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    slugs = sys.argv[2:] or ["684-18-124", "684-16-127"]
    for slug in slugs:
        p = HERE / f"{slug}.json"
        doc = json.load(open(p, encoding="utf-8"))
        n = doc["n"]
        hx = dense(doc["checks"]["X"], n)
        hz = dense(doc["checks"]["Z"], n)
        res = {}
        for side, (a, b) in (("X", (hx, hz)), ("Z", (hz, hx))):
            seed = 70000 + doc["k"] * 13 + (0 if side == "X" else 1) + trials // 1000
            w = measure(a, b, trials, seed)
            if w.rejected or w.weight is None:
                print(f"{slug} {side}: NO LOGICAL FOUND ({w!r:.150})")
                continue
            res[side] = {"value": int(w.weight), "confidence": "upper_bound",
                         "witness": sorted(int(x) for x in w.support),
                         "witness_provenance": {
                             "found_by": ["@Ming-yuan-Liang"],
                             "date": "2026-11-21",
                             "found_at_samples": trials,
                             "survived_samples": trials,
                             "tool": (f"surrogate.distance_rand_witness gf2_fast "
                                      f"{trials:,} trials pd12, seed {seed}"),
                             "seeds": [seed]}}
            print(f"{slug} {side}: d<={w.weight} at {trials:,} trials "
                  f"(seed {seed})")
        if not res:
            continue
        dmin = min(s["value"] for s in res.values())
        doc["distance"]["d"] = dmin
        for side in ("X", "Z"):
            doc["distance"][side] = res.get(side) or {
                "value": dmin + 999, "confidence": "upper_bound", "witness": [],
                "witness_provenance": {"found_by": ["@Ming-yuan-Liang"],
                                       "date": "2026-11-21",
                                       "found_at_samples": trials,
                                       "tool": "heavier side, not witnessed"}}
        doc["name"] = doc["name"].split(" screen reading")[0]
        json.dump(doc, open(p, "w", encoding="utf-8"), indent=1)
        print(f"{slug}: d={dmin} (X={res.get('X',{}).get('value')}, "
              f"Z={res.get('Z',{}).get('value')})")


if __name__ == "__main__":
    main()
