"""Generic deep rung: rebuild a Kasai affine 2BGA candidate from its spec and
run one fresh-seed distance_rand_witness at the given trial depth.

    python phase2_deep.py Q A_COMMA B_COMMA TRIALS SEED OUTPREFIX

Writes <OUTPREFIX>_seed<SEED>.json beside this script with the witness support
(the expensive artifact). Nothing here is a submission.
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
    trials = int(sys.argv[4])
    seed = int(sys.argv[5])
    prefix = sys.argv[6]
    t0 = time.time()
    HX, HZ = build_2bga_affine(q, a, b)
    HX = np.asarray(HX, dtype=np.int8) % 2
    HZ = np.asarray(HZ, dtype=np.int8) % 2
    n = HX.shape[1]
    k = compute_k(HX, HZ)
    res = distance_rand_witness(HX, HZ, trials=trials, seed=seed,
                                backend="numpy")
    out = {"q": q, "a": a, "b": b, "n": n, "k": k, "seed": seed,
           "trials": trials, "wall_s": round(time.time() - t0, 1)}
    if not res or res.rejected:
        out.update({"weight": None, "side": None, "support": None,
                    "rejected": res.rejected if res else "empty"})
        print(f"seed {seed}: NO LOGICAL ({out['rejected']})", flush=True)
    else:
        out.update({"weight": int(res.weight), "side": str(res.side),
                    "support": [int(x) for x in res.support],
                    "rejected": ""})
        print(f"[[{n},{k}]] seed {seed}: d<={res.weight} ({res.side}) "
              f"{time.time()-t0:.0f}s", flush=True)
    path = os.path.join(_HERE, f"{prefix}_seed{seed}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path}", flush=True)


if __name__ == "__main__":
    main()
