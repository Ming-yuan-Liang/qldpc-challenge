"""Quick k-distribution probe: 500 random (a,b) pairs on Aff(F_17), |a|=|b| in
{8,9,10}, record k. Serial, no distance search. Not an experiment record.
"""
import os
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402

from bbga_labels import build_2bga_affine  # noqa: E402
from css import compute_k  # noqa: E402

t0 = time.time()
hist = Counter()
rng = np.random.default_rng(123)
for i in range(500):
    w = int(rng.choice([8, 9, 10]))
    a = sorted(int(x) for x in rng.choice(272, size=w, replace=False))
    b = sorted(int(x) for x in rng.choice(272, size=w, replace=False))
    HX, HZ = build_2bga_affine(17, a, b)
    k = compute_k(HX, HZ)
    hist[int(k)] += 1
print(f"500 draws in {time.time()-t0:.1f}s")
for k in sorted(hist):
    print(f"  k={k:3d}: {hist[k]}")
print("k in [16,22]:", sum(v for k, v in hist.items() if 16 <= k <= 22))
