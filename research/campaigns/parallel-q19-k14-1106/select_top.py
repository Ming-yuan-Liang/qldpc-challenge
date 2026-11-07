"""Merge screening chunks, kill cross-chunk duplicates, select the top draws.

Selection: k in [12,16], connected, unique fingerprint (first draw index wins),
ranked by screen reading d ascending, tie-break efficiency descending.
Writes select.json and prints the summary.

Usage: python select_top.py <top_n>
"""
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    recs = []
    for p in glob.glob(os.path.join(_HERE, "screen_*.jsonl")):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
    by_i = {}
    for r in recs:
        by_i[r["i"]] = r  # later chunks rewrite nothing: same i, same draw
    seen_fp = {}
    merged = []
    stats = {"total": len(recs), "k_out": 0, "disconnected": 0,
             "dup_in_chunk": 0, "dup_cross_chunk": 0, "error": 0, "read": 0,
             "no_logical_found": 0}
    for i in sorted(by_i):
        r = dict(by_i[i])
        s = r.get("status", "")
        if s == "k_out":
            stats["k_out"] += 1
        elif s == "disconnected":
            stats["disconnected"] += 1
        elif s == "dup_in_chunk":
            stats["dup_in_chunk"] += 1
        elif s.startswith("error"):
            stats["error"] += 1
        elif s == "read":
            fp = r["fp"]
            if fp in seen_fp:
                r["status"] = "dup_cross_chunk"
                stats["dup_cross_chunk"] += 1
            else:
                seen_fp[fp] = i
                stats["read"] += 1
        elif s == "no_logical_found":
            stats["no_logical_found"] += 1
        merged.append(r)

    reads = [r for r in merged if r.get("status") == "read"]
    reads.sort(key=lambda r: (r["d_screen"], -r.get("efficiency", 0)))
    top = reads[:top_n]
    out = {"stats": stats, "n_read_unique": len(reads),
           "top": top,
           "all_reads": [{"i": r["i"], "k": r["k"], "w": r["w"],
                          "d_screen": r["d_screen"],
                          "efficiency": r.get("efficiency"),
                          "fp": r["fp"]} for r in reads]}
    with open(os.path.join(_HERE, "select.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(stats))
    print(f"unique read draws: {len(reads)}")
    for r in top:
        print(f"  draw {r['i']}: w={r['w']} k={r['k']} "
              f"d_screen<={r['d_screen']} ({r['side']}) "
              f"eff={r.get('efficiency')} fp={r['fp']}")


if __name__ == "__main__":
    main()
