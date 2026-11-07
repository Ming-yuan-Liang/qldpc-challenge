"""q19-k14 lane screening chunk: Kasai affine 2BGA over Aff(F_19), n=684.

Draws |a| = |b| = w, w in {7,8,9} uniform, exponents uniform in [0,342).
Per draw: build -> compute_k -> k in [12,16] filter -> connectivity ->
css_fingerprint (within-chunk dedup; cross-chunk in merge) -> 400-trial RIS
reading. Appends one JSON line per draw to the chunk's JSONL.

Usage: python screen_chunk.py <start> <count> <out.jsonl>
"""
import json
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
from qldpc_verify import css_fingerprint
from surrogate import distance_rand_witness, prepare_distance_search

BASE_SEED = 20261106
SCREEN_TRIALS = 400
SCREEN_SEED_BASE = 555000
K_LO, K_HI = 12, 16


def draw_pair(i):
    """Deterministic draw i: |a| = |b| = w in {7,8,9}, exponents uniform in [0,342)."""
    rng = np.random.default_rng(BASE_SEED + i)
    w = int(rng.choice([7, 8, 9]))
    a = sorted(int(x) for x in rng.choice(342, size=w, replace=False))
    b = sorted(int(x) for x in rng.choice(342, size=w, replace=False))
    return w, a, b


def main():
    start, count, out_path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    seen_fp = set()
    with open(out_path, "a", encoding="utf-8") as out:
        for i in range(start, start + count):
            t0 = time.time()
            rec = {"i": i, "w": None, "k": None, "status": None}
            try:
                w, a, b = draw_pair(i)
                rec.update(w=w, a=a, b=b)
                HX, HZ = build_2bga_affine(19, a, b)
                if not verify_css(HX, HZ):
                    rec["status"] = "css_fail"
                    continue
                k = compute_k(HX, HZ)
                rec["k"] = k
                if not (K_LO <= k <= K_HI):
                    rec["status"] = "k_out"
                    continue
                st = block_structure(HX, HZ)
                rec["connected"] = bool(st["connected"])
                if not st["connected"]:
                    rec["status"] = "disconnected"
                    continue
                fp = css_fingerprint(HX, HZ)
                rec["fp"] = fp
                if fp in seen_fp:
                    rec["status"] = "dup_in_chunk"
                    continue
                seen_fp.add(fp)
                prep = prepare_distance_search(HX, HZ)
                res = distance_rand_witness(
                    prepared=prep, trials=SCREEN_TRIALS,
                    seed=SCREEN_SEED_BASE + i, backend="numpy")
                if res:
                    rec["status"] = "read"
                    rec["d_screen"] = int(res.weight)
                    rec["side"] = res.side
                    rec["efficiency"] = round(k * res.weight ** 2 / 684, 2)
                else:
                    rec["status"] = "no_logical_found"
            except Exception as e:  # noqa: BLE001 - record and keep the chunk alive
                rec["status"] = f"error:{type(e).__name__}:{e}"
            finally:
                rec["secs"] = round(time.time() - t0, 1)
                out.write(json.dumps(rec) + "\n")
                out.flush()
                if rec["status"] not in ("k_out",):
                    print(f"[{start}] draw {i}: {rec['status']} "
                          f"k={rec.get('k')} d_screen={rec.get('d_screen')}",
                          flush=True)


if __name__ == "__main__":
    main()
