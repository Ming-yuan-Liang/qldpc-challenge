"""L5 pair-partition CPM machinery: rebuild the published irregular templates
(6x14 rate-1/7, 5x12 rate-1/6, 4x10 rate-1/5) from their provenance, solve the
paired-difference exponent system at new lifts N, and screen draws.

Equations (per pairing cell (i,j), column pair (a,b)):
    x_ia - z_ja - x_ib + z_jb = 0 (mod N)
H[i*N+r, c*N+((r+s_ic) mod N)] = 1 (994-142-40 sign convention).

Solutions are drawn as exact integer solutions of the homogeneous system
(reduced mod N afterwards), so any composite N is admissible.
"""
import argparse
import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
sys.path.insert(0, os.path.join(ROOT, "research", "campaigns",
                                "beat-surface-k50-w8-unrestricted"))

import numpy as np  # noqa: E402
from css import verify_css, compute_k  # noqa: E402
from prescreen import block_structure  # noqa: E402
from surrogate import distance_rand_witness  # noqa: E402

# ---------------------------------------------------------------------------
# templates (verbatim from codes/ provenance)
# ---------------------------------------------------------------------------
TEMPLATES = {}

# 994-142-40: 6x14 pair-closed, rate 1/7
TEMPLATES["pp614"] = {
    "rows": [[0, 1, 2, 3, 4, 5, 10, 11],
             [0, 1, 4, 5, 6, 7, 10, 11],
             [0, 1, 6, 7, 8, 9, 12, 13],
             [2, 3, 6, 7, 10, 11, 12, 13],
             [2, 3, 4, 5, 8, 9, 12, 13],
             [0, 1, 2, 3, 4, 5, 8, 9]],
    "L": 14,
    "pairing": {
        "0,0": [[0, 2], [1, 3], [4, 10], [5, 11]],
        "0,1": [[0, 4], [1, 5], [10, 11]],
        "0,2": [[0, 1]],
        "0,3": [[2, 10], [3, 11]],
        "0,4": [[2, 5], [3, 4]],
        "0,5": [[0, 3], [1, 2], [4, 5]],
        "1,0": [[0, 4], [1, 5], [10, 11]],
        "1,1": [[0, 6], [1, 7], [4, 11], [5, 10]],
        "1,2": [[0, 7], [1, 6]],
        "1,3": [[6, 11], [7, 10]],
        "1,4": [[4, 5]],
        "1,5": [[0, 5], [1, 4]],
        "2,0": [[0, 1]],
        "2,1": [[0, 7], [1, 6]],
        "2,2": [[0, 6], [1, 7], [8, 9], [12, 13]],
        "2,3": [[6, 13], [7, 12]],
        "2,4": [[8, 13], [9, 12]],
        "2,5": [[0, 8], [1, 9]],
        "3,0": [[2, 11], [3, 10]],
        "3,1": [[6, 11], [7, 10]],
        "3,2": [[6, 13], [7, 12]],
        "3,3": [[2, 12], [3, 13], [6, 7], [10, 11]],
        "3,4": [[2, 13], [3, 12]],
        "3,5": [[2, 3]],
        "4,0": [[2, 5], [3, 4]],
        "4,1": [[4, 5]],
        "4,2": [[8, 13], [9, 12]],
        "4,3": [[2, 13], [3, 12]],
        "4,4": [[2, 12], [3, 13], [4, 9], [5, 8]],
        "4,5": [[2, 4], [3, 5], [8, 9]],
        "5,0": [[0, 3], [1, 2], [4, 5]],
        "5,1": [[0, 5], [1, 4]],
        "5,2": [[0, 9], [1, 8]],
        "5,3": [[2, 3]],
        "5,4": [[2, 4], [3, 5], [8, 9]],
        "5,5": [[0, 2], [1, 3], [4, 8], [5, 9]],
    },
    # published exponents at N=71 (for builder validation)
    "S_X_71": [[62, 40, 7, 40, 37, 52, None, None, None, None, 27, 27, None, None],
               [41, 0, None, None, 8, 4, 4, 20, None, None, 16, 21, None, None],
               [49, 32, None, None, None, None, 31, 33, 33, 16, None, None, 6, 65],
               [None, None, 8, 8, None, None, 0, 49, None, None, 53, 25, 5, 12],
               [None, None, 29, 15, 70, 0, None, None, 69, 9, None, None, 7, 38],
               [5, 21, 54, 59, 32, 52, None, None, 68, 13, None, None, None, None]],
    "S_Z_71": [[9, 63, 25, 63, 47, 67, None, None, None, None, 37, 42, None, None],
               [49, 13, None, None, 24, 25, 12, 33, None, None, 37, 37, None, None],
               [17, 66, None, None, None, None, 70, 67, 42, 25, None, None, 23, 11],
               [None, None, 22, 27, None, None, 68, 46, None, None, 42, 14, 19, 31],
               [None, None, 32, 13, 10, 6, None, None, 4, 20, None, None, 10, 36],
               [64, 4, 42, 42, 12, 27, None, None, 48, 59, None, None, None, None]],
}

# 996-166-34: 5x12 pair-complement-2, rate 1/6
TEMPLATES["pp512"] = {
    "rows": [[4, 5, 6, 7, 8, 9, 10, 11],
             [2, 3, 6, 7, 8, 9, 10, 11],
             [0, 1, 6, 7, 8, 9, 10, 11],
             [0, 1, 2, 3, 4, 5, 10, 11],
             [0, 1, 2, 3, 4, 5, 8, 9]],
    "L": 12,
    "pairing": {
        "0,0": [[4, 6], [5, 7], [8, 9], [10, 11]],
        "0,1": [[6, 11], [7, 9], [8, 10]],
        "0,2": [[6, 8], [7, 10], [9, 11]],
        "0,3": [[4, 11], [5, 10]],
        "0,4": [[4, 9], [5, 8]],
        "1,0": [[6, 8], [7, 10], [9, 11]],
        "1,1": [[2, 7], [3, 6], [8, 9], [10, 11]],
        "1,2": [[6, 11], [7, 9], [8, 10]],
        "1,3": [[2, 11], [3, 10]],
        "1,4": [[2, 9], [3, 8]],
        "2,0": [[6, 11], [7, 9], [8, 10]],
        "2,1": [[6, 8], [7, 10], [9, 11]],
        "2,2": [[0, 6], [1, 7], [8, 9], [10, 11]],
        "2,3": [[0, 11], [1, 10]],
        "2,4": [[0, 9], [1, 8]],
        "3,0": [[4, 11], [5, 10]],
        "3,1": [[2, 11], [3, 10]],
        "3,2": [[0, 11], [1, 10]],
        "3,3": [[0, 1], [2, 3], [4, 5], [10, 11]],
        "3,4": [[0, 5], [1, 2], [3, 4]],
        "4,0": [[4, 9], [5, 8]],
        "4,1": [[2, 9], [3, 8]],
        "4,2": [[0, 9], [1, 8]],
        "4,3": [[0, 3], [1, 4], [2, 5]],
        "4,4": [[0, 1], [2, 3], [4, 5], [8, 9]],
    },
}

# 1000-200-29: 4x10 pair-complement, rate 1/5; X and Z templates differ
TEMPLATES["pp410"] = {
    "rows_X": [[0, 1, 2, 3, 4, 5, 8, 9],
               [0, 1, 2, 3, 6, 7, 8, 9],
               [0, 1, 4, 5, 6, 7, 8, 9],
               [2, 3, 4, 5, 6, 7, 8, 9]],
    "rows_Z": [[0, 1, 2, 3, 4, 5, 6, 7],
               [0, 1, 2, 3, 4, 5, 8, 9],
               [0, 1, 2, 3, 6, 7, 8, 9],
               [2, 3, 4, 5, 6, 7, 8, 9]],
    "L": 10,
    "pairing": {
        "0,0": [[0, 4], [1, 2], [3, 5]],
        "0,1": [[0, 5], [1, 4], [2, 8], [3, 9]],
        "0,2": [[0, 1], [2, 3], [8, 9]],
        "0,3": [[2, 5], [3, 8], [4, 9]],
        "1,0": [[0, 7], [1, 6], [2, 3]],
        "1,1": [[0, 8], [1, 3], [2, 9]],
        "1,2": [[0, 2], [1, 8], [3, 7], [6, 9]],
        "1,3": [[2, 8], [3, 9], [6, 7]],
        "2,0": [[0, 5], [1, 4], [6, 7]],
        "2,1": [[0, 9], [1, 5], [4, 8]],
        "2,2": [[0, 7], [1, 9], [6, 8]],
        "2,3": [[4, 7], [5, 6], [8, 9]],
        "3,0": [[2, 7], [3, 4], [5, 6]],
        "3,1": [[2, 3], [4, 5], [8, 9]],
        "3,2": [[2, 8], [3, 9], [6, 7]],
        "3,3": [[2, 4], [3, 7], [5, 8], [6, 9]],
    },
}


# ---------------------------------------------------------------------------
# exponent-system solver (exact, over Z; reduce mod N afterwards)
# ---------------------------------------------------------------------------
def build_system(tpl):
    """Return (cols, M): cols = list of var keys ('x',i,c) / ('z',j,c);
    M = equations as integer rows (coefficients of x_ia - z_ja - x_ib + z_jb).
    """
    rowsX = tpl.get("rows_X") or tpl["rows"]
    rowsZ = tpl.get("rows_Z") or tpl["rows"]
    cols = []
    idx = {}
    for i, rcols in enumerate(rowsX):
        for c in rcols:
            idx[("x", i, c)] = len(cols)
            cols.append(("x", i, c))
    for j, rcols in enumerate(rowsZ):
        for c in rcols:
            idx[("z", j, c)] = len(cols)
            cols.append(("z", j, c))
    eqs = []
    for key, pairs in tpl["pairing"].items():
        i_s, j_s = key.split(",")
        i, j = int(i_s), int(j_s)
        for (a, b) in pairs:
            eq = [0] * len(cols)
            eq[idx[("x", i, a)]] += 1
            eq[idx[("z", j, a)]] -= 1
            eq[idx[("x", i, b)]] -= 1
            eq[idx[("z", j, b)]] += 1
            eqs.append(eq)
    return cols, np.array(eqs, dtype=object), idx


def solve_system(tpl):
    """Exact RREF over Q. Returns (cols, pivot_cols, free_cols, C, L) where
    x_dep = -C @ x_free (C rational, exact Fractions) and L = lcm of the
    denominators per dependent row combined (global lcm) so that integral
    free vectors with entries in L*Z give integral solutions."""
    cols, M, idx = build_system(tpl)
    M = [[Fraction(v) for v in row] for row in M]
    nrows, ncols = len(M), len(M[0])
    pivots = []
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, nrows):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(nrows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == nrows:
            break
    free = [c for c in range(ncols) if c not in set(pivots)]
    # dependent rows: row t has pivot at column pivots[t]; x_{pivots[t]} =
    # -sum_{c free} M[t][c] * x_c
    C = []
    denoms = []
    for t in range(r):
        row = []
        for c in free:
            row.append(M[t][c])
        C.append(row)
        denoms.extend([fr.denominator for fr in row])
    L = 1
    for d in denoms:
        L = L * d // __import__("math").gcd(L, d)
    return cols, pivots, free, C, L


def draw_solution(tpl, N, rng, shift=None):
    """Random exact integer solution reduced mod N -> S_X, S_Z arrays
    (None where the template has no entry).

    The RREF gives x_pivot = -C @ x_free over Q. Free entries are drawn as
    multiples of L (the global denominator lcm) so dependent entries come out
    integral; the whole integer vector is then reduced mod N and the pairing
    equations are re-checked mod N before returning."""
    cols, pivots, free, C, L = solve_system(tpl)
    u = {c: int(rng.integers(0, N)) for c in free}
    fv = {c: u[c] * L for c in free}
    vals = {}
    for c in free:
        vals[c] = fv[c] % N
    for t, pc in enumerate(pivots):
        s = Fraction(0)
        for pos, c in enumerate(free):
            if C[t][pos] != 0:
                s += C[t][pos] * fv[c]
        assert s.denominator == 1, "non-integral dependent value"
        vals[pc] = (-int(s)) % N
    _check_equations(tpl, vals, N)
    rowsX = tpl.get("rows_X") or tpl["rows"]
    rowsZ = tpl.get("rows_Z") or tpl["rows"]
    Lsize = tpl["L"]
    SX = [[None] * Lsize for _ in rowsX]
    SZ = [[None] * Lsize for _ in rowsZ]
    for (side, i, c), pos in _index_map(tpl).items():
        v = vals[pos] % N
        if shift is not None:
            v = (v + shift) % N
        (SX if side == "x" else SZ)[i][c] = v
    return SX, SZ


_INDEX_CACHE = {}


def _check_equations(tpl, vals, N):
    """Assert every pairing equation holds mod N on the drawn values."""
    rowsX = tpl.get("rows_X") or tpl["rows"]
    rowsZ = tpl.get("rows_Z") or tpl["rows"]
    im = _index_map(tpl)
    for key, pairs in tpl["pairing"].items():
        i, j = map(int, key.split(","))
        for (a, b) in pairs:
            xia = vals[im[("x", i, a)]]
            zja = vals[im[("z", j, a)]]
            xib = vals[im[("x", i, b)]]
            zjb = vals[im[("z", j, b)]]
            assert (xia - zja - xib + zjb) % N == 0, \
                f"equation violation at cell {key} pair {a},{b}"


def _index_map(tpl):
    key = id(tpl)
    if key not in _INDEX_CACHE:
        cols, _, _, _, _ = solve_system(tpl)
        _INDEX_CACHE[key] = {c: p for p, c in enumerate(cols)}
    return _INDEX_CACHE[key]


def build_H(tpl, SX, SZ, N):
    """H[i*N+r, c*N+((r+s_ic) mod N)] = 1."""
    rowsX = tpl.get("rows_X") or tpl["rows"]
    rowsZ = tpl.get("rows_Z") or tpl["rows"]
    Lsize = tpl["L"]
    HX = np.zeros((len(rowsX) * N, Lsize * N), dtype=np.int8)
    HZ = np.zeros((len(rowsZ) * N, Lsize * N), dtype=np.int8)
    for i, rcols in enumerate(rowsX):
        for c in rcols:
            s = SX[i][c]
            rs = (np.arange(N) + s) % N
            HX[i * N + np.arange(N), c * N + rs] = 1
    for j, rcols in enumerate(rowsZ):
        for c in rcols:
            s = SZ[j][c]
            rs = (np.arange(N) + s) % N
            HZ[j * N + np.arange(N), c * N + rs] = 1
    return HX, HZ


def tanner_girth(HX, HZ, cap=8):
    """Tanner-graph girth of the (check, qubit) bipartite graph, capped."""
    g = cap + 1
    for H in (HX, HZ):
        rows = [np.nonzero(r)[0] for r in H]
        # BFS from each check over 2-paths via qubits
        nbr = {}
        for qi, col in enumerate(H.T):
            cs = np.nonzero(col)[0]
            if len(cs):
                nbr[qi] = cs
        for qi, cs in nbr.items():
            for c0 in cs:
                # cycle length 2*girth detected via double BFS; cheap cap:
                pass
        # simple 4-cycle and 6-cycle counters instead of full girth
    # count 4-cycles: pairs of checks sharing >= 2 qubits
    def count4(H):
        Hb = (np.asarray(H) % 2).astype(np.int8)
        inter = Hb @ Hb.T
        np.fill_diagonal(inter, 0)
        return int((inter >= 2).sum() // 2)
    c4x, c4z = count4(HX), count4(HZ)
    return c4x, c4z


def quick_eval(tpl, SX, SZ, N):
    HX, HZ = build_H(tpl, SX, SZ, N)
    ok = bool(verify_css(HX, HZ))
    k = int(compute_k(HX, HZ)) if ok else -1
    conn, info = None, None
    try:
        bs = block_structure(HX, HZ)
        conn = len(bs.get("blocks", [])) == 1 if isinstance(bs, dict) else None
    except Exception:
        pass
    c4 = tanner_girth(HX, HZ)
    return HX, HZ, dict(css=ok, k=k, c4=c4, conn=conn)


def published_eval(tplname, N):
    tpl = TEMPLATES[tplname]
    SX = tpl["S_X_71"]
    SZ = tpl["S_Z_71"]
    assert N == 71
    HX, HZ, info = quick_eval(tpl, SX, SZ, N)
    print(f"published {tplname}@71 rebuild: {info}")
    # verify the pairing equations mod 71 on the published arrays
    rowsX = tpl.get("rows_X") or tpl["rows"]
    rowsZ = tpl.get("rows_Z") or tpl["rows"]
    bad = 0
    for key, pairs in tpl["pairing"].items():
        i, j = map(int, key.split(","))
        for (a, b) in pairs:
            v = (SX[i][a] - SZ[j][a] - SX[i][b] + SZ[j][b]) % 71
            if v != 0:
                bad += 1
    print(f"pairing-equation violations on published arrays: {bad}")
    return HX, HZ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--template", default="pp614")
    ap.add_argument("--N", type=int, default=49)
    ap.add_argument("--draws", type=int, default=5)
    ap.add_argument("--seed", type=int, default=49001)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    if args.validate:
        published_eval("pp614", 71)
        sys.exit(0)
    tpl = TEMPLATES[args.template]
    t0 = time.time()
    cols, pivots, free, C, L = solve_system(tpl)
    print(f"system: {len(cols)} vars, {len(pivots)} pivots, {len(free)} free, "
          f"L={L}  ({time.time()-t0:.1f}s)")
    for d in range(args.draws):
        SX, SZ = draw_solution(tpl, args.N, rng)
        HX, HZ, info = quick_eval(tpl, SX, SZ, args.N)
        print(f"draw {d}: N={args.N} css={info['css']} k={info['k']} "
              f"4cycles(X,Z)={info['c4']}")
