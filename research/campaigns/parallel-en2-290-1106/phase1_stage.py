"""PHASE 1 staging decision for the EN-2 winner (b3 move of the [[544,18,84]]
elite, screen claim d<=96 at 400 trials).

Reads phase1_witness_seed930001/2/3.json (20,000-trial fresh-seed rungs).

Lane rule: stage only if the lightest reading across seeds stays within 2
units of the claimed 96 (the claim was already an upper bound); the doc is
then packaged AT the lightest reading with that rung's witness embedded
(CI-refutation lesson: the claim must equal the lowest reading). If the
readings collapsed below 94, report the honest reading and do not stage.

On staging: make_submission with per-side witnesses (the lighter side's
witness comes from the rungs; the other side from a fresh lightest_logical
search at the same depth), save_submission under this run's staging dir, then
gate_and_record. Nothing here is a submission.
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from bbga_labels import build_2bga_affine
from coordination import gate_and_record, staging_dir, unique_path
from submit import make_submission, save_submission

Q = 17
A = [245, 84, 96, 270, 163, 268]
B = [245, 252, 47, 59, 143, 70]
CLAIM_D = 96
AUTHOR = "@Ming-yuan-Liang"


def dense_rungs():
    rungs = []
    for seed in (930001, 930002, 930003):
        with open(os.path.join(_HERE, f"phase1_witness_seed{seed}.json"),
                  encoding="utf-8") as f:
            rungs.append(json.load(f))
    return rungs


def main():
    rungs = dense_rungs()
    weights = [r["weight"] for r in rungs]
    print("rung readings:", {r["seed"]: r["weight"] for r in rungs}, flush=True)
    if any(w is None for w in weights):
        print("some rung found no logical; not staging", flush=True)
        return 1
    lightest = min(weights)
    print(f"lightest reading {lightest} vs claimed {CLAIM_D} "
          f"(delta {CLAIM_D - lightest})", flush=True)
    if CLAIM_D - lightest > 2:
        print("readings collapsed below the claim by more than 2: "
              "NOT staging; honest reading recorded", flush=True)
        return 2

    best = min(rungs, key=lambda r: r["weight"])
    light_side, light_wit = best["side"], best["support"]
    light_w = best["weight"]

    HX, HZ = build_2bga_affine(Q, A, B)
    HX = np.asarray(HX, dtype=np.int8) % 2
    HZ = np.asarray(HZ, dtype=np.int8) % 2

    from surrogate import lightest_logical
    trials = best["trials"]
    if light_side == "Z":
        wz, zwit = light_w, light_wit
        wx, xwit = lightest_logical(HX, HZ, trials=trials,
                                    seed=best["seed"] + 1)
        wx, xwit = int(wx), [int(q) for q in xwit]
    else:
        wx, xwit = light_w, light_wit
        wz, zwit = lightest_logical(HZ, HX, trials=trials,
                                    seed=best["seed"] + 1)
        wz, zwit = int(wz), [int(q) for q in zwit]
    dval = min(wx, wz)
    print(f"packaging witnesses: X<={wx} Z<={wz} -> d<={dval}", flush=True)

    doc = make_submission(
        HX, HZ,
        name=f"[[544,18,{dval}]] affine elite-neighborhood of the q17 "
             f"[[544,18,84]] elite (EN-2 b3 winner), deep-read",
        construction="Kasai affine 2BGA on Aff(F_17) (Z_17 x| Z_16, primitive "
                     "root 3 acting): a=[245,84,96,270,163,268], "
                     "b=[245,252,47,59,143,70] (b[3] 231->59, a single "
                     "coordinate move of the [[544,18,84]] elite). Screen "
                     f"read d<=96 at 400 trials; this claim is the lightest "
                     f"fresh-seed 20,000-trial RIS reading ({lightest}); "
                     "upper bound.",
        authors=[AUTHOR], family="generalized-bicycle",
        confidence="upper_bound", trials=trials,
        witnesses=(wx, xwit, wz, zwit),
        notes="Deep read of the EN-2 screen winner (screen-cache index 290, "
              "research/campaigns/affine-elite-nbhd-544-18-84); fresh seeds "
              "930001-930003 at 20,000 trials/side each.")
    path = unique_path(
        os.path.join(staging_dir(), f"544-18-{dval}.json"), doc)
    save_submission(doc, path,
                    spec={"constructor": "bbga_labels.build_2bga_affine",
                          "params": {"q": Q, "a": A, "b": B}})
    print(f"staged -> {path}", flush=True)
    verdict, vpath = gate_and_record(path)
    print(json.dumps({"passed": verdict.get("passed"),
                      "labels": verdict.get("labels"),
                      "board_advancing": verdict.get("novelty", {}).get(
                          "board_advancing"),
                      "verdict": str(vpath)}, indent=1), flush=True)
    return 0 if verdict.get("passed") else 3


if __name__ == "__main__":
    sys.exit(main())
