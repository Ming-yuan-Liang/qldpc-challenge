"""Benchmark one q19 affine 2BGA draw to size the screening job.

q19-k14 lane, campaign parallel-q19-k14-1106. Instrument: the kit surrogate
only, numpy backend, default pair_depth=10.
"""
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from bbga_labels import build_2bga_affine
from css import compute_k, verify_css
from prescreen import block_structure
from surrogate import distance_rand, prepare_distance_search
from qldpc_verify import css_fingerprint


def draw_pair(i, base_seed=20261106):
    """Deterministic draw i: |a| = |b| = w in {7,8,9}, exponents uniform in [0,342)."""
    rng = np.random.default_rng(base_seed + i)
    w = int(rng.choice([7, 8, 9]))
    a = sorted(int(x) for x in rng.choice(342, size=w, replace=False))
    b = sorted(int(x) for x in rng.choice(342, size=w, replace=False))
    return w, a, b


def main():
    t0 = time.time()
    w, a, b = draw_pair(0)
    print(f"draw: w={w} a={a} b={b}")
    HX, HZ = build_2bga_affine(19, a, b)
    print(f"build: {time.time()-t0:.1f}s  HX{HX.shape} css={verify_css(HX, HZ)}")
    t1 = time.time()
    k = compute_k(HX, HZ)
    print(f"compute_k={k}: {time.time()-t1:.1f}s")
    t1 = time.time()
    st = block_structure(HX, HZ)
    print(f"connected={st['connected']}: {time.time()-t1:.1f}s")
    t1 = time.time()
    fp = css_fingerprint(HX, HZ)
    print(f"fingerprint={fp}: {time.time()-t1:.1f}s")
    t1 = time.time()
    prep = prepare_distance_search(HX, HZ)
    print(f"prepare (kernel+logical bases): {time.time()-t1:.1f}s")
    t1 = time.time()
    d400 = distance_rand(prepared=prep, trials=400, seed=1234, backend="numpy")
    dt = time.time() - t1
    print(f"400-trial reading d<={d400}: {dt:.1f}s  -> {400/dt:.1f} trials/s")
    est20k = dt / 400 * 20000
    print(f"estimated 20k-trial single call: {est20k/60:.1f} min")


if __name__ == "__main__":
    main()
