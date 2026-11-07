"""Re-check the four staged candidates against the CURRENT board.

Runs in a clean worktree of origin/main (cwd there); candidates stay OUT of
the worktree's codes/ so the board comparison is unpolluted. Mirrors
cli/qldpc.py frontier_summary: same entry shape, same cells(), same pareto()
and the same domination relation over (n, k, d, w).
"""
import json
import os
import sys

WT = sys.argv[1]
CAND_PATHS = sys.argv[2:]
for p in (os.path.join(WT, "verify"), os.path.join(WT, "site"),
          os.path.join(WT, "research"), os.path.join(WT, "research", "kit")):
    sys.path.insert(0, p)

import qldpc_verify  # noqa: E402
from build import load_entries, pareto, cells  # noqa: E402

print("loading the board (cold structural pass over codes/) ...",
      file=sys.stderr)
t0 = __import__("time").time()
entries = load_entries()
print(f"loaded {len(entries)} entries in {__import__('time').time() - t0:.1f}s",
      file=sys.stderr)

out = []
for path in CAND_PATHS:
    slug = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    rep = qldpc_verify.verify(doc, refute=False)
    if not rep.get("ok"):
        bad = [c for c in rep.get("checks", []) if not c.get("ok", True)]
        out.append({"slug": slug, "structural": "FAIL",
                    "failed": [c.get("check") for c in bad]})
        continue
    n, k = doc["n"], doc["k"]
    comp = rep.get("computed", {})
    earned = rep.get("earned_distance", {}).get("d")
    d = earned["value"] if isinstance(earned, dict) else (
        earned or doc["distance"]["d"])
    cand = {"slug": slug, "n": n, "k": k, "d": d,
            "code_type": doc.get("code_type", "CSS"),
            "eff": round(k * d * d / n, 3),
            "w": comp.get("max_check_weight"),
            "locality_class": comp.get("locality_class", "unrestricted"),
            "weight_class": comp.get("weight_class", "weight-9plus")}
    res = {"slug": slug, "structural": "ok",
           "cell": f'{cand["locality_class"]}/{cand["weight_class"]}',
           "d": d, "w": cand["w"], "kd2n": cand["eff"], "cells": []}
    for cell in cells(cand):
        peers = [e for e in entries
                 if cell in cells(e)
                 and e.get("code_type", "CSS") == cand["code_type"]]
        on_front = len(peers) in pareto(peers + [cand])
        dominated = [e for e in peers
                     if e["n"] >= cand["n"] and e["k"] <= cand["k"]
                     and e["d"] <= cand["d"] and e["w"] >= cand["w"]
                     and (e["n"] > cand["n"] or e["k"] < cand["k"]
                          or e["d"] < cand["d"] or e["w"] > cand["w"])]
        dominated.sort(key=lambda e: (-e["eff"], e["n"]))
        dominators = [e for e in peers
                      if e["n"] <= cand["n"] and e["k"] >= cand["k"]
                      and e["d"] >= cand["d"] and e["w"] <= cand["w"]
                      and (e["n"] < cand["n"] or e["k"] > cand["k"]
                           or e["d"] > cand["d"] or e["w"] < cand["w"])]
        res["cells"].append({
            "cell": list(cell), "peers": len(peers),
            "on_frontier": bool(on_front),
            "dominates": [f"[[{e['n']},{e['k']},{e['d']}]]"
                          for e in dominated][:8],
            "dominated_by": [f"[[{e['n']},{e['k']},{e['d']}]]"
                             for e in dominators][:8]})
    out.append(res)

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "board_recheck_1105.json")
with open(dest, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
