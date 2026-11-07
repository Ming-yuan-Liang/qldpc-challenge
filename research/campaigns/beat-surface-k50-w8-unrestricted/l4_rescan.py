"""L4 deep re-scan: rebuild prior top-reading candidates and measure their
true distance with the gf2_fast backend at 500k trials (bias ~ +1-2 vs 8M).

Input: screening ledgers (records carry spec + d200). Filters d200 >= min-d.
Output: rescan ledger with d500k per candidate."""
import argparse
import glob
import json
import os
import sys
import time

KIT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge\research\kit"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
sys.path.insert(0, HERE)

import gf2poly  # noqa: E402
from surrogate import distance_rand_witness  # noqa: E402
from search import fingerprint  # noqa: E402
from css import compute_k  # noqa: E402


def rebuild(spec):
    m, a, b = spec["m"], spec["a"], spec["b"]
    return gf2poly.cyclic_gb(m, a, b)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledgers", nargs="+", required=True)
    ap.add_argument("--min-d200", type=int, default=12)
    ap.add_argument("--trials", type=int, default=500000)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    args = ap.parse_args()

    cands = {}
    for lp in args.ledgers:
        try:
            led = load(lp)
        except (OSError, ValueError):
            continue
        for r in led.get("records", []):
            if (r.get("d200") or 0) >= args.min_d200 and "spec" in r:
                cands[r["fp"]] = r
    fps = sorted(cands)
    fps = [fp for i, fp in enumerate(fps) if i % args.nshards == args.shard]
    print(f"rescan shard {args.shard}/{args.nshards}: {len(fps)} candidates "
          f"at {args.trials} trials (fast, threads={args.threads})", flush=True)

    out_path = os.path.join(HERE, f"rescan_{args.shard}.json")
    out = load(out_path) if os.path.exists(out_path) else {"rescans": {}}
    t0 = time.time()
    for idx, fp in enumerate(fps):
        if fp in out["rescans"]:
            continue
        r = cands[fp]
        HX, HZ = rebuild(r["spec"])
        wit = distance_rand_witness(HX, HZ, trials=args.trials, seed=4444,
                                    backend="fast", threads=args.threads)
        d = int(wit.weight) if wit else 10 ** 9
        out["rescans"][fp] = {"n": r["n"], "k": r["k"], "m": r["spec"]["m"],
                              "d200_numpy": r["d200"], "d500k_fast": d,
                              "side": wit.side if wit else "",
                              "spec": r["spec"]}
        save(out_path, out)
        print(f"  [{idx+1}/{len(fps)}] m={r['spec']['m']} n={r['n']} "
              f"k={r['k']} d200={r['d200']} -> d500k={d} "
              f"({time.time()-t0:.0f}s)", flush=True)
    print("rescan done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
