"""WL-signature scan of the lane's candidate pool (foreground, seconds).

Computes qldpc_verify.signature for each in-range draw (original stream +
new-stream 84) so the supervisor knows how many structural classes the
k>=12 corner actually contains before spending rungs.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (os.path.join(ROOT, "research", "kit"), os.path.join(ROOT, "verify"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np
from bench_one import draw_pair
from l1_screen import draw_pair as draw_pair_new
from bbga_labels import build_2bga_affine
import qldpc_verify

def sig_for(HX, HZ, k):
    doc = {"n": HX.shape[1], "k": k, "code_type": "CSS",
           "checks": {"X": [sorted(np.nonzero(r % 2)[0].tolist()) for r in HX],
                      "Z": [sorted(np.nonzero(r % 2)[0].tolist()) for r in HZ]},
           "distance": {"d": 0}}
    s = qldpc_verify.signature(doc)
    return s["hash"]

out = {}
for i in (229, 106, 12, 70, 72):
    w, a, b = draw_pair(i)
    HX, HZ = build_2bga_affine(19, a, b)
    from css import compute_k
    k = compute_k(HX, HZ)
    out[f"orig-{i}"] = {"k": k, "sig": sig_for(HX, HZ, k)}
    print(f"orig draw {i}: k={k} sig={out[f'orig-{i}']['sig']}", flush=True)
w, a, b = draw_pair_new(84)
HX, HZ = build_2bga_affine(19, a, b)
from css import compute_k
k = compute_k(HX, HZ)
out["new-84"] = {"k": k, "sig": sig_for(HX, HZ, k)}
print(f"new-stream draw 84: k={k} sig={out['new-84']['sig']}", flush=True)
with open(os.path.join(HERE, "l1_wl_scan.json"), "w") as f:
    json.dump(out, f, indent=1)
print("distinct sigs:", len({v["sig"] for v in out.values()}))
