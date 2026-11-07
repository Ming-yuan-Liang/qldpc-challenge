"""q19-k14 RESUME lane screening chunk (L1 continuation).

The 2026-11-06 screen (screen_chunk.py, 250 draws, w in {7,8,9}) left the
k in [12,16] corner starved: 245/250 draws fell k_out, concentrated at
k = 0-4 under w = 9. This continuation shifts the weight distribution down
one notch (w in {6,7,8}) to raise the in-range yield toward the lane's
k >= 14 target, on a fresh seed base (20261107) so no draw of the original
stream is redrawn. Everything else is the lane protocol: build -> CSS by
construction -> compute_k -> k filter -> connectivity -> css_fingerprint
(within-chunk dedup) -> 400-trial RIS reading.

Usage: python l1_screen.py <start> <count> <out.jsonl>
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

BASE_SEED = 20261107          # fresh stream; 20261106 + i is the finished screen
SCREEN_TRIALS = 400
SCREEN_SEED_BASE = 556000
K_LO, K_HI = 12, 16


def draw_pair(i):
    """Deterministic continuation draw i: |a| = |b| = w in {6,7,8}, exponents
    uniform in [0, 342)."""
    rng = np.random.default_rng(BASE_SEED + i)
    w = int(rng.choice([6, 7, 8]))
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
