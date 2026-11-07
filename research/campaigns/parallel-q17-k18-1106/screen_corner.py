"""Lane q17-k18, stage B: prepass + 400-trial RIS screen of the k=16-22
corner draws from the pool JSONL.

Per-draw stats land in a JSONL (one line per corner draw: prepass status,
fingerprint, board WL flag, 400-trial reading, efficiency). The authoritative
screen is research/kit/search.screen (the kit's own prepass: CSS, k filter,
within-batch fingerprint dedup, connectivity, board exact/WL dedup, then the
400-trial numpy RIS reading behind it).

    uv run --no-sync python research/campaigns/parallel-q17-k18-1106/screen_corner.py \
        --pool research/campaigns/parallel-q17-k18-1106/pool_draws.jsonl \
        --out research/campaigns/parallel-q17-k18-1106/screened_draws.jsonl \
        --workers 8 --trials 400 --limit 250
"""
import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np  # noqa: E402

from group_algebra import build_2bga, metacyclic  # noqa: E402
from search import PREPASS_COUNTS, screen  # noqa: E402

Q, K_ORDER = 17, 16
N_GROUP = Q * K_ORDER


def build(a, b):
    mul = metacyclic(Q, K_ORDER, 3)[0]
    return build_2bga(mul, a, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--min-k", type=int, default=16)
    ap.add_argument("--max-k", type=int, default=22)
    ap.add_argument("--limit", type=int, default=250,
                    help="screen at most this many corner draws (by pool index)")
    ap.add_argument("--start", type=int, default=0,
                    help="slice [start, stop) of the corner list (chunked runs)")
    ap.add_argument("--stop", type=int, default=None)
    ap.add_argument("--append", action="store_true",
                    help="append to --out instead of overwriting")
    ap.add_argument("--order", choices=("index", "kdesc"), default="index",
                    help="kdesc: within the [start:stop] slice, screen higher k first")
    ap.add_argument("--skip-screened", action="store_true",
                    help="exclude pool_i already present in --out")
    args = ap.parse_args()

    corner = []
    seen_ab = set()
    with open(args.pool, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if not (args.min_k <= rec["k"] <= args.max_k):
                continue
            key = (tuple(rec["a"]), tuple(rec["b"]))
            if key in seen_ab:
                continue
            seen_ab.add(key)
            corner.append(rec)
    corner.sort(key=lambda r: r["i"])
    corner = corner[:args.limit]
    if args.skip_screened and os.path.exists(args.out):
        done_i = set()
        with open(args.out, encoding="utf-8") as f:
            for line in f:
                try:
                    done_i.add(json.loads(line)["i"])
                except (ValueError, KeyError):
                    continue
        before = len(corner)
        corner = [r for r in corner if r["i"] not in done_i]
        print(f"skipping {before - len(corner)} already-screened draws",
              flush=True)
    lo, hi = args.start, args.stop if args.stop is not None else len(corner)
    chunk = corner[lo:hi]
    if args.order == "kdesc":
        chunk = sorted(chunk, key=lambda r: (-r["k"], r["i"]))
    print(f"corner draws (k in [{args.min_k},{args.max_k}]): {len(corner)}; "
          f"chunk [{lo}:{hi}] = {len(chunk)} ({args.order} order)", flush=True)
    if not corner:
        print("nothing to screen")
        return

    cands = []
    for rec in chunk:
        HX, HZ = build(rec["a"], rec["b"])
        spec = {"family": "2bga-affine", "q": Q, "a": rec["a"], "b": rec["b"],
                "w": rec["w"], "pool_i": rec["i"]}
        cands.append((spec, HX, HZ))

    tally = {}
    t0 = time.time()
    recs = screen(cands, min_k=args.min_k, min_d=4, trials=args.trials,
                  seed=0, index=None, workers=args.workers, audit=tally,
                  batch=32)
    print(f"screen done in {time.time()-t0:.0f}s; audit "
          f"{ {k: tally.get(k) for k in PREPASS_COUNTS} }", flush=True)

    by_spec = {}
    for r in recs:
        s = r["spec"]
        by_spec[(tuple(s["a"]), tuple(s["b"]), s["pool_i"])] = r

    n_read = 0
    mode = "a" if args.append else "w"
    with open(args.out, mode, encoding="utf-8", newline="\n") as f:
        for rec in chunk:
            key = (tuple(rec["a"]), tuple(rec["b"]), rec["i"])
            r = by_spec.get(key)
            out = {"i": rec["i"], "w": rec["w"], "a": rec["a"], "b": rec["b"],
                   "k": rec["k"]}
            if r is None:
                out["status"] = "prepass_dropped"
                out["d400"] = None
                out["eff"] = None
            else:
                out["status"] = "screened"
                out["d400"] = int(r["d"])
                out["eff"] = float(r["efficiency"])
                out["fp"] = r["fingerprint"]
                out["board_wl"] = r.get("board_wl")
                n_read += 1
            f.write(json.dumps(out) + "\n")
    print(f"screened readings: {n_read}/{len(chunk)} -> {args.out}")
    best = sorted((r for r in recs), key=lambda r: -r["efficiency"])[:12]
    for r in best:
        s = r["spec"]
        print(f"  [[{r['n']},{r['k']},{r['d']}]] eff={r['efficiency']:.2f} "
              f"w={s['w']} pool_i={s['pool_i']}")


if __name__ == "__main__":
    main()
