"""L4 confirmation + staging: 3 fresh seeds x >=20k trials/side, then package.

Reads a promising record from a screening ledger, rebuilds the code from its
spec, runs flat fresh-seed rungs per side with lightest_logical (which returns
(weight, support) witnesses), checks flatness + dominance, and on success
packages via submit.make_submission + save_submission into the lane staging
dir, then runs the gate (coordination.gate_and_record) and reports
board_advancing. Checkpointed per (seed, side) rung for kill resilience.

Usage:
  python -I l4_confirm.py --ledger ledger_w8_51001.json --index 0 \
      [--trials 20000] [--seeds 910001,910002,910003] [--stage]
"""
import argparse
import json
import os
import sys
import time

import numpy as np

KIT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge\research\kit"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, KIT)
sys.path.insert(0, HERE)

os.environ.setdefault("QLDPC_RUN_ID", "l4-beat-surface")

import gf2poly  # noqa: E402
from css import compute_k  # noqa: E402
from surrogate import lightest_logical  # noqa: E402
from search import fingerprint  # noqa: E402
from l4_board import Board  # noqa: E402


def rebuild(spec):
    if spec.get("family") == "2bga-metacyclic":
        from group_algebra import metacyclic, build_2bga
        mul, _ = metacyclic(spec["n"], spec["k_m"], spec["r"])
        return build_2bga(mul, spec["a"], spec["b"])
    m, a, b = spec["m"], spec["a"], spec["b"]
    return gf2poly.cyclic_gb(m, a, b)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--seeds", default="910001,910002,910003")
    ap.add_argument("--stage", action="store_true",
                    help="package + gate on success")
    args = ap.parse_args()

    led = load(args.ledger)
    rec = led["promising"][args.index]
    spec = rec["spec"]
    HX, HZ = rebuild(spec)
    n, k = int(HX.shape[1]), int(compute_k(HX, HZ))
    w = int(max(HX.sum(1).max(), HZ.sum(1).max()))
    fp = fingerprint(HX, HZ)
    assert n == rec["n"] and k == rec["k"] and w == rec["w"], \
        f"rebuild mismatch: {(n, k, w)} vs {(rec['n'], rec['k'], rec['w'])}"
    print(f"confirm [[{n},{k},?]] w={w} fp={fp} spec={json.dumps(spec)[:120]}",
          flush=True)

    seeds = [int(s) for s in args.seeds.split(",")]
    cpath = os.path.join(HERE, f"confirm_{fp[:12]}.json")
    cled = load(cpath) if os.path.exists(cpath) else {
        "fp": fp, "n": n, "k": k, "w": w, "trials": args.trials, "rungs": {}}

    def rung_key(seed, side):
        return f"{seed}:{side}:{args.trials}"

    readings = {"X": {}, "Z": {}}
    witnesses = {}
    for seed in seeds:
        for side, (Hself, Hopp) in (("X", (HX, HZ)), ("Z", (HZ, HX))):
            key = rung_key(seed, side)
            if key in cled["rungs"]:
                r = cled["rungs"][key]
                readings[side][seed] = r["weight"]
                witnesses[(side, seed)] = r["support"]
                print(f"  reused {key}: w={r['weight']}", flush=True)
                continue
            t0 = time.time()
            wt, sup = lightest_logical(Hself, Hopp, trials=args.trials,
                                       seed=seed)
            cled["rungs"][key] = {"weight": int(wt), "support": sup,
                                  "dt_s": round(time.time() - t0, 1)}
            save(cpath, cled)
            readings[side][seed] = int(wt)
            witnesses[(side, seed)] = sup
            print(f"  rung {key}: w={wt} dt={time.time()-t0:.0f}s", flush=True)

    wx = min(readings["X"].values())
    wz = min(readings["Z"].values())
    d = min(wx, wz)
    xs = sorted(set(readings["X"].values()))
    zs = sorted(set(readings["Z"].values()))
    flat = (len(xs) == 1 and len(zs) == 1 and xs[0] == wx and zs[0] == wz)
    print(f"claimed d={d} (X={wx} {readings['X']}, Z={wz} {readings['Z']}) "
          f"flat={flat}", flush=True)

    board = Board(os.path.join(HERE, "l4_board_cache.json"))
    dom, adv = board.verdict(n, k, d, w)
    print(f"dominance: dominated_by={len(dom)} {dom[:3]} advances={len(adv)} "
          f"{adv[:3]}", flush=True)

    cled["claimed_d"] = d
    cled["wx"], cled["wz"], cled["flat"] = wx, wz, flat
    cled["dominated_by"] = dom
    cled["advances_n"] = len(adv)
    save(cpath, cled)

    if not flat:
        print("NOT FLAT: readings vary across fresh seeds; no claim.", flush=True)
        return 2
    if dom:
        print("DOMINATED: not a find; record as non-frontier.", flush=True)
        return 3
    if not adv:
        print("ADVANCES NOTHING: gate may still call it board_advancing "
              "(not-dominated), but lane criterion wants a strict gain.", flush=True)

    if not args.stage:
        print("dry-run ok; pass --stage to package + gate.", flush=True)
        return 0

    # package
    from submit import make_submission, save_submission  # noqa: E402
    from coordination import unique_path, staging_dir, gate_and_record  # noqa: E402
    xseed = min(seeds, key=lambda s: readings["X"][s])
    zseed = min(seeds, key=lambda s: readings["Z"][s])
    if spec.get("family") == "2bga-metacyclic":
        name = (f"2BGA [[{n},{k},{d}]] w={w} (metacyclic "
                f"Z_{spec['n']} x| Z_{spec['k_m']}, r={spec['r']})")
        construction = (f"2-block group algebra on the metacyclic group "
                        f"Z_{spec['n']} x| Z_{spec['k_m']} (r^{spec['k_m']}=1 "
                        f"mod {spec['n']}), weight-2 supports a={spec['a']}, "
                        f"b={spec['b']}")
        family = "2bga"
        recipe_spec = {"constructor": "group_algebra.build_2bga",
                       "params": {"mul": f"metacyclic({spec['n']},"
                                          f"{spec['k_m']},{spec['r']})",
                                  "a": spec["a"], "b": spec["b"]},
                       "family": "2bga-metacyclic", "k_filter": [45, 55]}
    else:
        name = (f"cyclic GB [[{n},{k},{d}]] w={w} "
                f"(2B-free generalized bicycle)")
        construction = (f"cyclic generalized bicycle over Z_{spec['m']}: "
                        f"H_X=[circ(a)|circ(b)], H_Z=[circ(b)^T|circ(a)^T], "
                        f"a={spec['a']}, b={spec['b']} (exponent supports)")
        family = "generalized-bicycle"
        recipe_spec = {"constructor": "gf2poly.cyclic_gb",
                       "params": {"m": spec["m"], "a": spec["a"],
                                  "b": spec["b"]},
                       "family": "generalized-bicycle", "k_band": [45, 55]}
    doc = make_submission(
        HX, HZ,
        name=name,
        construction=construction,
        authors=["l4-beat-surface-k50-w8"],
        family=family,
        confidence="upper_bound",
        trials=args.trials,
        seed=xseed,
        notes=(f"Lane beat-surface-k50-w8-unrestricted; flat at {len(seeds)} "
               f"fresh seeds x {args.trials} trials/side "
               f"(X seeds {sorted(readings['X'])}, Z seeds {sorted(readings['Z'])}); "
               f"screening spec kept as recipe."),
        witnesses=(wx, witnesses[("X", xseed)], wz, witnesses[("Z", zseed)]),
    )
    staging = staging_dir()          # research/candidates/l4-beat-surface
    path = unique_path(os.path.join(staging, f"{n}-{k}-{d}.json"), doc)
    errs = save_submission(doc, path, spec=recipe_spec)
    print(f"staged: {path} (schema errs: {errs})", flush=True)

    verdict, out = gate_and_record(path)
    nov = (verdict.get("gates") or {}).get("novelty") or {}
    print(f"gate passed={verdict.get('passed')} "
          f"board_advancing={nov.get('board_advancing')} "
          f"verdict={out}", flush=True)
    print(json.dumps(verdict.get("labels"), indent=1), flush=True)
    if nov.get("board_advancing") is False:
        nf = os.path.join(staging, "nonfrontier")
        os.makedirs(nf, exist_ok=True)
        for suffix in ("", ".verdict.json", ".recipe.json", ".preflight.json"):
            src = path + suffix
            if os.path.exists(src):
                os.replace(src, os.path.join(nf, os.path.basename(src)))
        print("moved to nonfrontier/ (dominated per gate)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
