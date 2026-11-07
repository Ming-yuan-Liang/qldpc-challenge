"""Lane q17-k18, stage D: analyze deep rungs, stage flat survivors.

Flat rule (strict, per the lane): a draw moves on iff all its fresh-seed
rungs (>= 3, each `--trials` trials/side) return the same reading
R = min(wx, wz). Per-side claims are the per-side minima across the flat
rungs, each with the witness that set it. Staging goes through the kit path:
make_submission -> save_submission (with the rebuild spec) at
coordination.unique_path(staging_dir()/<n>-<k>-<d>.json, doc); the gate is run
separately as `uv run --no-sync python research/kit/coordination.py gate`.

Usage:
  python analyze_and_stage.py --rungs deep_rungs.jsonl --trials 20000 \
      [--threshold-json thresholds.json] [--stage] [--dry-run]
"""
import argparse
import json
import os
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np  # noqa: E402

AUTHOR = "@Ming-yuan-Liang"

# d a [[544, K, W]] must exceed to be potentially board-advancing under the
# committed board (from board_landscape.py; 544-18-82 w=12 and 514-32-70 w=16
# are the strongest dominators). k is always even for this family:
# rank(HX) == rank(HZ), so k = 544 - 2*rank(HX).
THRESHOLD = {16: 82, 18: 82, 20: 70, 22: 70}


def group_rungs(path):
    """Group the deep_subjobs.jsonl records into per-draw rungs.

    One rung = (i, rung_seed): its X weight is the lightest valid sub-search
    weight over that (i, X, rung_seed) group, with the witness that set it;
    same for Z. A rung is complete when at least one valid sub-search exists
    on each side and every sub-search of the rung has been run (the caller
    knows the expected sub count from the records' sub_trials).
    """
    subs = defaultdict(list)
    meta = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            meta[r["i"]] = {"a": r["a"], "b": r["b"], "w": r.get("w"),
                            "k": r.get("k")}
            subs[(r["i"], r["rung_seed"], r["side"])].append(r)
    rungs = defaultdict(list)
    for (i, seed, side), rs in subs.items():
        valid = [r for r in rs if r.get("valid") and r.get("weight") is not None]
        best = min(valid, key=lambda r: r["weight"]) if valid else None
        rungs[i].append({
            "seed": seed, "side": side,
            "weight": best["weight"] if best else None,
            "support": best["support"] if best else [],
            "n_subs": len(rs),
            "sub_weights": sorted(r["weight"] for r in valid),
        })
    return rungs, meta


def analyze(rungs, meta, trials, expected_subs=4):
    out = []
    for i, rs in sorted(rungs.items()):
        by_seed = defaultdict(dict)
        for r in rs:
            if r["weight"] is None:
                continue
            if expected_subs and r.get("n_subs", 0) != expected_subs:
                continue          # rung-side incomplete; not stageable evidence
            by_seed[r["seed"]][r["side"]] = (r["weight"], r["support"])
        full = {s: v for s, v in by_seed.items()
                if "X" in v and "Z" in v}
        readings = {}
        for s, v in sorted(full.items()):
            readings[s] = min(v["X"][0], v["Z"][0])
        rec = {"i": i, "a": meta[i]["a"], "b": meta[i]["b"],
               "w": meta[i]["w"], "k": meta[i].get("k"),
               "rung_readings": readings, "n_rungs": len(readings),
               "rung_detail": rs}
        vals = list(readings.values())
        rec["flat"] = len(vals) >= 3 and len(set(vals)) == 1
        if vals:
            rec["R"] = min(vals)
            rec["honest_upper"] = min(vals)
        if rec["flat"]:
            R = vals[0]
            flat_seeds = [s for s, v in readings.items() if v == R]
            wx = min(full[s]["X"][0] for s in flat_seeds)
            wz = min(full[s]["Z"][0] for s in flat_seeds)
            xseed = next(s for s in flat_seeds if full[s]["X"][0] == wx)
            zseed = next(s for s in flat_seeds if full[s]["Z"][0] == wz)
            rec["wx"], rec["wz"] = wx, wz
            rec["xwit"] = full[xseed]["X"][1]
            rec["zwit"] = full[zseed]["Z"][1]
            rec["xseed"], rec["zseed"] = xseed, zseed
            rec["flat_seeds"] = flat_seeds
            rec["threshold"] = THRESHOLD.get(meta[i].get("k") or 0, None)
        out.append(rec)
    return out


def rec_min_k(meta, i):
    # k is not carried in the rung records; recover from the draw pool file is
    # the caller's job. Here we accept the analysis caller passing k via meta.
    return meta[i].get("k", 0)


def stage(rec, trials, staging_env):
    """Package one flat survivor through the kit path; returns (path, doc)."""
    from bbga_labels import build_2bga_affine
    from coordination import staging_dir, unique_path
    from css import compute_k
    from submit import make_submission, save_submission

    a, b = rec["a"], rec["b"]
    HX, HZ = build_2bga_affine(17, a, b)
    k = compute_k(HX, HZ)
    n = int(HX.shape[1])
    d = min(rec["wx"], rec["wz"])
    seed_w = len(a)                     # |a| = |b| throughout this lane
    check_w = len(a) + len(b)           # row weight of HX = |a| + |b|
    seeds_txt = ", ".join(str(s) for s in sorted(rec["flat_seeds"]))
    doc = make_submission(
        HX, HZ,
        name=f"[[{n},{k},{d}]] Kasai affine 2BGA Aff(F_17)",
        construction=(
            "Kasai affine 2BGA: two-block group-algebra code over the affine "
            "group Aff(F_17) in its metacyclic realization Z_17 x| Z_16 "
            "(order 272; primitive root 3 acting). With "
            "research/kit/group_algebra.py: mul, _ = metacyclic(17, 16, 3), "
            f"then HX, HZ = build_2bga(mul, a, b) for a = {a} and b = {b} "
            f"(|a| = |b| = {seed_w}, check weight {check_w}, a uniform random "
            "draw of the q17-k18 lane). "
            f"Distance is a fresh-seed 20,000-trial-per-side RIS upper bound: "
            f"{len(rec['flat_seeds'])} rungs (seeds {seeds_txt}) agree flat "
            f"at {rec['R']}."),
        authors=[AUTHOR],
        family="generalized-bicycle",
        confidence="upper_bound",
        trials=trials, seed=sorted(rec["flat_seeds"])[0],
        witnesses=(rec["wx"], rec["xwit"], rec["wz"], rec["zwit"]),
        notes=(f"Lane q17-k18 (parallel-1106 campaign): uniform random seed "
               f"draw, |a|=|b|={seed_w}, k={k}. {len(rec['flat_seeds'])} fresh-seed "
               f"rungs at 20,000 trials/side read flat at {rec['R']} "
               f"(X<={rec['wx']}, Z<={rec['wz']}). Staged for review; not a "
               "submission."))
    # witness provenance: the true rung each embedded witness came from
    import datetime
    prov = {"found_by": [AUTHOR], "date": datetime.date.today().isoformat(),
            "found_at_samples": trials, "survived_samples": trials,
            "tool": "research/kit/surrogate.lightest_logical"}
    doc["distance"]["X"]["witness_provenance"] = dict(prov, seeds=[int(rec["xseed"])])
    doc["distance"]["Z"]["witness_provenance"] = dict(prov, seeds=[int(rec["zseed"])])
    if staging_env:
        os.environ["QLDPC_RUN_ID"] = staging_env
    path = unique_path(
        os.path.join(staging_dir(), f"{n}-{k}-{d}.json"), doc)
    save_submission(doc, path,
                    spec={"constructor": "bbga_labels.build_2bga_affine",
                          "params": {"q": 17, "a": list(a), "b": list(b)}})
    return path, doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", required=True)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--pool", default=None,
                    help="pool JSONL to recover each draw's k and w")
    ap.add_argument("--stage", action="store_true",
                    help="stage flat survivors (default: analysis only)")
    ap.add_argument("--run-id", default="q17-k18-1106")
    ap.add_argument("--out", default=None,
                    help="write the analysis JSON here")
    args = ap.parse_args()

    rungs, meta = group_rungs(args.rungs)
    if args.pool:
        with open(args.pool, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r["i"] in meta:
                    meta[r["i"]]["k"] = r["k"]
                    meta[r["i"]]["w"] = r["w"]

    recs = analyze(rungs, meta, args.trials)
    for rec in recs:
        thr = THRESHOLD.get(rec_min_k(meta, rec["i"]))
        rec["threshold"] = thr
        rec["advancing_if_flat"] = (thr is not None and rec.get("R") is not None
                                    and rec["R"] > thr)
        flat = "FLAT" if rec["flat"] else f"not-flat {sorted(rec['rung_readings'].values())}"
        print(f"i={rec['i']} k={meta[rec['i']].get('k')} w={rec['w']} "
              f"R={rec.get('R')} {flat} thr={thr} "
              f"advancing={rec['advancing_if_flat']}", flush=True)

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(recs, f, indent=1)

    if args.stage:
        for rec in recs:
            if not rec["flat"]:
                continue
            if not rec["advancing_if_flat"]:
                print(f"i={rec['i']}: flat at {rec['R']} but at/below the "
                      f"domination threshold {rec['threshold']}; recorded as "
                      "dominated miss, not staged", flush=True)
                continue
            path, doc = stage(rec, args.trials, args.run_id)
            print(f"i={rec['i']}: staged [[{doc['n']},{doc['k']},{doc['distance']['d']}]] "
                  f"-> {path}", flush=True)


if __name__ == "__main__":
    main()
