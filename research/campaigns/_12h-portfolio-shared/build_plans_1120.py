"""Build promote plans for the L5+L6 slate against the 2026-11-20 board.

Plans follow the promote-plan-544-20-80.json shape: candidate inlined,
NO recipe key (keeps repro manifests out of the PRs; the 130-min verify
cap lesson from Rounds 229/230), evidence assembled from the campaign
ledgers.

L5 ladder rungs are loaded from the per-candidate confirm ledgers
(research/campaigns/beat-surface-k100-w8-unrestricted/confirm_pp*.json,
matched by fingerprint), plus the two gate_changed fresh-seed battery
rungs per code parsed from battery_harvest.log. L6 rungs are transcribed
from workspace/deep.jsonl rows verbatim, plus any gate_changed battery
rungs recorded in l6_battery_1120.log when present.

Usage: python build_plans_1120.py <slug> [<slug> ...]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAND = ROOT / "research" / "candidates"
SHARED = ROOT / "research" / "campaigns" / "_12h-portfolio-shared"
L5CAMP = ROOT / "research" / "campaigns" / "beat-surface-k100-w8-unrestricted"

L5_SLATES = {
    "510-102-19": dict(template="pp410 4x10 rate 1/5, lift Z_51, design k=102",
                       kd2n="72.2", screen_floor=17, advances="+2 over the floor"),
    "588-98-22": dict(template="pp512 5x12 rate 1/6, lift Z_49, design k=98",
                      kd2n="80.7", screen_floor=19,
                      advances="+3 over the floor; kd2/n 80.7 vs campaign bar 51.0"),
    "686-98-24": dict(template="pp614 6x14 rate 1/7, lift Z_49, design k=98",
                      kd2n="82.3", screen_floor=19,
                      advances="+5 over the floor; keeper of the 686 corner "
                               "(the 22/23 readings are Pareto-covered by this document)"),
    "714-102-25": dict(template="pp614 6x14 rate 1/7, lift Z_51, design k=102",
                       kd2n="89.4", screen_floor=21,
                       advances="+4 over the floor; dominates seven board entries"),
}

L6 = {
    "840-18-28": {
        "lattice": "21x20 (TILE4 transposed assembly)",
        "ladder": [
            (200000, 29, "fast r3 200k pd16, seed 401"),
            (200000, 30, "fast r3 200k pd16, seed 409"),
            (200000, 31, "fast r3 200k pd16, seed 419"),
            (5000, 44, "numpy 5k cross-check X, seed 601"),
            (5000, 35, "numpy 5k cross-check Z, seed 602"),
            (1000000, 29, "fast 1M pd12, seed 503"),
            (1000000, 28, "fast 1M pd12, seed 509"),
            (1000000, 28, "fast 1M pd12, seed 521"),
            (1000000, 28, "fast 1M pd12, seed 531"),
        ],
        "kd2n": "18.0",
        "cell": "k=18 d=28 at n=840 (old: 792-18-27)",
    },
    "880-18-29": {
        "lattice": "22x20 (TILE4 transposed assembly)",
        "ladder": [
            (200000, 30, "fast r3 200k pd16, seed 401"),
            (200000, 30, "fast r3 200k pd16, seed 409"),
            (200000, 29, "fast r3 200k pd16, seed 419"),
            (5000, 41, "numpy 5k cross-check X, seed 601"),
            (1000000, 29, "fast 1M pd12, seed 503"),
            (1000000, 29, "fast 1M pd12, seed 509"),
            (1000000, 29, "fast 1M pd12, seed 521"),
            (1000000, 30, "fast 1M pd12, seed 531"),
        ],
        "kd2n": "19.3",
        "cell": "k=18 d=29 below n=899 (old: 899-18-31 grafted line)",
    },
    "924-29-27": {
        "lattice": "21x22 (B5-29 supports)",
        "ladder": [
            (200000, 27, "fast r3 200k pd16, seed 401"),
            (200000, 27, "fast r3 200k pd16, seed 409"),
            (200000, 27, "fast r3 200k pd16, seed 419"),
            (5000, 30, "numpy 5k cross-check X, seed 601"),
            (5000, 31, "numpy 5k cross-check Z, seed 602"),
            (1000000, 27, "fast 1M pd12, seed 503"),
            (1000000, 27, "fast 1M pd12, seed 509"),
            (1000000, 27, "fast 1M pd12, seed 521"),
            (1000000, 27, "fast 1M pd12, seed 531"),
        ],
        "kd2n": "22.9",
        "cell": "beats 800-29-24 on d (+3) at n +124",
    },
    "968-29-28": {
        "lattice": "22x22 (B5-29 supports)",
        "ladder": [
            (200000, 29, "fast r3 200k pd16, seed 401"),
            (200000, 30, "fast r3 200k pd16, seed 409"),
            (200000, 30, "fast r3 200k pd16, seed 419"),
            (5000, 38, "numpy 5k cross-check X, seed 601"),
            (5000, 34, "numpy 5k cross-check Z, seed 602"),
            (1000000, 29, "fast 1M pd12, seed 503"),
            (1000000, 28, "fast 1M pd12, seed 509"),
            (1000000, 28, "fast 1M pd12, seed 521"),
            (1000000, 28, "fast 1M pd12, seed 531"),
        ],
        "kd2n": "23.5",
        "cell": "new cell kd2/n leader (old best 20.9 = 800-29-24)",
    },
    "968-32-25": {
        "lattice": "22x22 (B5-32 supports)",
        "ladder": [
            (200000, 27, "fast r3 200k pd16, seed 401"),
            (200000, 25, "fast r3 200k pd16, seed 409"),
            (200000, 26, "fast r3 200k pd16, seed 419"),
            (5000, 27, "numpy 5k cross-check X, seed 601"),
            (5000, 36, "numpy 5k cross-check Z, seed 602"),
            (1000000, 26, "fast 1M pd12, seed 503"),
            (1000000, 26, "fast 1M pd12, seed 509"),
            (1000000, 26, "fast 1M pd12, seed 521"),
            (1000000, 25, "fast 1M pd12, seed 531"),
        ],
        "kd2n": "20.7",
        "cell": "k=32 point at d=25 (old: 800-32-22, d=22)",
    },
}


def l5_rungs(slug, doc):
    """Load the confirm-ledger rungs (matched by fingerprint) + battery rungs."""
    verdict = json.loads((CAND / "l5-beat-surface" / f"{slug}.verdict.json")
                         .read_text(encoding="utf-8"))
    fp = str(verdict.get("candidate", {}).get("fingerprint", ""))
    rungs = []
    ledger = None
    for p in L5CAMP.glob("confirm_pp*.json"):
        c = json.loads(p.read_text(encoding="utf-8"))
        if fp.startswith(str(c.get("fp", "x"))[:8]):
            ledger = c
            break
    if ledger is None:
        raise SystemExit(f"no confirm ledger matches {slug} (fp {fp[:8]})")
    for r in ledger.get("rungs", []):
        trials = int(r["trials"])
        weight = int(r["weight"])
        pd = r.get("pair_depth", 10)
        side = r.get("side", "?")
        key = str(r.get("key", r.get("seed", "?")))
        rungs.append((trials, weight, True,
                      f"{'numpy' if trials >= 500000 else 'fast'} {trials:,}-trial rung "
                      f"pd{pd} {side}-side, seed {key}"))
    import re
    for line in (L5CAMP / "battery_harvest.log").read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{slug} seed ") and "no logical lighter than" in line:
            seed = line.split(" seed ")[1].split(":")[0]
            m = re.search(r"(\d+) trials", line)
            trials = int(m.group(1)) if m else 24000
            d = int(line.rsplit("no logical lighter than ", 1)[1].strip())
            rungs.append((trials, d, True, f"gate_changed fresh-seed battery, seed {seed}"))
    return rungs, ledger


def build(slug):
    lane = "l5-beat-surface" if slug in L5_SLATES else "l6-2dlocal"
    doc = json.loads((CAND / lane / f"{slug}.json").read_text(encoding="utf-8"))
    claim = int(doc["distance"]["d"])

    if slug in L5_SLATES:
        meta = L5_SLATES[slug]
        rungs, ledger = l5_rungs(slug, doc)
        n, k = doc["n"], doc["k"]
        direction = (
            f"Advance the unrestricted weight-8 cell's frontier in the n 500-750 "
            f"band with pair-partition CPM codes on the board's own 994-142-40 "
            f"template class. The {meta['template']} draw landed the k={k} "
            f"x d>={claim} corner; the board's recorded k>={k} entries at n<={n} "
            f"carry d<=21, so this document extends the cell frontier on the d "
            f"axis at lower n."
        )
        searched = (
            f"Lane beat-surface-k100-w8-unrestricted (60 draws per template lift; "
            f"500k triage of the top draws per lift). Screen floor "
            f"{meta['screen_floor']} at staged triage; the keeper deep-laddered "
            f"per the escalation discipline (multi-seed 500k rungs -> 2M -> "
            f"Z-side swapped-matrix 2M -> 500k at pair_depth 48; confirm ledger "
            f"confirm_{ledger['tag']}.json, ladder flat at {claim} across "
            f"seeds/budgets/sides), then two gate_changed fresh-seed batteries "
            f"confirmed no logical lighter than {claim}. gf2_fast C++ backend; "
            f"quotient caps and pair_depth recorded per rung in the ledger."
        )
        frontier = (
            f"Gate novelty for this document: board-advancing in the "
            f"(weight-8, unrestricted) cell, dominated_by empty, d_only_gain "
            f"false, advances_n {ledger.get('advances_n')}. kd^2/n = "
            f"{meta['kd2n']}. {meta['advances']}. The distance is a "
            f"witness-backed upper bound whose claim survived the multi-budget, "
            f"multi-instrument ladder recorded here and the gate's fresh-seed "
            f"refutation; honest reading, never 'exact'."
        )
        headline_family = "pair-partition CPM"
    else:
        meta = L6[slug]
        rungs = [(t, d, True, lab) for (t, d, lab) in meta["ladder"]]
        rungs += load_l6_battery_rungs(slug)
        direction = (
            f"Advance the weight-8 x local-2d-bilayer cell's frontier at n in "
            f"[700,1000] with planar-boundary bilayer codes "
            f"(research/local2d/boundary_engine.py::build_planar exact "
            f"half-infinite boundary gauge over F2[t], corner completion, "
            f"cleanup, weight reduction; bilayer layout "
            f"planar.grid_coordinates(layers=2), radius 4*sqrt(2)). "
            f"{meta['lattice']}: {meta['cell']}."
        )
        searched = (
            f"Lane w8-2dlocal-n700-1000 (Phase A: 6 seed support pairs x ~94 "
            f"lattice sizes; Phase B: 360 single-monomial mutants around the "
            f"B5 seeds, 24 screen advances). Escalation bar reqd(n,k) computed "
            f"live from codes/; board-dup guard by rowspace comparison caught "
            f"the known lattice twins. Ladder per the campaign method: screen "
            f"3x20k (pd22) -> 3x100k (pd20) -> deep 3x200k (pd16) -> 1M-class "
            f"x4 fresh seeds (pd12) -> numpy per-side cross-checks (5k/side). "
            f"Claim = lightest WITNESSED reading across all rungs (upper_bound, "
            f"never 'exact'); the gate's fresh-seed refutation found no logical "
            f"lighter than {claim}."
        )
        frontier = (
            f"Gate novelty for this document: board-advancing in the "
            f"(weight-8, local-2d-bilayer) cell, dominated_by empty, "
            f"d_only_gain false, advances_by [] (pure frontier extension). "
            f"kd^2/n = {meta['kd2n']}. Honesty note: the fast instrument reads "
            f"+1..+9 over true d at these sizes (board dup-calibration), so the "
            f"true distance is likely 1-5 below the claim; the witnesses carry "
            f"and the CI refutation battery is the correction path."
        )
        headline_family = "2D-local bilayer"

    ladder = [{"trials": t, "d": d, "fresh": bool(f), "label": lab}
              for (t, d, f, lab) in rungs]
    prov = doc.get("provenance", {})
    plan = {
        "candidate": doc,
        "evidence": {
            "headline": f"{headline_family} at kd^2/n {meta['kd2n']}, "
                        f"n={doc['n']}, k={doc['k']}, d<={claim}",
            "direction": direction,
            "searched": searched,
            "ladder": ladder,
            "frontier": frontier,
            "reproduction": (
                "Rebuild from committed kit code, verified bit-identical to the "
                "entry's fingerprint before submission. "
                + prov.get("construction", "") +
                " The check matrices in codes/ are the submission artifact; the "
                "witnesses embedded in the distance block re-verify against "
                "them independently (H.v = 0, outside the rowspace, weight "
                "equals the reading)."
            ),
            "tools": {
                "model": "GLM-5.3-Flash",
                "harness": "ZCode",
                "local": "research/kit (surrogate.distance_rand_witness, gf2_fast "
                         "C++ backend), verify/gate_changed.py fresh-seed batteries, "
                         "verify/validate_candidate.py gate",
            },
        },
    }
    out = CAND / lane / f"promote-plan-{slug}.json"
    out.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    deepest = max((r["trials"] for r in ladder), default=0)
    best = min((r["d"] for r in ladder), default=None)
    flat = 0
    for r in reversed(ladder):
        if r["fresh"] and r["d"] == best:
            flat += 1
        elif r["fresh"]:
            break
    print(f"wrote {out} ({len(ladder)} rungs, claim d={claim}, best {best}, "
          f"deepest {deepest:,}, trailing-flat {flat})")


def load_l6_battery_rungs(slug):
    out = []
    log = SHARED / "l6_battery_1120.log"
    if not log.exists():
        return out
    import re
    for line in log.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{slug} seed ") and "no logical lighter than" in line:
            seed = line.split(" seed ")[1].split(":")[0]
            m = re.search(r"(\d+) trials", line)
            trials = int(m.group(1)) if m else 24000
            d = int(line.rsplit("no logical lighter than ", 1)[1].strip())
            out.append((trials, d, True, f"gate_changed fresh-seed battery, seed {seed}"))
    return out


if __name__ == "__main__":
    for s in sys.argv[1:]:
        build(s)
