"""Deep re-read for the RESUME lane's NEW-stream draws (l1_screen.py stream).

Identical protocol and chunking to deep_unit.py (8 sub-chunks per side,
20,000 trials/side per rung, spawned sub-seeds, JSONL checkpointing with
resume), but the draw comes from ``l1_screen.draw_pair`` (base seed 20261107,
w in {6,7,8}) instead of ``bench_one.draw_pair`` (base 20261106, w in
{7,8,9}). New-stream draw indices are recorded as ``i`` with ``stream:
"l1-20261107"`` so the two streams never mix inside one JSONL.

Usage: python l1_deep_unit.py <stream_draw_index> <seed> <trials_per_side> <out.jsonl>
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, _HERE)  # l1_screen.draw_pair

for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from l1_screen import draw_pair
from bbga_labels import build_2bga_affine
from surrogate import lightest_logical, validate_logical

N_CHUNKS = 8
STREAM = "l1-20261107"


def append(out_path, rec):
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def load_progress(out_path, i, seed):
    done, best, have_final = set(), {"X": (None, None), "Z": (None, None)}, False
    if not os.path.exists(out_path):
        return done, best, have_final
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("stream") != STREAM or r.get("i") != i or r.get("seed") != seed:
                continue
            if r.get("status") == "final":
                have_final = True
                continue
            if r.get("status") == "start" or "chunk" not in r:
                continue
            if "kept" in r:
                continue
            if r.get("w") is None or not r.get("valid"):
                continue
            key = (r["side"], r["chunk"])
            if key in done:
                continue
            done.add(key)
            if "wit" in r and (best[r["side"]][0] is None
                               or r["w"] < best[r["side"]][0]):
                best[r["side"]] = (int(r["w"]), [int(q) for q in r["wit"]])
    return done, best, have_final


def main():
    i, seed, trials, out_path = (int(sys.argv[1]), int(sys.argv[2]),
                                 int(sys.argv[3]), sys.argv[4])
    chunk_trials = trials // N_CHUNKS
    done, best, have_final = load_progress(out_path, i, seed)
    if have_final:
        print(f"stream {STREAM} draw {i} seed {seed}: final present; skip",
              flush=True)
        return
    t0 = time.time()
    w, a, b = draw_pair(i)
    if not done:
        append(out_path, {"stream": STREAM, "i": i, "seed": seed,
                          "trials": trials, "status": "start", "w": w})
    else:
        print(f"stream {STREAM} draw {i} seed {seed}: resuming "
              f"{len(done)}/16 chunks", flush=True)

    HX, HZ = build_2bga_affine(19, a, b)
    x_seed, z_seed = np.random.SeedSequence(int(seed)).spawn(2)
    for side, Hself, Hopp, sseed in (("X", HX, HZ, x_seed),
                                     ("Z", HZ, HX, z_seed)):
        sub_seeds = sseed.spawn(N_CHUNKS)
        for c, sub in enumerate(sub_seeds):
            if (side, c) in done:
                continue
            tc = time.time()
            wgt, sup = lightest_logical(Hself, Hopp, trials=chunk_trials,
                                        seed=sub)
            ok, why = (True, "ok")
            if sup:
                ok, why = validate_logical(HX, HZ, side, wgt, sup)
            rec = {"stream": STREAM, "i": i, "seed": seed, "side": side,
                   "chunk": c, "trials": chunk_trials,
                   "w": int(wgt) if sup else None,
                   "valid": bool(ok), "why": why,
                   "secs": round(time.time() - tc, 1)}
            if sup and ok and (best[side][0] is None or wgt < best[side][0]):
                best[side] = (int(wgt), [int(q) for q in sup])
                rec["wit"] = [int(q) for q in sup]
            append(out_path, rec)
    wx, xwit = best["X"] if best["X"][0] is not None else (trials + 1, [])
    wz, zwit = best["Z"] if best["Z"][0] is not None else (trials + 1, [])
    final = {"stream": STREAM, "i": i, "seed": seed, "trials": trials,
             "status": "final", "w": w, "a": a, "b": b,
             "wx": wx, "wz": wz,
             "reading": int(min(wx, wz)),
             "side": ("X" if wx <= wz else "Z"),
             "xwit": xwit, "zwit": zwit,
             "n_chunks": N_CHUNKS,
             "secs_total": round(time.time() - t0, 1)}
    append(out_path, final)
    print(f"stream {STREAM} draw {i} seed {seed}: X<={wx} Z<={wz} "
          f"reading<={final['reading']} ({final['secs_total']}s incl. resume)",
          flush=True)


if __name__ == "__main__":
    main()
