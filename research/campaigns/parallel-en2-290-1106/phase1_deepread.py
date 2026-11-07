"""PHASE 1 deep read of the EN-2 winner (screen-cache index 290 of
research/campaigns/affine-elite-nbhd-544-18-84): the b3 single-coordinate move
of the [[544,18,84]] q=17 elite, screen reading [[544,18,96]] eff 304.9.

One seed per process. 20,000 trials/side at the lane's default pair_depth=10
(the same instrument the 400-trial screen and the earlier 20k rungs used).

Writes phase1_witness_seed<seed>.json beside this script (witness included:
the lightest logical support is the expensive artifact, never dropped).
Nothing here is a submission.
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

Q = 17
A = [245, 84, 96, 270, 163, 268]
B = [245, 252, 47, 59, 143, 70]   # the b3 move: b[3] 231 -> 59
CLAIM_D = 96                      # screen reading of this spec (400 trials)


def main():
    seed = int(sys.argv[1])
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 20_000
    t0 = time.time()
    HX, HZ = build_2bga_affine(Q, A, B)
    HX = np.asarray(HX, dtype=np.int8) % 2
    HZ = np.asarray(HZ, dtype=np.int8) % 2
    n = HX.shape[1]
    k = compute_k(HX, HZ)
    wx_rows = int(HX.sum(axis=1).max())
    wz_rows = int(HZ.sum(axis=1).max())
    print(f"seed {seed}: built n={n} k={k} max_row_weight X={wx_rows} "
          f"Z={wz_rows} HX{HX.shape} HZ{HZ.shape}", flush=True)

    res = distance_rand_witness(HX, HZ, trials=trials, seed=seed,
                                backend="numpy")
    if not res or res.rejected:
        print(f"seed {seed}: NO LOGICAL ({res.rejected if res else 'empty'})",
              flush=True)
        out = {"seed": seed, "trials": trials, "n": n, "k": k,
               "claimed_d": CLAIM_D, "weight": None, "side": None,
               "support": None, "rejected": res.rejected if res else "empty"}
    else:
        print(f"seed {seed}: reading d<={res.weight} (side {res.side}) "
              f"after {time.time()-t0:.0f}s", flush=True)
        out = {"seed": seed, "trials": trials, "n": n, "k": k,
               "claimed_d": CLAIM_D, "weight": int(res.weight),
               "side": str(res.side), "support": [int(q) for q in res.support],
               "rejected": ""}
    out["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(_HERE, f"phase1_witness_seed{seed}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path}", flush=True)


if __name__ == "__main__":
    main()
