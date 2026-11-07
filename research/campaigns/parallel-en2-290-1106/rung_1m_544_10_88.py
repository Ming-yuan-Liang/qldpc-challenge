"""One deep fresh-seed rung for the staged [[544,10,88]], split into chunks.

promote.py reuses a staged witness only above 1,000,000 trials/side on a
fresh seed (DEFAULT_MIN_DEEP_TRIALS). This driver runs that rung as 4,000-
trial chunks with derived chunk seeds (rung seed + c*1,000,003), the same
decomposition the en2-290 lane used, sharded across independent worker
processes. Every chunk's reading is flushed to a JSONL progress file, so a
killed worker loses at most its current chunk.

If any chunk reads lighter than the claimed 88, the witness support is
written to <out>.witness-<weight>.json immediately -- never lose a witness.

Usage (one worker): python rung_1m_544_10_88.py --worker 0 --workers 8 \
    --seed 20261109 --chunks 250 --out progress_1m_w0.jsonl
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kit")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "verify")))

from group_algebra import metacyclic, build_2bga  # noqa: E402
from surrogate import distance_rand_witness  # noqa: E402

CLAIM = 88
Q = 17
R = 3
A = [41, 46, 195, 120, 100, 125]
B = [4, 106, 142, 66, 174, 103]

# Alternative code (684-12-120): --code 684 switches Q/R/A/B/CLAIM below.
# winner544 = EN-2 winner [[544,18,84]] (b3 move of the elite; params pinned
# by L3, fingerprint facbfe8f45fba8e2, witnesses validated). inc544 = the
# merged incumbent [[544,18,76]] (CI truth), the paired-depth control.
CODES = {
    "544": {"claim": 88, "q": 17, "r": 3,
            "a": [41, 46, 195, 120, 100, 125],
            "b": [4, 106, 142, 66, 174, 103]},
    "684": {"claim": 120, "q": 19, "r": 2,
            "a": [149, 150, 286, 301, 322, 329, 341],
            "b": [7, 15, 76, 158, 217, 233, 245]},
    "winner544": {"claim": 84, "q": 17, "r": 3,
                  "a": [245, 84, 96, 270, 163, 268],
                  "b": [245, 252, 47, 59, 143, 70]},
    "inc544": {"claim": 76, "q": 17, "r": 3,
               "a": [245, 84, 96, 270, 163, 268],
               "b": [245, 252, 47, 231, 143, 70]},
    # inc684 = the merged [[684,12,108]] (CI-certified true d = 108): the
    # 684-family matched-depth offset control.
    "inc684": {"claim": 108, "q": 19, "r": 2,
               "a": [60, 67, 97, 154, 336, 191, 104, 227],
               "b": [103, 228, 254, 324, 107, 317, 4, 185]},
    # k20 = the staged [[544,20,87]] (L2's leader, w=20; the live submission).
    "k20": {"claim": 87, "q": 17, "r": 3,
            "a": [21, 38, 57, 60, 186, 196, 209, 217, 219, 251],
            "b": [4, 35, 54, 55, 152, 180, 206, 230, 240, 246]},
}


def main():
    global CLAIM, Q, R, A, B
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, required=True, help="the rung's fresh seed")
    ap.add_argument("--chunks", type=int, default=250)
    ap.add_argument("--chunk-trials", type=int, default=4000)
    ap.add_argument("--pair-depth", type=int, default=10)
    ap.add_argument("--code", choices=sorted(CODES), default="544",
                    help="which staged candidate to run the deep rung on")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    spec = CODES[args.code]
    CLAIM = spec["claim"]
    Q, R, A, B = spec["q"], spec["r"], spec["a"], spec["b"]

    mul, _ = metacyclic(Q, Q - 1, R)
    HX, HZ = build_2bga(mul, A, B)
    HX = np.asarray(HX, dtype=np.uint8) % 2
    HZ = np.asarray(HZ, dtype=np.uint8) % 2

    # The done-set is GLOBAL within one code's rung: every worker reads all
    # progress files for THIS code (both waves), so a restarted/enlarged wave
    # never re-runs a chunk another worker has already flushed.
    here = os.path.dirname(os.path.abspath(args.out)) or "."
    patterns = [os.path.join(here, f"progress_1m_{args.code}_w*.jsonl")]
    if args.code == "544":          # legacy wave-1 files
        patterns += [os.path.join(here, "progress_1m_w*.jsonl"),
                     os.path.join(here, "timing_probe.jsonl")]
    done = set()
    for path in [p for pat in patterns for p in glob.glob(pat)]:
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            done.add(json.loads(line)["chunk"])
                        except (json.JSONDecodeError, KeyError):
                            continue
        except OSError:
            continue

    with open(args.out, "a", encoding="utf-8") as log:
        for c in range(args.chunks):
            if c % args.workers != args.worker or c in done:
                continue
            seed = args.seed + c * 1_000_003
            t0 = time.time()
            res = distance_rand_witness(HX, HZ, args.chunk_trials, seed,
                                        pair_depth=args.pair_depth)
            dt = time.time() - t0
            rec = {"worker": args.worker, "chunk": c, "seed": seed,
                   "trials": args.chunk_trials, "pair_depth": args.pair_depth}
            if res and res.weight is not None:
                rec["d"] = int(res.weight)
                rec["side"] = res.side
                if int(res.weight) < CLAIM:
                    wit = {"chunk": c, "seed": seed, "trials": args.chunk_trials,
                           "side": res.side, "weight": int(res.weight),
                           "support": sorted(int(q) for q in res.support)}
                    wpath = f"{args.out}.witness-{int(res.weight)}-c{c}.json"
                    with open(wpath, "w", encoding="utf-8") as wf:
                        json.dump(wit, wf)
                    rec["witness_file"] = wpath
            else:
                rec["d"] = None
                rec["note"] = "no logical found at this chunk budget"
            rec["seconds"] = round(dt, 1)
            log.write(json.dumps(rec) + "\n")
            log.flush()


if __name__ == "__main__":
    main()
