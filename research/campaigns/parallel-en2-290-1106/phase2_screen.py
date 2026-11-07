"""PHASE 2 stage A: continue the kasai-affine-q17-directed-s20 directed lane.

The original lane (research/campaigns/kasai-affine-q17-directed-s20) never ran:
its dir holds only campaign.json + run.py, no screen_cache/summary. This script
executes its generator on this lane's budget: 100 fresh directed draws,
sample_kasai_affine(100, q_range=(17,17), weight=6, seed=20) -- the first 100
draws of exactly the config that lane declares.

Screen: 400-trial numpy distance_rand (default pair_depth=10, the lane
instrument), board prepass (connectivity + fingerprint dedup + WL flag) via
screen(). Output: screen_cache.json in lane_runner's format plus a ranked
phase2_screen_ranked.json. Nothing here is a submission.
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from search import sample_kasai_affine, screen
from prescreen import board_index


def main():
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    t0 = time.time()
    cands = list(sample_kasai_affine(num, q_range=(17, 17), weight=6, seed=20))
    print(f"generator -> {len(cands)} built", flush=True)

    index = board_index()
    print(f"board index ready ({time.time()-t0:.0f}s)", flush=True)

    audit = {}
    recs = screen(cands, min_k=1, min_d=4, trials=400, seed=0,
                  index=index, audit=audit, workers=workers)
    print(f"screened {len(recs)}/{len(cands)}; audit {audit}; "
          f"{time.time()-t0:.0f}s", flush=True)

    spec_keys = [json.dumps(s, sort_keys=True) for s, _, _ in cands]
    spec_to_rec = {json.dumps(r["spec"], sort_keys=True): r for r in recs}
    rec_list = [spec_to_rec.get(kk) for kk in spec_keys]
    with open(os.path.join(_HERE, "screen_cache.json"), "w", encoding="utf-8") as f:
        json.dump({"spec_keys": spec_keys, "recs": rec_list, "screen_audit": audit}, f)

    ranked = [{"idx": i,
               "spec": recs_i["spec"],
               "n": recs_i["n"], "k": recs_i["k"], "d": recs_i["d"],
               "efficiency": recs_i["efficiency"],
               "fingerprint": recs_i.get("fingerprint"),
               "board_wl": recs_i.get("board_wl")}
              for i, recs_i in enumerate(rec_list) if recs_i is not None]
    ranked.sort(key=lambda r: -r["efficiency"])
    with open(os.path.join(_HERE, "phase2_screen_ranked.json"), "w",
              encoding="utf-8") as f:
        json.dump(ranked, f, indent=1)
    print("top 10 by screen efficiency:")
    for r in ranked[:10]:
        print(f"  [[{r['n']},{r['k']},{r['d']}]] eff {r['efficiency']:.1f} "
              f"idx {r['idx']} a={r['spec']['a']} b={r['spec']['b']}", flush=True)


if __name__ == "__main__":
    main()
