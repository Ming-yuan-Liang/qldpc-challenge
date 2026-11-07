"""One-off timing probe for the q17 lane: build one affine 2BGA, measure
compute_k and a 400-trial numpy RIS reading. Not an experiment record.
"""
import os
import sys
import time

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
from surrogate import distance_rand, prepare_distance_search  # noqa: E402

rng = np.random.default_rng(0)
a = sorted(int(x) for x in rng.choice(272, size=8, replace=False))
b = sorted(int(x) for x in rng.choice(272, size=8, replace=False))

t0 = time.time()
HX, HZ = build_2bga_affine(17, a, b)
t1 = time.time()
k = compute_k(HX, HZ)
t2 = time.time()
print(f"build: {t1-t0:.2f}s  compute_k: {t2-t1:.2f}s  k={k}", flush=True)

prep = prepare_distance_search(HX, HZ)
t3 = time.time()
print(f"prepare: {t3-t2:.2f}s", flush=True)

t4 = time.time()
d = distance_rand(prepared=prep, trials=400, seed=1)
t5 = time.time()
print(f"400-trial reading: {t5-t4:.1f}s  d<={d}", flush=True)

t6 = time.time()
d2 = distance_rand(prepared=prep, trials=50, seed=2)
t7 = time.time()
print(f"50-trial reading: {t7-t6:.1f}s  d<={d2}  (per-trial ~{(t7-t6)/50*1000:.0f} ms)", flush=True)
