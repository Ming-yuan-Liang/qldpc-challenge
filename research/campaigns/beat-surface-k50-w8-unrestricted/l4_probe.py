"""Probe: sampler reach + instrument speed for the L4 lane. One-off."""
import os
import sys
import time

import numpy as np

KIT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge\research\kit"
sys.path.insert(0, KIT)

from search import sample_cyclic_gb, sample_bb  # noqa: E402
from surrogate import distance_rand, prepare_distance_search  # noqa: E402
from css import compute_k  # noqa: E402

t0 = time.time()
got = []
for spec, HX, HZ in sample_cyclic_gb(6, m_range=(150, 500), weight=(4, 4),
                                     k_band=(45, 55), seed=7):
    got.append((spec, HX, HZ, time.time() - t0))
    if len(got) >= 4:
        break
for spec, HX, HZ, dt in got:
    k = compute_k(HX, HZ)
    w = int(max(HX.sum(1).max(), HZ.sum(1).max()))
    print(f"spec m={spec['m']} designed k={spec['k']} computed k={k} w={w} "
          f"n={HX.shape[1]} build_dt={dt:.1f}s sum={time.time()-t0:.1f}s")

if got:
    spec, HX, HZ, _ = got[0]
    t = time.time()
    prep = prepare_distance_search(HX, HZ)
    print(f"prepare (kernel bases both sides): {time.time()-t:.1f}s "
          f"n={HX.shape[1]}")
    for trials in (50, 200):
        t = time.time()
        d = distance_rand(HX, HZ, trials=trials, seed=11, prepared=prep)
        dt = time.time() - t
        print(f"distance_rand trials={trials}: d_ub={d} dt={dt:.1f}s "
              f"({1000*dt/trials:.1f} ms/trial)")

    # smaller n timing
    t0 = time.time()
    got2 = []
    for spec2, HX2, HZ2 in sample_cyclic_gb(3, m_range=(150, 175),
                                            weight=(4, 4), k_band=(45, 55),
                                            seed=9):
        got2.append((spec2, HX2, HZ2))
        if len(got2) >= 2:
            break
    if got2:
        spec2, HX2, HZ2 = got2[0]
        k2 = compute_k(HX2, HZ2)
        w2 = int(max(HX2.sum(1).max(), HZ2.sum(1).max()))
        prep2 = prepare_distance_search(HX2, HZ2)
        t = time.time()
        d2 = distance_rand(HX2, HZ2, trials=100, seed=3, prepared=prep2)
        print(f"small n={HX2.shape[1]} k={k2} w={w2}: 100 trials "
              f"d_ub={d2} dt={time.time()-t:.1f}s")
