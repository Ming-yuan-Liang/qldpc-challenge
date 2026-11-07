"""Precompute the odd-m menu for cyclic-GB screening: which m admit a
designed divisor of degree in [23,28] (k=45..55 band), cached to JSON.

Run once per machine; both tracks share it. Factoring x^m-1 is the cost the
kit sampler would otherwise pay repeatedly inside a search.
"""
import json
import os
import random
import sys
import time

KIT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge\research\kit"
sys.path.insert(0, KIT)

import gf2poly  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "l4_m_menu.json")


def m_feasible(m, lo=23, hi=27):
    """Can some subset of irreducible factor degrees of x^m-1 sum into the band?

    Band [23,27]: the kit sampler draws designed_divisor over
    (k_band[0]//2, k_band[1]//2) = (22, 27), and k = 2 deg g is even, so the
    realizable degrees are 23..27. A degree-28-only m would leave the
    sampler's `while built < num` spinning forever with no yield."""
    facs = gf2poly.factor_squarefree(gf2poly.x_pow_m_minus_1(m), random.Random(m))
    degs = sorted(gf2poly.deg(p) for p in facs)
    # subset-sum reachability up to hi
    reach = {0}
    for d in degs:
        reach |= {s + d for s in reach if s + d <= hi}
    return bool(lo <= max(reach) and any(lo <= s <= hi for s in reach)), degs


def main(lo_m, hi_m):
    menu = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            menu = json.load(f)
    t0 = time.time()
    for m in range(lo_m, hi_m + 1, 2):
        if str(m) in menu:
            continue
        ok, degs = m_feasible(m)
        menu[str(m)] = {"ok": bool(ok), "degs": degs}
        if len(menu) % 10 == 0 or not ok:
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(menu, f)
        print(f"m={m} ok={ok} ndeg={len(degs)} dt={time.time()-t0:.0f}s",
              flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(menu, f)
    good = sorted(int(k) for k, v in menu.items() if v["ok"])
    print(f"feasible m ({len(good)}): {good}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
