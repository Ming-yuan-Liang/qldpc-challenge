"""L5 deep confirmation: multi-seed trial ladder + quotient screens on the
FULL code, witness persistence per rung, dominance precheck, optional
packaging + gate (mirrors l4_confirm but for pp-CPM template draws).

Every reading that could support a claim is persisted (weight, side, support,
seed, trials, pair_depth) into a per-candidate confirm ledger immediately.

Usage:
  python l5_deep.py --ledger ledger_pp_pp614_49_99001.json --draws 3,17 \
      --rungs 500000,500000,500000 --seeds 800001,800002,800003
  python l5_deep.py --ledger ... --draws 3 --rungs 2000000 --seeds 800009 \
      --quotient --stage
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
sys.path.insert(0, os.path.join(ROOT, "research", "campaigns",
                                "beat-surface-k50-w8-unrestricted"))

os.environ.setdefault("QLDPC_RUN_ID", "l5-beat-surface")

from l5_pp import TEMPLATES, build_H, quick_eval  # noqa: E402
from surrogate import distance_rand_witness, validate_logical  # noqa: E402
from css import compute_k  # noqa: E402
from search import fingerprint  # noqa: E402
from l4_board import Board  # noqa: E402

BOARD = Board(os.path.join(HERE, "l5_board_cache.json"))


def save(path, obj):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def rebuild(tplname, N, SX, SZ):
    tpl = TEMPLATES[tplname]
    return build_H(tpl, SX, SZ, N)


def quotient_caps(tplname, N, SX, SZ, HX, HZ, threads=2):
    """For each proper divisor d of N: build the Z_d quotient code from the
    exponents mod d, RIS it, repeat any logical (N/d)-fold, and keep it only
    if validate_logical accepts it against the FULL code. Returns a list of
    {d, quotient_reading, full_weight, side, support} sound caps."""
    tpl = TEMPLATES[tplname]
    out = []
    for d in range(2, N):
        if N % d:
            continue
        SXd = [[(v % d if v is not None else None) for v in row] for row in SX]
        SZd = [[(v % d if v is not None else None) for v in row] for row in SZ]
        HXd, HZd = build_H(tpl, SXd, SZd, d)
        if not ((HXd.sum(1) > 0).all() and (HZd.sum(1) > 0).all()):
            continue
        wit = distance_rand_witness(HXd, HZd, trials=20000, seed=700000 + d,
                                    backend="fast", threads=threads,
                                    pair_depth=10)
        if not wit:
            continue
        m = N // d
        rep = np.zeros(HX.shape[1], dtype=np.int8)
        for q in wit.support:
            blk, off = divmod(q, d)
            for t in range(m):
                rep[blk * N + off + t * d] = 1
        w_rep = int(rep.sum())
        ok, why = validate_logical(HX, HZ, wit.side, w_rep,
                                   [int(i) for i in np.nonzero(rep)[0]])
        if ok:
            out.append({"d": d, "q_read": int(wit.weight), "mult": m,
                        "full_weight": w_rep, "side": wit.side,
                        "support": [int(i) for i in np.nonzero(rep)[0]]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--draws", required=True)
    ap.add_argument("--rungs", default="500000,500000,500000")
    ap.add_argument("--seeds", default="800001,800002,800003")
    ap.add_argument("--pair-depth", type=int, default=10)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--quotient", action="store_true")
    ap.add_argument("--zside", action="store_true",
                    help="append one swapped-matrix rung (Z-side witness)")
    ap.add_argument("--stage", action="store_true")
    args = ap.parse_args()

    led = json.load(open(args.ledger, encoding="utf-8"))
    tplname, N = led["template"], led["N"]
    n = led["n"]
    floor = led["floor"]

    for di in [int(x) for x in args.draws.split(",")]:
        rec = led["draws"][str(di)]
        SX, SZ = rec["SX"], rec["SZ"]
        HX, HZ = rebuild(tplname, N, SX, SZ)
        k = int(compute_k(HX, HZ))
        w = int(max(HX.sum(1).max(), HZ.sum(1).max()))
        fp = fingerprint(HX, HZ)
        tag = f"{tplname}_N{N}_d{di}_{fp[:8]}"
        cpath = os.path.join(HERE, f"confirm_{tag}.json")
        cled = json.load(open(cpath, encoding="utf-8")) if \
            os.path.exists(cpath) else {"tag": tag, "fp": fp, "n": n, "k": k,
                                        "w": w, "N": N, "floor": floor,
                                        "rungs": [], "quotient": []}
        print(f"=== draw {di}: [[{n},{k},?]] w={w} floor={floor} "
              f"fp={fp[:12]} ({cpath})", flush=True)

        if args.quotient and not cled["quotient"]:
            t0 = time.time()
            caps = quotient_caps(tplname, N, SX, SZ, HX, HZ, args.threads)
            cled["quotient"] = caps
            save(cpath, cled)
            qmin = min((c["full_weight"] for c in caps), default=None)
            print(f"  quotient caps: {[(c['d'], c['full_weight']) for c in caps]}"
                  f" min_full={qmin} ({time.time()-t0:.0f}s)", flush=True)

        seeds = [int(s) for s in args.seeds.split(",")]
        trials_list = [int(t) for t in args.rungs.split(",")]
        rungs = list(zip(seeds * len(trials_list), trials_list)) if \
            len(seeds) == 1 else list(zip(seeds, trials_list))
        if args.zside:
            rungs.append(("swZ", trials_list[-1]))
        for seed, trials in rungs:
            swapped = seed == "swZ"
            snum = 810777 if swapped else seed
            key = f"{seed}:{trials}:pd{args.pair_depth}"
            if any(r["key"] == key for r in cled["rungs"]):
                r = next(r for r in cled["rungs"] if r["key"] == key)
                print(f"  reused {key}: w={r['weight']} ({r['side']})",
                      flush=True)
                continue
            t0 = time.time()
            wit = distance_rand_witness(HZ, HX, trials=trials, seed=snum,
                                        backend="fast", threads=args.threads,
                                        pair_depth=args.pair_depth) \
                if swapped else \
                distance_rand_witness(HX, HZ, trials=trials, seed=seed,
                                      backend="fast", threads=args.threads,
                                      pair_depth=args.pair_depth)
            dt = time.time() - t0
            wside = wit.side if wit else ""
            if swapped and wside:
                wside = "Z" if wside == "X" else "X"
            entry = {"key": key, "seed": str(seed), "trials": trials,
                     "pair_depth": args.pair_depth,
                     "weight": int(wit.weight) if wit else None,
                     "side": wside,
                     "support": list(wit.support) if wit else [],
                     "sec": round(dt, 1)}
            cled["rungs"].append(entry)
            save(cpath, cled)   # witness persisted immediately
            wt = entry["weight"]
            print(f"  rung {key}: w={wt} ({entry['side']}) dt={dt:.0f}s",
                  flush=True)

        weights = [r["weight"] for r in cled["rungs"] if r["weight"]]
        if weights:
            d_claim = min(weights)
            qmin = min((c["full_weight"] for c in cled["quotient"]), default=10**6)
            d_claim = min(d_claim, qmin) if qmin else d_claim
            below = [r for r in cled["rungs"] if r["weight"] and
                     r["weight"] < d_claim]
            dom, adv = BOARD.verdict(n, k, d_claim, w)
            cled["d_claim"] = d_claim
            cled["dominated_by"] = dom
            cled["advances_n"] = len(adv)
            save(cpath, cled)
            print(f"  claimed d<={d_claim}; dominated_by={len(dom)} "
                  f"advances={len(adv)} (floor {floor}, "
                  f"non-dominated={not dom and d_claim > floor})", flush=True)

            if args.stage and not dom and d_claim > floor:
                from submit import make_submission, save_submission  # noqa
                from coordination import (unique_path, staging_dir,
                                          gate_and_record)  # noqa
                tpl = TEMPLATES[tplname]
                n_rows = len(tpl.get("rows_X") or tpl["rows"])
                rate_den = tpl["L"] - 2 * n_rows
                best_x = min((r for r in cled["rungs"]
                              if r["weight"] and r["side"] == "X"),
                             key=lambda r: r["weight"], default=None)
                best_z = min((r for r in cled["rungs"]
                              if r["weight"] and r["side"] == "Z"),
                             key=lambda r: r["weight"], default=None)
                wit_x = (best_x["weight"], best_x["support"]) if best_x else None
                wit_z = (best_z["weight"], best_z["support"]) if best_z else None
                rate_den = tpl["L"] - 2 * n_rows
                name = (f"pair-partition CPM [[{n},{k},{d_claim}]] w={w} "
                        f"({n_rows}x{tpl['L']} pair-closed template, "
                        f"rate 1/{rate_den}, lift Z_{N})")
                construction = (
                    f"Irregular pair-partition CPM CSS code (Okada-Kasai "
                    f"arXiv:2607.14091 commutation rule) on the "
                    f"{n_rows}x{tpl['L']} template published with "
                    f"codes/994-142-40 (rows as unions of column pairs, check "
                    f"weight 8), cyclic lift N={N}, n={n}, design k=2N={2*N}; "
                    f"exponents drawn from the exact integer solution lattice "
                    f"of the paired-difference equations reduced mod {N} "
                    f"(4-cycle-free draw, lane beat-surface-k100-w8).")
                recipe_spec = {
                    "constructor": "l5_pp.build_H",
                    "params": {"template": tplname, "N": N,
                               "SX": SX, "SZ": SZ},
                    "family": "pair-partition-cpm"}
                num_seeds = [int(r["seed"]) for r in cled["rungs"]
                             if str(r.get("seed", "")).isdigit()]
                doc = make_submission(
                    HX, HZ, name=name, construction=construction,
                    authors=["l5-beat-surface-k100-w8"],
                    family="pair-partition-cpm",
                    confidence="upper_bound",
                    trials=max(r["trials"] for r in cled["rungs"]),
                    seed=num_seeds[-1] if num_seeds else 0,
                    notes=(f"Lane beat-surface-k100-w8-unrestricted. Exponent "
                           f"draw of the 994-142-40 template class at lift "
                           f"Z_{N}; readings: "
                           f"{[(r['trials'], r['weight']) for r in cled['rungs']]}; "
                           f"quotient caps {[(c['d'], c['full_weight']) for c in cled['quotient']]}; "
                           f"pair_depth {args.pair_depth}."),
                    witnesses=(wit_x[0], wit_x[1], wit_z[0], wit_z[1])
                    if wit_x and wit_z else None,
                )
                staging = staging_dir()
                path = unique_path(os.path.join(staging, f"{n}-{k}-{d_claim}.json"),
                                   doc)
                errs = save_submission(doc, path, spec=recipe_spec)
                print(f"staged: {path} (errs={errs})", flush=True)
                verdict, out = gate_and_record(path)
                nov = (verdict.get("gates") or {}).get("novelty") or {}
                print(f"gate passed={verdict.get('passed')} "
                      f"board_advancing={nov.get('board_advancing')} "
                      f"verdict={out}", flush=True)
        else:
            print("  no readings yet", flush=True)


if __name__ == "__main__":
    main()
