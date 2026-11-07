"""Stage draw 53244 as [[544,20,87]] per coordinator authorization (b-modified).

Claim d <= 87 (upper bound at the lightest reading). Evidence: 20 fresh-seed
rungs at 20,000 trials/side, floor 87 reproduced at rung seeds 911006 & 911008
(both X-side, both supports embedded/sidecar); Z bound 88 at seed 911012;
sibling draw 74545 (distinct a,b, same WL signature class) corroborates the
floor at 87 on its Z side (seeds 911005 & 911006). Staging through the kit
path: make_submission -> save_submission with rebuild spec, under
QLDPC_RUN_ID=l2-q17-resume. promote.py is NOT run (it writes codes/).
"""
import json
import os
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["QLDPC_RUN_ID"] = "l2-q17-resume"

import analyze_resume as ar  # noqa: E402
from bbga_labels import build_2bga_affine  # noqa: E402
from coordination import staging_dir, unique_path  # noqa: E402
from css import compute_k  # noqa: E402
from submit import make_submission, save_submission  # noqa: E402
from group_algebra import metacyclic  # noqa: E402

DRAW = 53244
SIBLING = 74545
CLAIM = 87
R = 20_000

# pool meta (a, b, w, d400)
pool = {}
with open(os.path.join(_HERE, "pool_draws.jsonl"), encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["i"] in (DRAW, SIBLING):
            pool[r["i"]] = r
screened = {}
with open(os.path.join(_HERE, "screened_draws.jsonl"), encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["i"] in (DRAW, SIBLING):
            screened[r["i"]] = r

rungs, meta = ar.rung_readings(os.path.join(_HERE, "deep_subjobs.jsonl"))
by_seed = rungs[DRAW]
readings = {s: min(v["X"][0], v["Z"][0]) for s, v in sorted(by_seed.items())
            if "X" in v and "Z" in v}
floor = min(readings.values())
assert floor == CLAIM, f"floor moved: {floor}"
hits = [s for s, v in readings.items() if v == CLAIM]
assert len(hits) >= 2, hits

# X-side: lightest over all rungs; the two floor witnesses are both X-side
x_hits = sorted((by_seed[s]["X"][0], s) for s in hits)
wx, x_seed1 = x_hits[0]
xwit1 = by_seed[x_seed1]["X"][1]
x_seed2 = x_hits[1][1]
xwit2 = by_seed[x_seed2]["X"][1]
assert wx == CLAIM
# Z-side lightest (complete rungs only)
wz, z_seed = min((by_seed[s]["Z"][0], s) for s in by_seed
                 if "X" in by_seed[s] and "Z" in by_seed[s])
zwit = by_seed[z_seed]["Z"][1]
print(f"per-side: X<={wx} (witnesses at seeds {x_seed1},{x_seed2}), "
      f"Z<={wz} (witness seed {z_seed}); rungs={len(readings)}")

a, b = pool[DRAW]["a"], pool[DRAW]["b"]
HX, HZ = build_2bga_affine(17, a, b)
k = compute_k(HX, HZ)
n = int(HX.shape[1])
assert (n, k) == (544, 20), (n, k)
d = min(wx, wz)
assert d == CLAIM

ladder = ", ".join(f"{s}:{readings[s]}" for s in sorted(readings))
seed_w = len(a)
check_w = len(a) + len(b)
AUTHOR = "@Ming-yuan-Liang"

doc = make_submission(
    HX, HZ,
    name=f"[[{n},{k},{d}]] Kasai affine 2BGA Aff(F_17)",
    construction=(
        "Kasai affine 2BGA: two-block group-algebra code over the affine "
        "group Aff(F_17) in its metacyclic realization Z_17 x| Z_16 (order "
        "272; primitive root 3 acting). With research/kit/group_algebra.py: "
        f"mul, _ = metacyclic(17, 16, 3), then HX, HZ = build_2bga(mul, a, b) "
        f"for a = {a} and b = {b} (|a| = |b| = {seed_w}, check weight "
        f"{check_w}; a uniform random draw of the q17-k18 lane, pool index "
        f"{DRAW})."),
    authors=[AUTHOR],
    family="generalized-bicycle",
    confidence="upper_bound",
    trials=R, seed=x_seed1,
    witnesses=(wx, xwit1, wz, zwit),
    notes=(
        f"Lane q17-k18 (parallel-q17-k18-1106 campaign, resume 2026-11-06). "
        f"Distance is an upper bound at the lightest reading: {len(readings)} "
        f"fresh-seed rungs at {R:,} trials/side each (numpy RIS, "
        f"lightest_logical, pair_depth 10), chronological readings "
        f"[{ladder}]. The floor {CLAIM} is reproduced by two independent "
        f"rung seeds ({x_seed1}, {x_seed2}), both X-side; the second "
        f"weight-{CLAIM} witness is carried beside this file in "
        f"<slug>.evidence.json and in the campaign checkpoint "
        f"deep_subjobs.jsonl. No rung of {len(readings)} ever read below "
        f"{CLAIM}. A sibling draw from the same lane screen (pool index "
        f"{SIBLING}, distinct exponent sets, identical Weisfeiler-Leman "
        f"signature class a76c1ee56001cd1d) independently reproduces the "
        f"{CLAIM} floor on its Z side at rung seeds 911005 and 911006. "
        f"Screen reading was d400={screened[DRAW]['d400']} (400 trials), the "
        f"usual inflation above the deep floor. A 1,000,000-trial-per-side "
        f"rung is pending (supervisor-owned); per the +5 offset(1M) "
        f"calibration on this family the expected 1M reading is 84-87, and "
        f"the entry repackages at the lightest reading per playbook. Staged "
        f"for review; not a submission."))

import datetime  # noqa: E402
prov = {"found_by": [AUTHOR], "date": datetime.date.today().isoformat(),
        "found_at_samples": R, "survived_samples": R,
        "tool": "research/kit/surrogate.lightest_logical"}
doc["distance"]["X"]["witness_provenance"] = dict(
    prov, seeds=[int(x_seed1), int(x_seed2)])
doc["distance"]["Z"]["witness_provenance"] = dict(prov, seeds=[int(z_seed)])

path = unique_path(
    os.path.join(staging_dir(), f"{n}-{k}-{d}.json"), doc)
save_submission(doc, path,
                spec={"constructor": "bbga_labels.build_2bga_affine",
                      "params": {"q": 17, "a": list(a), "b": list(b)}})
print("staged ->", path)

# sidecar evidence: full ladder + both floor witnesses + sibling corroboration
sib_rungs = {s: min(v["X"][0], v["Z"][0]) for s, v in sorted(rungs[SIBLING].items())
             if "X" in v and "Z" in v}
evidence = {
    "candidate": os.path.basename(path),
    "claim": {"n": n, "k": k, "d_upper_bound": d},
    "trials_per_side_per_rung": R,
    "instrument": "research/kit/surrogate.lightest_logical (numpy RIS, pair_depth 10)",
    "ladder": [{"rung_seed": s, "reading": readings[s],
                "x_weight": by_seed[s]["X"][0], "z_weight": by_seed[s]["Z"][0]}
               for s in sorted(readings)],
    "floor_witnesses": [
        {"side": "X", "rung_seed": x_seed1, "weight": wx, "support": xwit1},
        {"side": "X", "rung_seed": x_seed2, "weight": wx, "support": xwit2},
        {"side": "Z", "rung_seed": z_seed, "weight": wz, "support": zwit},
    ],
    "sibling_corroboration": {
        "pool_index": SIBLING, "a": pool[SIBLING]["a"], "b": pool[SIBLING]["b"],
        "wl_signature": "a76c1ee56001cd1d", "same_class": True,
        "rungs": sib_rungs,
        "floor_seeds": [911005, 911006], "floor": CLAIM,
        "floor_supports": [
            {"side": "Z", "rung_seed": 911005,
             "support": rungs[SIBLING][911005]["Z"][1]},
            {"side": "Z", "rung_seed": 911006,
             "support": rungs[SIBLING][911006]["Z"][1]},
        ],
    },
    "checkpoint": "research/campaigns/parallel-q17-k18-1106/deep_subjobs.jsonl",
}
sidecar = path.replace(".json", ".evidence.json")
with open(sidecar, "w", encoding="utf-8", newline="\n") as f:
    json.dump(evidence, f, indent=1)
print("evidence sidecar ->", sidecar)
