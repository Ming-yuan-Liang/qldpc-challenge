"""Resumable deep rung: rebuild a Kasai affine 2BGA candidate and spend
TOTAL_TRIALS trials/side on distance_rand_witness in CHUNK-trial checkpoints.

The environment kills long-running python tasks in waves (two waves observed
2026-11-06, exit 137), so every chunk's result is flushed to
<OUTJSON>.progress before the next chunk starts and a restarted process
resumes from the recorded chunk count. The final reading is the min across
chunks; the witness support of the lightest chunk operator is preserved.

    python phase_deep_ckpt.py Q A_COMMA B_COMMA TOTAL_TRIALS SEED OUTJSON [CHUNK]

Chunk seeds are derived deterministically (SEED + c*1000003) so the rung is
reproducible. Nothing here is a submission.
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from bbga_labels import build_2bga_affine
from css import compute_k
from surrogate import distance_rand_witness


def main():
    q = int(sys.argv[1])
    a = [int(x) for x in sys.argv[2].split(",")]
    b = [int(x) for x in sys.argv[3].split(",")]
    total = int(sys.argv[4])
    seed = int(sys.argv[5])
    outjson = sys.argv[6]
    chunk = int(sys.argv[7]) if len(sys.argv) > 7 else 4000
    outjson = outjson.strip().strip('"')
    if not os.path.isabs(outjson):
        outjson = os.path.join(_HERE, os.path.basename(outjson))
    prog_path = outjson + ".progress"

    t0 = time.time()
    HX, HZ = build_2bga_affine(q, a, b)
    HX = np.asarray(HX, dtype=np.int8) % 2
    HZ = np.asarray(HZ, dtype=np.int8) % 2
    n = HX.shape[1]
    k = compute_k(HX, HZ)

    prog = {"q": q, "a": a, "b": b, "n": n, "k": k, "seed": seed,
            "total_trials": total, "chunk": chunk, "chunks": []}
    if os.path.exists(prog_path):
        with open(prog_path, encoding="utf-8") as f:
            prog = json.load(f)
        print(f"resuming: {len(prog['chunks'])} chunks already done",
              flush=True)

    best = None  # (weight, side, support, chunk_seed)
    for rec in prog["chunks"]:
        if rec["weight"] is not None and (best is None or
                                          rec["weight"] < best[0]):
            best = (rec["weight"], rec["side"], rec["support"], rec["chunk_seed"])

    n_chunks = (total + chunk - 1) // chunk
    while len(prog["chunks"]) < n_chunks:
        c = len(prog["chunks"])
        trials_c = min(chunk, total - c * chunk)
        cseed = seed + c * 1_000_003
        tc0 = time.time()
        res = distance_rand_witness(HX, HZ, trials=trials_c, seed=cseed,
                                    backend="numpy")
        if not res or res.rejected:
            rec = {"chunk": c, "chunk_seed": cseed, "trials": trials_c,
                   "weight": None, "side": None, "support": None,
                   "rejected": res.rejected if res else "empty"}
            print(f"chunk {c}: NO LOGICAL ({rec['rejected']})", flush=True)
        else:
            rec = {"chunk": c, "chunk_seed": cseed, "trials": trials_c,
                   "weight": int(res.weight), "side": str(res.side),
                   "support": [int(x) for x in res.support], "rejected": ""}
            if best is None or rec["weight"] < best[0]:
                best = (rec["weight"], rec["side"], rec["support"], cseed)
            print(f"chunk {c}: d<={rec['weight']} ({rec['side']}) "
                  f"running best {best[0]} [{time.time()-tc0:.0f}s]",
                  flush=True)
        prog["chunks"].append(rec)
        tmp = prog_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(prog, f)
        os.replace(tmp, prog_path)

    out = {"q": q, "a": a, "b": b, "n": n, "k": k, "seed": seed,
           "trials": total, "chunk": chunk,
           "n_chunks": len(prog["chunks"]),
           "wall_s": round(time.time() - t0, 1)}
    if best is None:
        out.update({"weight": None, "side": None, "support": None,
                    "rejected": "no logical in any chunk"})
        print(f"seed {seed}: NO LOGICAL anywhere", flush=True)
    else:
        out.update({"weight": best[0], "side": best[1], "support": best[2],
                    "best_chunk_seed": best[3],
                    "chunk_weights": [c["weight"] for c in prog["chunks"]],
                    "rejected": ""})
        print(f"DONE [[{n},{k}]] seed {seed}: d<={best[0]} ({best[1]}) "
              f"chunks {[c['weight'] for c in prog['chunks']]} "
              f"[{time.time()-t0:.0f}s]", flush=True)
    with open(outjson, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {outjson}", flush=True)


if __name__ == "__main__":
    main()
