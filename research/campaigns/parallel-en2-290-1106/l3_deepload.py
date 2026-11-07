"""L3 lane: resumable deep rung on a code whose checks live in a board-style
JSON (no a/b spec needed -- used for the incumbent codes/544-18-76.json).

Same protocol as phase_deep_ckpt.py: TOTAL_TRIALS trials/side spent as CHUNK-
trial checkpoint chunks of surrogate.distance_rand_witness (numpy backend,
default pair_depth), chunk seeds derived as SEED + c*1000003, progress flushed
to <OUTJSON>.progress after every chunk so a killed process resumes. The final
reading is the min across chunks; the lightest chunk's support is preserved.

    python l3_deepload.py ENTRY_JSON TOTAL_TRIALS SEED OUTJSON [CHUNK]

ENTRY_JSON is a submission-shaped JSON with checks.X / checks.Z. Nothing here
is a submission.
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

from css import compute_k, verify_css
from surrogate import distance_rand_witness


def rows_to_dense(rows, n):
    M = np.zeros((len(rows), n), dtype=np.int8)
    for i, row in enumerate(rows):
        for q in row:
            M[i, int(q)] ^= 1
    return M


def main():
    entry = sys.argv[1]
    total = int(sys.argv[2])
    seed = int(sys.argv[3])
    outjson = sys.argv[4].strip().strip('"')
    chunk = int(sys.argv[5]) if len(sys.argv) > 5 else 4000
    if not os.path.isabs(outjson):
        outjson = os.path.join(_HERE, os.path.basename(outjson))
    if not os.path.isabs(entry):
        entry = os.path.join(_ROOT, entry)
    prog_path = outjson + ".progress"

    t0 = time.time()
    with open(entry, encoding="utf-8") as f:
        doc = json.load(f)
    n = int(doc["n"])
    HX = rows_to_dense(doc["checks"]["X"], n)
    HZ = rows_to_dense(doc["checks"]["Z"], n)
    k = compute_k(HX, HZ)
    css_ok = verify_css(HX, HZ)
    wx_rows = int(HX.sum(axis=1).max())
    wz_rows = int(HZ.sum(axis=1).max())
    print(f"seed {seed}: loaded {os.path.basename(entry)} n={n} k={k} "
          f"(doc k={doc.get('k')}) css_ok={css_ok} max_row_weight X={wx_rows} "
          f"Z={wz_rows} claim d<={doc['distance']['d']}", flush=True)
    if not css_ok or k != int(doc["k"]):
        print(f"seed {seed}: ENTRY UNUSABLE (css_ok={css_ok}, k mismatch)",
              flush=True)
        return 3

    prog = {"entry": entry, "n": n, "k": k, "seed": seed,
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

    out = {"entry": entry, "n": n, "k": k, "seed": seed,
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
