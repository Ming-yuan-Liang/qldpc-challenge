"""L5 screening funnel for pair-partition CPM draws.

Stages (fast RIS, both sides per call): 1000 -> 10000 -> 100000 trials with
optimistic dominance margins vs the lane floor; a draw is rejected at the
first stage whose reading < floor + margin (sound: readings are upper bounds
and only drop with deeper trials). Survivors go to the deep queue.

Ledger is checkpointed after every draw (kill-wave safe, resumable by index).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
sys.path.insert(0, os.path.join(ROOT, "research", "campaigns",
                                "beat-surface-k50-w8-unrestricted"))

from l5_pp import TEMPLATES, draw_solution, quick_eval  # noqa: E402
from surrogate import distance_rand_witness  # noqa: E402
from l4_board import Board  # noqa: E402

BOARD = Board(os.path.join(HERE, "l5_board_cache.json"))

# dominance floors for w=8, k 95-105 (from l5_scan against board 7ea802a1f)
def floor_for(n, k, w=8):
    dom, _ = BOARD.verdict(n, k, 10**6, w)   # dominated only if entry d >= huge
    # verdict with d=10^6: every entry with n<=n, k>=k, w<=w "dominates";
    # the floor is max(entry d) + 1 over that set
    best = -1
    for (en, ek, ed, ew, name) in BOARD.entries:
        if ew <= w and ek >= k and en <= n and ed > best:
            best = ed
    return best + 1


def clean_draw(tpl, N, rng, cap=300):
    """Draw until 4-cycle-free, k in band, css; return (SX, SZ, info, attempts)."""
    for a in range(cap):
        SX, SZ = draw_solution(tpl, N, rng)
        HX, HZ, info = quick_eval(tpl, SX, SZ, N)
        if info["css"] and info["c4"] == (0, 0) and 95 <= info["k"] <= 105:
            return SX, SZ, HX, HZ, info, a + 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--batch", type=int, default=100)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--stages", default="1000,10000,100000")
    ap.add_argument("--margins", default="7,4,2")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--pair-depth", type=int, default=10)
    ap.add_argument("--ledger", default=None)
    args = ap.parse_args()

    tpl = TEMPLATES[args.template]
    n = tpl["L"] * args.N
    stages = [int(s) for s in args.stages.split(",")]
    margins = [int(m) for m in args.margins.split(",")]
    ledger_path = args.ledger or os.path.join(
        HERE, f"ledger_pp_{args.template}_{args.N}_{args.seed}.json")
    rng = np.random.default_rng(args.seed)

    # warm the solver cache once (Fractions RREF is the slow first step)
    from l5_pp import solve_system, _index_map
    solve_system(tpl)
    _index_map(tpl)

    floor = floor_for(n, 2 * args.N)
    print(f"template={args.template} N={args.N} n={n} k=2N={2*args.N} "
          f"floor={floor} ledger={os.path.basename(ledger_path)}", flush=True)

    ledger = {"template": args.template, "N": args.N, "n": n, "k": 2 * args.N,
              "floor": floor, "seed": args.seed, "stages": stages,
              "margins": margins, "pair_depth": args.pair_depth,
              "backend": "fast", "draws": {}}
    if os.path.exists(ledger_path):
        with open(ledger_path, encoding="utf-8") as f:
            old = json.load(f)
        if old.get("template") == args.template and old.get("N") == args.N:
            ledger = old
            print(f"resuming ledger with {len(ledger['draws'])} draws",
                  flush=True)
        rng = np.random.default_rng(args.seed + 1_000_000 * len(ledger["draws"]))

    t_start = time.time()
    done = len(ledger["draws"])
    for di in range(done, args.batch):
        got = clean_draw(tpl, args.N, rng)
        if got is None:
            rec = {"verdict": "no_clean_draw"}
            ledger["draws"][str(di)] = rec
            with open(ledger_path, "w", encoding="utf-8") as f:
                json.dump(ledger, f)
            continue
        SX, SZ, HX, HZ, info, att = got
        rec = {"attempts": att, "k": info["k"], "c4": info["c4"],
               "SX": SX, "SZ": SZ, "stages": [], "best": None}
        verdict = "rejected"
        for si, (trials, margin) in enumerate(zip(stages, margins)):
            t0 = time.time()
            wit = distance_rand_witness(HX, HZ, trials=trials,
                                        seed=args.seed + 977 * (di + 1) + si,
                                        backend="fast", threads=args.threads,
                                        pair_depth=args.pair_depth)
            dt = time.time() - t0
            wt = int(wit.weight) if wit else 10**6
            rec["stages"].append({"trials": trials, "weight": wt,
                                  "side": wit.side if wit else "",
                                  "support": list(wit.support) if wit and wt <= floor else [],
                                  "sec": round(dt, 2)})
            if rec["best"] is None or wt < rec["best"]:
                rec["best"] = wt
            if wt <= floor + margin - 1:
                verdict = f"rejected@stage{si}"
                break
            verdict = "promising" if si == len(stages) - 1 else "alive"
        rec["verdict"] = verdict
        ledger["draws"][str(di)] = rec
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f)
        print(f"draw {di}: att={att} k={info['k']} best={rec['best']} "
              f"{verdict} ({time.time()-t_start:.0f}s)", flush=True)

    best = {k: v["best"] for k, v in ledger["draws"].items()
            if isinstance(v.get("best"), int)}
    prom = [k for k, v in ledger["draws"].items() if v.get("verdict") == "promising"]
    print(f"\nbatch done: {len(ledger['draws'])} draws, "
          f"promising: {prom}, top readings: "
          f"{sorted(best.items(), key=lambda kv: kv[1])[:8]}")


if __name__ == "__main__":
    main()
