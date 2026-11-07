"""Lane q17-k18, stage C v2: resumable deep RIS readings, sub-chunked.

One RUNG = one fresh seed at `--trials` trials per side. Each rung-side is
executed as `--n-sub` sub-searches of `--trials/n-sub` trials each with
decorrelated seeds (rung_seed*1000 + j), via
research/kit/surrogate.lightest_logical, pair_depth 10 -- the same numpy
instrument as the screen and the note's ladder; the rung's weight is the
lightest sub-search result and its witness the support that set it. The total
budget per rung per side is unchanged (20,000 trials); the sub-chunking only
makes each unit small enough to checkpoint, so a killed background driver
loses at most the sub-searches in flight. Every sub-witness is written to the
JSONL -- never dropped. Resume: (i, side, rung_seed, sub_idx) already in the
JSONL is skipped.

    uv run --no-sync python research/campaigns/parallel-q17-k18-1106/deep_read2.py \
        --draws research/campaigns/parallel-q17-k18-1106/top_draws.json \
        --out research/campaigns/parallel-q17-k18-1106/deep_subjobs.jsonl \
        --workers 14 --trials 20000 --n-sub 4 \
        --seeds 911001 911002 911003
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
    """One sub-search: (i, a, b, side, rung_seed, sub_idx, sub_trials)."""
    HX, HZ = build_2bga(table(), rec["a"], rec["b"])
    sub_seed = rec["rung_seed"] * 1000 + rec["sub_idx"]
    t0 = time.time()
    if rec["side"] == "X":
        w, sup = lightest_logical(HX, HZ, trials=rec["sub_trials"], seed=sub_seed)
    else:
        w, sup = lightest_logical(HZ, HX, trials=rec["sub_trials"], seed=sub_seed)
    out = {"i": rec["i"], "side": rec["side"], "rung_seed": rec["rung_seed"],
           "sub_idx": rec["sub_idx"], "sub_trials": rec["sub_trials"],
           "seconds": round(time.time() - t0, 1)}
    if w == float("inf") or not sup:
        out["weight"] = None
        out["support"] = []
        out["valid"] = False
        out["note"] = "no logical found"
        return out
    ok, why = validate_logical(HX, HZ, rec["side"], w, sup)
    out["weight"] = int(w)
    out["support"] = sorted(int(q) for q in sup)
    out["valid"] = bool(ok)
    out["note"] = why
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--n-sub", type=int, default=4)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    args = ap.parse_args()

    with open(args.draws, encoding="utf-8") as f:
        draws = json.load(f)

    n_sub = args.n_sub
    sub_trials = args.trials // n_sub
    assert sub_trials * n_sub == args.trials

    done = set()
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add((r["i"], r["side"], r["rung_seed"], r["sub_idx"]))
                except (ValueError, KeyError):
                    continue

    jobs = []
    for seed in args.seeds:            # seed-major: rung 1 completes first
        for d in draws:
            for side in ("X", "Z"):
                for sub in range(n_sub):
                    if (d["i"], side, seed, sub) in done:
                        continue
                    jobs.append({"i": d["i"], "a": d["a"], "b": d["b"],
                                 "side": side, "rung_seed": int(seed),
                                 "sub_idx": sub, "sub_trials": sub_trials})
    total = len(draws) * len(args.seeds) * 2 * n_sub
    print(f"{len(draws)} draws x {len(args.seeds)} rungs x 2 sides x {n_sub} "
          f"sub-searches: {total} total, {len(jobs)} to run "
          f"({sub_trials} trials each)", flush=True)
    if not jobs:
        print("all sub-searches already done")
        return

    meta = {d["i"]: d for d in draws}
    t0 = time.time()
    done_n = 0
    with open(args.out, "a", encoding="utf-8", newline="\n") as f:
        if args.workers > 1:
            import multiprocessing as mp
            ctx = mp.get_context("spawn")
            with ctx.Pool(args.workers) as pool:
                for out in pool.imap_unordered(job, jobs):
                    d = meta[out["i"]]
                    out["a"], out["b"], out["k"] = d["a"], d["b"], d["k"]
                    f.write(json.dumps(out) + "\n")
                    f.flush()
                    done_n += 1
                    print(f"  [{done_n}/{len(jobs)}] i={out['i']} "
                          f"seed={out['rung_seed']} {out['side']}#{out['sub_idx']} "
                          f"w={out['weight']} ({out['seconds']}s "
                          f"valid={out['valid']})", flush=True)
        else:
            for j in jobs:
                out = job(j)
                out["a"], out["b"], out["k"] = j["a"], j["b"], meta[j["i"]]["k"]
                f.write(json.dumps(out) + "\n")
                f.flush()
                done_n += 1
                print(f"  [{done_n}/{len(jobs)}] i={out['i']} "
                      f"seed={out['rung_seed']} {out['side']}#{out['sub_idx']} "
                      f"w={out['weight']} ({out['seconds']}s "
                      f"valid={out['valid']})", flush=True)
    print(f"done: {done_n} sub-searches in {(time.time()-t0)/60:.1f} min "
          f"-> {args.out}")


if __name__ == "__main__":
    main()
