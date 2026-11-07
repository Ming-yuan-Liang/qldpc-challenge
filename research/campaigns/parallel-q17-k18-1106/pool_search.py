"""Lane q17-k18, stage A: uniform random seed-exponent pool on Aff(F_17).

Draws (a, b) with |a| = |b| in {8, 9, 10}, exponents uniform in [0, 272),
records k = 544 - rank(HX) - rank(HZ) for every draw via a bit-packed GF(2)
rank (the gate recomputes k itself on anything staged; this fast rank is only
the screening filter that makes the rare k=16-22 corner reachable at all).

Output: draws JSONL, one line per draw:
  {"i": int, "w": int, "a": [...], "b": [...], "k": int}

    uv run --no-sync python research/campaigns/parallel-q17-k18-1106/pool_search.py \
        --pool 40000 --workers 8 --seed 1106 \
        --out research/campaigns/parallel-q17-k18-1106/pool_draws.jsonl
"""
import argparse
import json
import os
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np  # noqa: E402

Q = 17
K_ORDER = Q - 1               # metacyclic Z_17 x| Z_16
N_GROUP = Q * K_ORDER         # 272
N = 2 * N_GROUP               # 544
PRIMITIVE_ROOT = 3            # smallest primitive root mod 17 (kit's derivation)
WEIGHTS = (8, 9, 10)

_TABLE = None


def _table():
    global _TABLE
    if _TABLE is None:
        from group_algebra import metacyclic
        _TABLE = metacyclic(Q, K_ORDER, PRIMITIVE_ROOT)[0]
    return _TABLE


def pack_bits(M):
    """(rows, cols) 0/1 int8 -> (rows, cols/64) uint64, bit i = column 64w+i."""
    cols = M.shape[1]
    pad = (-cols) % 64
    if pad:
        M = np.concatenate([M, np.zeros((M.shape[0], pad), dtype=np.int8)], axis=1)
    packed = np.packbits(M, axis=1, bitorder="little")
    return np.ascontiguousarray(packed).view(np.uint64)


def rank_bits(rows, ncols):
    """GF(2) rank by forward elimination on the packed rows."""
    M = rows.copy()
    r = 0
    nrows = M.shape[0]
    one = np.uint64(1)
    for col in range(ncols):
        wi, bit = col >> 6, col & 63
        mask = one << np.uint64(bit)
        colbits = (M[r:, wi] & mask) != 0
        if not colbits.any():
            continue
        piv = r + int(np.argmax(colbits))
        if piv != r:
            M[[r, piv]] = M[[piv, r]]
        below = (M[r + 1:, wi] & mask) != 0
        if below.any():
            M[r + 1:][below] ^= M[r]
        r += 1
        if r == nrows:
            break
    return r


def code_k(a, b):
    """k of the 2BGA with seeds a, b, via the packed rank."""
    from group_algebra import build_2bga
    HX, HZ = build_2bga(_table(), a, b)
    return N - rank_bits(pack_bits(HX), N) - rank_bits(pack_bits(HZ), N)


def draw_k(i):
    """One uniform draw; returns the JSONL record."""
    rng = np.random.default_rng((int(SEED), int(i)))
    w = int(rng.choice(WEIGHTS))
    a = sorted(int(x) for x in rng.choice(N_GROUP, size=w, replace=False))
    b = sorted(int(x) for x in rng.choice(N_GROUP, size=w, replace=False))
    return {"i": int(i), "w": w, "a": a, "b": b, "k": int(code_k(a, b))}


SEED = 0


def _init(seed):
    global SEED
    SEED = int(seed)
    _table()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=int, default=40000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1106)
    ap.add_argument("--out", required=True)
    ap.add_argument("--append", action="store_true",
                    help="continue the draw index after the existing file")
    args = ap.parse_args()

    start_i = 0
    if args.append and os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            start_i = sum(1 for _ in f)
    mode = "a" if (args.append and start_i) else "w"

    hist = Counter()
    hist_corner = Counter()
    t0 = time.time()
    with open(args.out, mode, encoding="utf-8", newline="\n") as f:
        if args.workers > 1:
            import multiprocessing as mp
            ctx = mp.get_context("spawn")
            with ctx.Pool(args.workers, initializer=_init,
                          initargs=(args.seed,)) as pool:
                for rec in pool.imap_unordered(draw_k, range(start_i, start_i + args.pool),
                                               chunksize=16):
                    f.write(json.dumps(rec) + "\n")
                    hist[rec["k"]] += 1
                    if 16 <= rec["k"] <= 22:
                        hist_corner[rec["k"]] += 1
        else:
            _init(args.seed)
            for i in range(start_i, start_i + args.pool):
                rec = draw_k(i)
                f.write(json.dumps(rec) + "\n")
                hist[rec["k"]] += 1
                if 16 <= rec["k"] <= 22:
                    hist_corner[rec["k"]] += 1

    dt = time.time() - t0
    print(f"{args.pool} draws in {dt:.0f}s ({args.pool/dt:.0f}/s) -> {args.out}")
    print("k histogram:", dict(sorted(hist.items())))
    print(f"k in [16,22]: {sum(hist_corner.values())} {dict(sorted(hist_corner.items()))}")


if __name__ == "__main__":
    main()
