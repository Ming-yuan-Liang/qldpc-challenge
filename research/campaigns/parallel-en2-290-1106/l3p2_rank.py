"""L3 lane PHASE 2 ranker (CPU-free): rank screened k=12/14 draws by their
400-trial reading and print the deep-read shortlist.

    python l3p2_rank.py [TOP_N]

Reads l3p2_screened.jsonl (one JSON per draw, from screen_corner.py). Only
rows with status "screened" and a d400 reading are ranked; prepass_dropped
rows are tallied. Prints the top N by d400 (ties broken by lower w, then
efficiency, then pool index). Nothing here is a submission.
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    path = os.path.join(_HERE, "l3p2_screened.jsonl")
    rows, dropped = [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("status") == "screened" and r.get("d400") is not None:
                rows.append(r)
            else:
                dropped += 1
    rows.sort(key=lambda r: (-r["d400"], r["w"], -r.get("eff") or 0, r["i"]))
    print(f"screened {len(rows)} draws ({dropped} prepass_dropped); "
          f"top {min(top_n, len(rows))} by d400:")
    for r in rows[:top_n]:
        print(f"  pool_i {r['i']:>7d} k={r['k']:>2d} w={r['w']} "
              f"d400={r['d400']} eff={r.get('eff'):.1f} "
              f"fp={r.get('fp')} board_wl={r.get('board_wl')}")
    if rows:
        import collections
        print("d400 distribution:",
              dict(sorted(collections.Counter(
                  (r['k'], r['d400'] // 10 * 10) for r in rows).items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
