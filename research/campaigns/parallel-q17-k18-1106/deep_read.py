"""Lane q17-k18, stage C: fresh-seed deep RIS readings of the top draws.

Each rung = one fresh seed x `--trials` trials per side, one side per job
(research/kit/surrogate.lightest_logical, the same numpy instrument the screen
uses, pair_depth default 10). Both sides are read so each rung yields the
per-side witnesses a submission needs; every witness found is written to the
JSONL -- never dropped.

    uv run --no-sync python research/campaigns/parallel-q17-k18-1106/deep_read.py \
        --draws research/campaigns/parallel-q17-k18-1106/top_draws.json \
        --out research/campaigns/parallel-q17-k18-1106/deep_rungs.jsonl \
        --workers 10 --trials 20000 --seeds 2026110601 2026110602 2026110603
"""
import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from group_algebra import build_2bga, metacyclic  # noqa: E402
from surrogate import lightest_logical, validate_logical  # noqa: E402

Q, K_ORDER = 17, 16
_TABLE = None


def table():
    global _TABLE
    if _TABLE is None:
        _TABLE = metacyclic(Q, K_ORDER, 3)[0]
    return _TABLE


def job(rec):
    """One side of one rung: (i, a, b, side, trials, seed) -> JSONL record."""
    i, a, b, side, trials, seed = (rec["i"], rec["a"], rec["b"], rec["side"],
                                   rec["trials"], rec["seed"])
    HX, HZ = build_2bga(table(), a, b)
    t0 = time.time()
    if side == "X":
        w, sup = lightest_logical(HX, HZ, trials=trials, seed=seed)
    else:
        w, sup = lightest_logical(HZ, HX, trials=trials, seed=seed)
    out = {"i": i, "seed": seed, "side": side, "trials": trials,
           "seconds": round(time.time() - t0, 1)}
    if w == float("inf") or not sup:
        out["weight"] = None
        out["support"] = []
        out["valid"] = False
        out["note"] = "no logical found"
        return out
    ok, why = validate_logical(HX, HZ, side, w, sup)
    out["weight"] = int(w)
    out["support"] = sorted(int(q) for q in sup)
    out["valid"] = bool(ok)
    out["note"] = why
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", required=True,
                    help="JSON file: list of draws with i, a, b, k, w")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--append", action="store_true")
    args = ap.parse_args()

    with open(args.draws, encoding="utf-8") as f:
        draws = json.load(f)

    jobs = []
    for d in draws:
        for seed in args.seeds:
            for side in ("X", "Z"):
                jobs.append({"i": d["i"], "a": d["a"], "b": d["b"], "k": d["k"],
                             "side": side, "trials": args.trials,
                             "seed": int(seed)})
    print(f"{len(draws)} draws x {len(args.seeds)} seeds x 2 sides = "
          f"{len(jobs)} rung-jobs at {args.trials} trials", flush=True)

    mode = "a" if args.append else "w"
    done = 0
    t0 = time.time()
    with open(args.out, mode, encoding="utf-8", newline="\n") as f:
        if args.workers > 1:
            import multiprocessing as mp
            ctx = mp.get_context("spawn")
            with ctx.Pool(args.workers) as pool:
                for out in pool.imap_unordered(job, jobs):
                    out["a"] = next(j2["a"] for j2 in jobs if j2["i"] == out["i"])
                    out["b"] = next(j2["b"] for j2 in jobs if j2["i"] == out["i"])
                    f.write(json.dumps(out) + "\n")
                    f.flush()
                    done += 1
                    print(f"  [{done}/{len(jobs)}] i={out['i']} seed={out['seed']} "
                          f"{out['side']} w={out['weight']} "
                          f"({out['seconds']}s, valid={out['valid']})", flush=True)
        else:
            for j in jobs:
                out = job(j)
                out["a"], out["b"] = j["a"], j["b"]
                f.write(json.dumps(out) + "\n")
                f.flush()
                done += 1
                print(f"  [{done}/{len(jobs)}] i={out['i']} seed={out['seed']} "
                      f"{out['side']} w={out['weight']} "
                      f"({out['seconds']}s, valid={out['valid']})", flush=True)
    print(f"done: {done} rungs in {(time.time()-t0)/60:.1f} min -> {args.out}")


if __name__ == "__main__":
    main()
