"""L5 secondary probe: non-abelian 2BGA weight-8 (4+4 supports) k-scan.

Board precedents: 336-28-16 (PSL(2,7), k/|G| = 0.167), 300-36-13
(C5 x D30, k/|G| = 0.24). Lane needs k 95-105 at n = 2|G| in [500, 1000],
i.e. k/|G| in [0.19, 0.42]. This scan measures the k distribution on
non-abelian groups of order 250-500 to see if the family can reach the band.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))

from group_algebra import (alt, sym, perm_group, direct_product,  # noqa
                           cyclic_product, build_2bga)
from css import compute_k  # noqa: E402


def psl2q(q):
    """PSL(2, q) for odd prime q, acting on P^1(F_q) (q+1 points)."""
    pts = [(0, 1)] + [(1, x) for x in range(q)]     # infinity, then a/1
    idx = {p: i for i, p in enumerate(pts)}

    def apply(m, p):
        a, b = p
        num = (m[0] * a + m[1] * b) % q
        den = (m[2] * a + m[3] * b) % q
        if den == 0:
            return (1, 0)                     # [num:0] = [1:0]
        if num == 0:
            return (0, 1)                     # [0:den] = [0:1]
        return (1, (den * pow(num, -1, q)) % q)   # [num:den] = [1:den/num]

    def mat_perm(m):
        m = tuple(v % q for v in m)
        return tuple(idx[apply(m, p)] for p in pts)

    def mulm(A, B):
        return ((A[0] * B[0] + A[1] * B[2]) % q, (A[0] * B[1] + A[1] * B[3]) % q,
                (A[2] * B[0] + A[3] * B[2]) % q, (A[2] * B[1] + A[3] * B[3]) % q)

    # generators of SL(2,q): [[1,1],[0,1]], [[0,-1],[1,0]]; the projective
    # action factors through PSL(2,q) automatically (h and -h act alike),
    # so closing the two permutation images gives PSL(2,q) directly.
    gens = [mat_perm(m) for m in [(1, 1, 0, 1), (0, q - 1, 1, 0)]]
    return perm_group(gens, q + 1)


def gl2p(p):
    """GL(2, p) acting on the p^2 nonzero-anchored vector space (p^2 points)."""
    pts = [(x, y) for x in range(p) for y in range(p)]
    idx = {v: i for i, v in enumerate(pts)}
    ident = (1, 0, 0, 1)
    mats = [(1, 1, 0, 1), (0, 1, 1, 0), (2, 0, 0, 1), (1, 0, 0, 2)]
    group = {ident}
    frontier = [ident]
    while frontier:
        nxt = []
        for a in frontier:
            for g in mats:
                h = ((a[0] * g[0] + a[1] * g[2]) % p, (a[0] * g[1] + a[1] * g[3]) % p,
                     (a[2] * g[0] + a[3] * g[2]) % p, (a[2] * g[1] + a[3] * g[3]) % p)
                if h not in group:
                    group.add(h)
                    nxt.append(h)
        frontier = nxt
    perms = []
    for m in group:
        pm = []
        for v in pts:
            w = ((m[0] * v[0] + m[1] * v[1]) % p, (m[2] * v[0] + m[3] * v[1]) % p)
            pm.append(idx[w])
        perms.append(tuple(pm))
    return perm_group(perms, p * p)


def build_groups():
    out = {}
    mul, el = psl2q(7)
    out["PSL27"] = mul
    m168 = mul
    m2, _ = cyclic_product(2)
    out["PSL27xC2"], _ = direct_product(m168, m2)
    out["A6"] = alt(6)[0]
    mA5 = alt(5)[0]
    m7, _ = cyclic_product(7)
    out["A5xC7"], _ = direct_product(mA5, m7)
    out["GL25"] = gl2p(5)[0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", required=True)
    ap.add_argument("--draws", type=int, default=500)
    ap.add_argument("--seed", type=int, default=61001)
    ap.add_argument("--kmin", type=int, default=95)
    ap.add_argument("--kmax", type=int, default=105)
    ap.add_argument("--ledger", default=None)
    args = ap.parse_args()
    groups = build_groups()
    mul = groups[args.group]
    N = mul.shape[0]
    n = 2 * N
    rng = np.random.default_rng(args.seed)
    ledger_path = args.ledger or os.path.join(
        HERE, f"ledger_2bga_{args.group}_{args.seed}.json")
    led = {"group": args.group, "N": N, "n": n, "seed": args.seed,
           "kmin": args.kmin, "kmax": args.kmax, "draws": []}
    if os.path.exists(ledger_path):
        led = json.load(open(ledger_path, encoding="utf-8"))
        print(f"resuming with {len(led['draws'])} draws", flush=True)
    hist = {}
    best_k = 0
    t0 = time.time()
    done = len(led["draws"])
    for d in range(done, args.draws):
        a = [0] + [int(x) for x in rng.integers(1, N, size=3)]
        a = sorted(set(a))
        while len(a) < 4:
            x = int(rng.integers(1, N))
            if x not in a:
                a.append(x)
        b = [0] + [int(x) for x in rng.integers(1, N, size=3)]
        b = sorted(set(b))
        while len(b) < 4:
            x = int(rng.integers(1, N))
            if x not in b:
                b.append(x)
        HX, HZ = build_2bga(mul, a, b)
        k = int(compute_k(HX, HZ))
        rec = {"a": a, "b": b, "k": k}
        led["draws"].append(rec)
        hist[k] = hist.get(k, 0) + 1
        best_k = max(best_k, k)
        if k and 0.9 * args.kmax <= k:
            print(f"  draw {d}: k={k} a={a} b={b}", flush=True)
        if (d + 1) % 25 == 0 or d == args.draws - 1:
            with open(ledger_path, "w", encoding="utf-8") as f:
                json.dump(led, f)
            print(f"{d+1}/{args.draws} draws: best_k={best_k} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    print("k histogram:", dict(sorted(hist.items())))


if __name__ == "__main__":
    main()
