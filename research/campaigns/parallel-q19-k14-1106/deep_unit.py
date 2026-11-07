"""q19-k14 lane deep re-read: kill-resistant, resumable chunked form.

One draw x one fresh seed = one rung: 20,000 trials per side. The side's
budget is split into N_CHUNKS sub-chunks on independently spawned sub-seeds
(SeedSequence(seed).spawn -> per side -> spawn(N_CHUNKS)), so the reading is
20,000 trials/side of the same per-trial distribution as the unsplit stream.
Every chunk result (weight AND witness support) is appended to the JSONL as
soon as it is done, and a restarted unit RESUMES from the recorded chunks:
completed (side, chunk) pairs are skipped, their weights/supports restored.
A kill therefore loses at most one chunk and a relaunch never repeats work.

Instrument unchanged: ``surrogate.lightest_logical`` (numpy, pair_depth=10
default). Every chunk proposal is re-validated with the kit's
``surrogate.validate_logical`` before it is recorded or resumed.

Usage: python deep_unit.py <draw_index> <seed> <trials_per_side> <out.jsonl>
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, _HERE)  # bench_one.draw_pair

for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from bench_one import draw_pair
from bbga_labels import build_2bga_affine
from surrogate import lightest_logical, validate_logical

N_CHUNKS = 8


def append(out_path, rec):
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def load_progress(out_path, i, seed, chunk_trials):
    """Resume state from recorded chunks of this (i, seed): done set + best."""
    done, best, have_final = set(), {"X": (None, None), "Z": (None, None)}, False
    if not os.path.exists(out_path):
        return done, best, have_final
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("i") != i or r.get("seed") != seed:
                continue
            if r.get("status") == "final":
                have_final = True
                continue
            if r.get("status") == "start" or "chunk" not in r:
                continue
            if "kept" in r:
                # pre-resume format: weight without a persisted support;
                # ignore entirely so the chunk is re-run (deterministic per
                # sub-seed) and the witness is recovered exactly
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
    done, best, have_final = load_progress(out_path, i, seed, chunk_trials)
    if have_final:
        print(f"draw {i} seed {seed}: final already present; skip", flush=True)
        return
    t0 = time.time()
    w, a, b = draw_pair(i)
    if not done:
        append(out_path, {"i": i, "seed": seed, "trials": trials,
                          "status": "start", "w": w})
    else:
        print(f"draw {i} seed {seed}: resuming with {len(done)}/16 chunks done",
              flush=True)

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
            rec = {"i": i, "seed": seed, "side": side, "chunk": c,
                   "trials": chunk_trials,
                   "w": int(wgt) if sup else None,
                   "valid": bool(ok), "why": why,
                   "secs": round(time.time() - tc, 1)}
            if sup and ok and (best[side][0] is None or wgt < best[side][0]):
                best[side] = (int(wgt), [int(q) for q in sup])
                rec["wit"] = [int(q) for q in sup]
            append(out_path, rec)
    wx, xwit = best["X"] if best["X"][0] is not None else (trials + 1, [])
    wz, zwit = best["Z"] if best["Z"][0] is not None else (trials + 1, [])
    final = {"i": i, "seed": seed, "trials": trials, "status": "final",
             "w": w, "a": a, "b": b,
             "wx": wx, "wz": wz,
             "reading": int(min(wx, wz)),
             "side": ("X" if wx <= wz else "Z"),
             "xwit": xwit, "zwit": zwit,
             "n_chunks": N_CHUNKS,
             "secs_total": round(time.time() - t0, 1)}
    append(out_path, final)
    print(f"draw {i} seed {seed}: X<={wx} Z<={wz} reading<={final['reading']} "
          f"({final['secs_total']}s incl. resume)", flush=True)


if __name__ == "__main__":
    main()
