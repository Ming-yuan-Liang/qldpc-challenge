"""L3 lane PHASE 2 screener, kill-tolerant: screens the k=12/14 pool ONE DRAW
AT A TIME, appending each result line to the output JSONL immediately (the
lesson from the 2026-11-06 ~12:35 kill wave that cost a whole 110-draw batch:
research/kit search.screen computes an entire batch before its single
end-of-batch write).

    python l3p2_screen_slice.py [MAX_DRAWS] [WORKERS]

Reads l3p2_pool_k1214.jsonl (already sorted w8-first), skips draws already
present in l3p2_screened.jsonl, screens up to MAX_DRAWS new draws with the
kit's own prepass + 400-trial numpy RIS reading (search.screen on
one-draw batches, within-batch fingerprint dedup per draw; the board-dedup
index is skipped for screening economy - the gate re-checks dedup on any
survivor). Each completed draw is flushed as one JSON line, so an external
kill loses at most the draw in flight.

Nothing here is a submission.
"""
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
from prescreen import board_index  # noqa: E402
from search import PREPASS_COUNTS, screen  # noqa: E402

Q, K_ORDER = 17, 16
POOL = os.path.join(_HERE, "l3p2_pool_k1214.jsonl")
OUT = os.path.join(_HERE, "l3p2_screened.jsonl")


def main():
    max_draws = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    done_i = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                try:
                    done_i.add(json.loads(line)["i"])
                except (ValueError, KeyError):
                    continue
    pool = []
    with open(POOL, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["i"] not in done_i:
                pool.append(r)
    print(f"{len(done_i)} draws already screened; {len(pool)} remaining; "
          f"screening up to {max_draws}", flush=True)

    mul = metacyclic(Q, K_ORDER, 3)[0]
    idx = board_index()  # built ONCE: board exact/WL dedup on every draw
    print(f"board index ready", flush=True)
    n_done = 0
    t0 = time.time()
    with open(OUT, "a", encoding="utf-8", newline="\n") as g:
        for rec in pool:
            if n_done >= max_draws:
                break
            HX, HZ = build_2bga(mul, rec["a"], rec["b"])
            spec = {"family": "2bga-affine", "q": Q, "a": rec["a"],
                    "b": rec["b"], "w": rec["w"], "pool_i": rec["i"]}
            tally = {}
            recs = screen([(spec, HX, HZ)], min_k=rec["k"], min_d=4,
                          trials=400, seed=0, index=idx, audit=tally,
                          workers=workers)
            r = recs[0] if recs else None
            out = {"i": rec["i"], "w": rec["w"], "k": rec["k"],
                   "a": rec["a"], "b": rec["b"]}
            if r is None:
                out["status"] = "prepass_dropped"
                out["d400"] = None
                out["eff"] = None
                bad = {k: tally.get(k) for k in PREPASS_COUNTS
                       if tally.get(k)}
                out["prepass"] = bad
            else:
                out["status"] = "screened"
                out["d400"] = int(r["d"])
                out["eff"] = float(r["efficiency"])
                out["fp"] = r.get("fingerprint")
                out["board_wl"] = r.get("board_wl")
            g.write(json.dumps(out) + "\n")
            g.flush()
            os.fsync(g.fileno())
            n_done += 1
            if r is not None:
                print(f"pool_i {rec['i']:>7d} k={rec['k']} w={rec['w']} "
                      f"d400={out['d400']} [{time.time()-t0:.0f}s]",
                      flush=True)
            else:
                print(f"pool_i {rec['i']:>7d} k={rec['k']} w={rec['w']} "
                      f"DROPPED {out.get('prepass')} [{time.time()-t0:.0f}s]",
                      flush=True)
    print(f"done: {n_done} draws this run -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
