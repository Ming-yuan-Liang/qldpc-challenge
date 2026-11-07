"""Resume-stage analyzer for lane q17-k18 (session of 2026-11-06, resume).

Operative rule (lane task, 2026-11-06): a draw is stage-worthy iff >= 3
completed fresh-seed rungs (each 20,000 trials/side, distinct rung seeds)
read exactly R, where R is the lightest rung reading over ALL completed
rungs of the draw. A rung reading is min over sides of the side's lightest
valid sub-search weight (4 sub-searches of 5,000 trials per side). No rung
can read below R by definition, so the claim "d <= R" (upper bound at the
lightest reading) is certified by >= 3 independent reproductions of R.

This deliberately replaces the strict all-rungs-equal check in
analyze_and_stage.analyze for draws whose already-recorded rungs disagree:
once two rungs differ the strict check is unsatisfiable no matter how many
further rungs are run, while the operative rule still requires independent
reproduction of the claimed reading. Deviation is recorded in REPORT.md.

Thresholds updated for the 2026-11-06 board move (board_landscape.py over
the committed board, [[544,18,76]] w=12 merged): k in {16, 18} need d > 76;
k in {19..22} need d > 70 (dominator [[514,32,70]] w=16).

Usage:
  uv run --no-sync python analyze_resume.py --rungs deep_subjobs.jsonl \
      --pool pool_draws.jsonl [--stage] [--run-id l2-q17-resume] [--out out.json]
"""
import argparse
import json
import os
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_HERE,)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import analyze_and_stage as base  # noqa: E402  (reuses group_rungs + stage)

# Board moved 2026-11-06: [[544,18,76]] merged, so k=16/18 need d > 76 now.
THRESHOLD = {16: 76, 18: 76, 20: 70, 22: 70}


def rung_readings(path, expected_subs=4):
    """Per-draw: {rung_seed: reading} over complete rungs + per-side detail.

    Sub-search records are deduped by (i, side, rung_seed, sub_idx) keeping
    the lightest weight (a restarted driver can append a repeat; the lightest
    valid result is the truth). A rung side is complete iff its 4 distinct
    sub_idx are all present; a rung is complete iff both sides are.
    """
    subs = defaultdict(dict)   # (i, seed, side) -> {sub_idx: rec}
    meta = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            meta[r["i"]] = {"a": r["a"], "b": r["b"], "k": r.get("k"),
                            "w": r.get("w")}
            key = (r["i"], r["rung_seed"], r["side"])
            cur = subs[key].get(r["sub_idx"])
            if cur is None or (r.get("valid") and r.get("weight") is not None
                               and (not cur.get("valid")
                                    or r["weight"] < cur["weight"])):
                subs[key][r["sub_idx"]] = r
    out = defaultdict(dict)    # i -> seed -> {"X": (w, sup), "Z": (w, sup)}
    for (i, seed, side), by_idx in subs.items():
        if len(by_idx) != expected_subs:
            continue           # side incomplete; not evidence
        valid = [r for r in by_idx.values()
                 if r.get("valid") and r.get("weight") is not None]
        if not valid:
            continue
        best = min(valid, key=lambda r: r["weight"])
        out[i].setdefault(seed, {})[side] = (int(best["weight"]),
                                             best.get("support") or [])
    return out, meta


def analyze(path):
    rungs, meta = rung_readings(path)
    recs = []
    for i, by_seed in sorted(rungs.items()):
        complete = {s: v for s, v in by_seed.items() if "X" in v and "Z" in v}
        readings = {s: min(v["X"][0], v["Z"][0]) for s, v in complete.items()}
        rec = {"i": i, "a": meta[i]["a"], "b": meta[i]["b"],
               "w": meta[i].get("w"), "k": meta[i].get("k"),
               "rung_readings": {str(s): readings[s] for s in sorted(readings)},
               "n_complete_rungs": len(readings)}
        thr = THRESHOLD.get(meta[i].get("k") or 0)
        rec["threshold"] = thr
        if readings:
            R = min(readings.values())
            agree = sorted(s for s, v in readings.items() if v == R)
            rec["R"] = R
            rec["agreeing_seeds"] = agree
            rec["n_agree"] = len(agree)
            rec["stageable"] = len(agree) >= 3 and thr is not None and R > thr
            if rec["stageable"]:
                # per-side lightest over all complete rungs (>= R each);
                # prefer an agreeing rung on ties, then the lowest seed.
                def pick(side):
                    cands = [(complete[s][side][0], s not in agree, s)
                             for s in complete]
                    w, _, s = min(cands)
                    return w, complete[s][side][1], s
                wx, xwit, xseed = pick("X")
                wz, zwit, zseed = pick("Z")
                rec.update({"wx": wx, "xwit": xwit, "xseed": xseed,
                            "wz": wz, "zwit": zwit, "zseed": zseed,
                            "flat_seeds": agree})
        else:
            rec["stageable"] = False
        recs.append(rec)
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", required=True)
    ap.add_argument("--pool", default=None)
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--run-id", default="l2-q17-resume")
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    recs = analyze(args.rungs)
    for rec in recs:
        line = (f"i={rec['i']} k={rec['k']} w={rec['w']} "
                f"rungs={rec['n_complete_rungs']} "
                f"readings={list(rec['rung_readings'].values())} "
                f"thr={rec['threshold']}")
        if "R" in rec:
            line += (f" R={rec['R']} agree={rec['n_agree']}"
                     f"({','.join(map(str, rec['agreeing_seeds']))}) "
                     f"stageable={rec['stageable']}")
        else:
            line += " (no complete rung yet)"
        print(line, flush=True)

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(recs, f, indent=1)

    if not args.stage:
        return
    for rec in recs:
        if not rec.get("stageable"):
            continue
        path, doc = base.stage(rec, args.trials, args.run_id)
        print(f"i={rec['i']}: staged [[{doc['n']},{doc['k']},"
              f"{doc['distance']['d']}]] -> {path}", flush=True)


if __name__ == "__main__":
    main()
