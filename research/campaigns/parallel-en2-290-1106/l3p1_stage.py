"""L3 lane PHASE 1 stager: package the EN-2 winner at its honest paired-depth
audited reading, only if the audit supports it.

Inputs (all in this directory):
  - Fresh L3 rungs: l3p1_win_seed830001/2/3.json (+ .progress chunk files)
    for the EN-2 winner (a=[245,84,96,270,163,268], b=[245,252,47,59,143,70]).
  - Prior lane rungs: phase1_witness_seed930001/2/3.json (+ .progress) for the
    same code (the lane's original three 20k rungs, readings 86/84/84).
  - Fresh L3 incumbent rungs: l3p1_inc_seed830011/12/13.json for the board's
    [[544,18,76]] (codes/544-18-76.json) at the same matched budget.

Decision rule (lane brief): the winner's lightest flat reading (fresh seeds,
spread <= FLAT_SPREAD; combined with the prior rungs for the claim value) must
be <= 84 and strictly greater than the incumbent's matched-budget reading for
the d-gain to be real; otherwise record and do not stage.

Witnesses: lightest X-side and Z-side supports across every chunk of every
winner rung (prior + fresh). A side no chunk ever returned is searched fresh
(lightest_logical, 20,000 trials, fresh seed).

Staging: QLDPC_RUN_ID=l3-en2 -> research/candidates/l3-en2/<n>-<k>-<d>.json
via submit.make_submission + save_submission (unique_path). The gate is then
run separately with research/kit/coordination.py gate <path>. Nothing here is
a submission into codes/.
"""
import datetime
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
from coordination import staging_dir, unique_path
from css import compute_k
from submit import make_submission, save_submission
from surrogate import lightest_logical

AUTHOR = "@Ming-yuan-Liang"
FLAT_SPREAD = 2
Q = 17
A = [245, 84, 96, 270, 163, 268]
B = [245, 252, 47, 59, 143, 70]
NEW_SEEDS = [830001, 830002, 830003]
OLD_SEEDS = [930001, 930002, 930003]
INC_SEEDS = [830011, 830012, 830013]
AUDIT_BAR = 84


def load_rung(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def chunk_records(rung):
    prog = rung + ".progress"
    if not os.path.exists(prog):
        return []
    with open(prog, encoding="utf-8") as f:
        return json.load(f)["chunks"]


def main():
    # --- winner rungs (fresh + prior) -------------------------------------
    new_rungs = [load_rung(os.path.join(_HERE, f"l3p1_win_seed{s}.json"))
                 for s in NEW_SEEDS]
    old_rungs = [load_rung(os.path.join(_HERE, f"phase1_witness_seed{s}.json"))
                 for s in OLD_SEEDS]
    inc_rungs = [load_rung(os.path.join(_HERE, f"l3p1_inc_seed{s}.json"))
                 for s in INC_SEEDS]
    missing = ([s for s, r in zip(NEW_SEEDS, new_rungs) if r is None] +
               [s for s, r in zip(OLD_SEEDS, old_rungs) if r is None] +
               [s for s, r in zip(INC_SEEDS, inc_rungs) if r is None])
    if missing:
        print(f"missing rung JSONs: {missing}; aborting (no staging)",
              flush=True)
        return 1

    new_read = [r["weight"] for r in new_rungs]
    old_read = [r["weight"] for r in old_rungs]
    inc_read = [r["weight"] for r in inc_rungs]
    if any(w is None for w in new_read + old_read + inc_read):
        print("a rung found no logical; aborting", flush=True)
        return 1
    new_light, new_spread = min(new_read), max(new_read) - min(new_read)
    all_light = min(new_read + old_read)
    inc_light = min(inc_read)
    inc_spread = max(inc_read) - inc_light
    print(f"winner fresh rungs {dict(zip(NEW_SEEDS, new_read))} "
          f"lightest {new_light} spread {new_spread}", flush=True)
    print(f"winner prior rungs {dict(zip(OLD_SEEDS, old_read))} "
          f"(lane en2-290-1106)", flush=True)
    print(f"incumbent fresh rungs {dict(zip(INC_SEEDS, inc_read))} "
          f"lightest {inc_light} spread {inc_spread} (claim 76)", flush=True)

    audit_ok = (new_spread <= FLAT_SPREAD and new_light <= AUDIT_BAR
                and new_light > inc_light)
    print(f"audit: flat(fresh)={new_spread <= FLAT_SPREAD} "
          f"lightest<={AUDIT_BAR}: {new_light <= AUDIT_BAR} "
          f"d-gain vs incumbent matched reading: {new_light} > {inc_light} "
          f"= {new_light > inc_light} -> {'PROCEED' if audit_ok else 'DO NOT STAGE'}",
          flush=True)
    if not audit_ok:
        return 2

    # --- witnesses: lightest per side across every winner chunk -----------
    all_chunks = []
    for r in new_rungs + old_rungs:
        all_chunks.extend(chunk_records(
            os.path.join(_HERE, f"l3p1_win_seed{r['seed']}.json")
            if r in new_rungs else
            os.path.join(_HERE, f"phase1_witness_seed{r['seed']}.json")))
    total_side_samples = sum(c["trials"] for c in all_chunks)

    HX, HZ = build_2bga_affine(Q, A, B)
    HX = np.asarray(HX, dtype=np.int8) % 2
    HZ = np.asarray(HZ, dtype=np.int8) % 2
    n = HX.shape[1]
    k = compute_k(HX, HZ)
    assert n == 544 and k == 18, (n, k)

    wit, chunk_meta, fresh = {}, {}, {}
    for side in ("X", "Z"):
        best = None
        for c in all_chunks:
            if (c["side"] == side and c["weight"] is not None
                    and c["support"]):
                if best is None or c["weight"] < best["weight"]:
                    best = c
        if best is not None:
            wit[side] = (best["weight"], best["support"])
            chunk_meta[side] = best
    for side in ("X", "Z"):
        if side not in wit:
            w, sup = lightest_logical(
                HX, HZ, trials=20000, seed=51000 + (1 if side == "Z" else 0))
            wit[side] = (int(w), [int(x) for x in sup])
            fresh[side] = True
            print(f"no chunk witness on {side}; fresh search read {side}<={w}",
                  flush=True)
    wx, xwit = wit["X"]
    wz, zwit = wit["Z"]
    dval = min(wx, wz)
    claim = min(dval, all_light)  # claim never above the lightest rung reading
    print(f"winner witnesses X<={wx} Z<={wz}; rung lightest {all_light}; "
          f"claim d<={claim}", flush=True)
    if claim < dval:
        # A rung read lighter than every witness we hold: re-derive d from the
        # lightest witness pair and keep the claim at the rung reading by
        # refusing to overclaim -- the doc needs a witness at its d value.
        print(f"NOTE: lightest rung reading {all_light} < min witness side "
              f"{dval}; packaging at witness pair d={dval} would overclaim. "
              f"Packaging at d={claim} requires a witness at {claim}.",
              flush=True)
        print("ABORT: no witness at the lightest reading; keep the witness "
              "JSONs and repackage with the lightest support embedded.",
              flush=True)
        return 3

    doc = make_submission(
        HX, HZ,
        name=f"[[{n},{k},{claim}]] Kasai affine 2BGA Aff(F_{Q}) "
             f"(EN-2 winner, b3 single-coordinate move of the [[544,18,84]] "
             f"q17 elite)",
        construction=f"2BGA on the metacyclic realization of Aff(F_{Q}) "
                     f"(Z_{Q} x| Z_{{16}}, primitive root 3 acting; Kasai's "
                     f"affine-coset structure): a={A}, b={B} (b[3] 231->59 "
                     f"move). Distance is the lightest of six fresh-seed "
                     f"20,000-trial RIS upper-bound readings (seeds "
                     f"{OLD_SEEDS} lane en2-290-1106; {NEW_SEEDS} lane l3-en2 "
                     f"paired-depth audit), spent as 4,000-trial checkpoint "
                     f"chunks; upper bound.",
        authors=[AUTHOR], family="generalized-bicycle",
        confidence="upper_bound", trials=4000,
        witnesses=(wx, xwit, wz, zwit),
        notes="EN-2 winner (screen-cache idx 290 of the affine-elite-nbhd "
              "544-18-84 lane; screen claim 96 collapsed to an honest 84). "
              "Paired-depth audit vs board peer codes/544-18-76.json at "
              "matched budget (3 fresh seeds x 20,000 trials/side, numpy "
              "distance_rand_witness, pair_depth 10): incumbent readings "
              f"{inc_read}, winner readings {new_read + old_read}. Campaign "
              "research/campaigns/parallel-en2-290-1106/ (lane l3-en2).")
    # Honest per-side witness provenance for chunk-sourced witnesses.
    for side in ("X", "Z"):
        if side in fresh:
            continue
        c = chunk_meta[side]
        doc["distance"][side]["witness_provenance"] = {
            "found_by": [AUTHOR],
            "date": datetime.date.today().isoformat(),
            "found_at_samples": int(c["trials"]),
            "survived_samples": int(total_side_samples),
            "tool": "research/kit/surrogate.distance_rand_witness",
            "seeds": [int(c["chunk_seed"])],
        }

    os.environ.setdefault("QLDPC_RUN_ID", "l3-en2")
    path = unique_path(
        os.path.join(staging_dir(), f"{n}-{k}-{claim}.json"), doc)
    save_submission(doc, path,
                    spec={"constructor": "bbga_labels.build_2bga_affine",
                          "params": {"q": Q, "a": A, "b": B}})
    print(f"staged -> {path}", flush=True)
    with open(os.path.join(_HERE, "l3p1_staged_path.txt"), "w",
              encoding="utf-8") as f:
        f.write(path + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
