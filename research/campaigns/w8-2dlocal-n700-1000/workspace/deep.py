"""Deep confirmation runs for escalated L6 candidates.

Reads escalate.jsonl (from sweep.py), rebuilds each candidate, and runs a
chunked multi-seed ladder. The fast kernel searches BOTH sides per call and
returns the global best (weight, side, support) -- exactly the quantity the
gate's refutation hunts under, so the claim basis is the global-min reading.
Per-side witnesses accumulate from whatever side each call reports; numpy
per-side chunks (rung "np") cross-check the fast readings and pin down the
Z witness for packaging.

Rungs (chunk = ONE checkpointed call):
  r3   200k trials, pair_depth 16, seeds 401/409/419   (fast, global)
  r4   1M trials,   pair_depth 12, seeds 503/509/521/531/541/551 (fast, global)
  np   numpy lightest_logical per side, 20000 trials, seed 601/602
       (--np-trials to override; expensive, only for staging candidates)

Every chunk appends to deep.jsonl before the next starts, so a kill wave
loses at most one chunk.  deep_summary.jsonl (rewritten idempotently) carries
per-candidate per-side lightest readings, the global-min claim, and witnesses.
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

ROOT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "research", "local2d"))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
sys.path.insert(0, os.path.join(ROOT, "verify"))

import boundary_engine as be  # noqa: E402
import surrogate  # noqa: E402

WS = os.path.join(ROOT, "research", "campaigns", "w8-2dlocal-n700-1000", "workspace")
DEEP = os.path.join(WS, "deep.jsonl")
DEEP_SUM = os.path.join(WS, "deep_summary.jsonl")
ESCALATE = os.path.join(WS, "escalate.jsonl")

R3 = (200_000, 16, (401, 409, 419))
R4 = (1_000_000, 12, (503, 509, 521, 531, 541, 551))


def cand_key(cand):
    pk = hashlib.sha1(json.dumps(
        [sorted(map(tuple, cand["pair"][0])),
         sorted(map(tuple, cand["pair"][1]))]).encode()).hexdigest()[:10]
    return f"{pk}|{cand['Lx']}x{cand['Ly']}"


def rebuild(cand):
    Sf = [tuple(p) for p in cand["pair"][0]]
    Sg = [tuple(p) for p in cand["pair"][1]]
    HX, HZ, info = be.build_planar(cand["Lx"], cand["Ly"], Sf, Sg)
    HX = be.reduce_weights(HX)
    HZ = be.reduce_weights(HZ)
    return HX, HZ, info


def append(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_deep():
    done = {}
    if os.path.exists(DEEP):
        with open(DEEP, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                k = rec.get("chunk_key")
                if k and k not in done:
                    done[k] = rec
    return done


def fast_chunk(chunk_key, HX, HZ, trials, pd, seed, ck):
    t0 = time.time()
    wit = surrogate.distance_rand_witness(
        HX, HZ, trials=trials, seed=seed, backend="fast", threads=2,
        pair_depth=pd)
    rec = {"chunk_key": chunk_key, "cand": ck, "instrument": "fast",
           "trials": trials, "pd": pd, "seed": seed,
           "weight": int(wit.weight) if wit.weight <= HX.shape[1] else None,
           "side": wit.side, "support": list(wit.support) if wit.support else [],
           "rejected": wit.rejected, "secs": round(time.time() - t0, 1),
           "ts": time.time()}
    if wit.rejected or wit.side not in ("X", "Z"):
        rec["weight"] = None
        rec["support"] = []
    return rec


def numpy_chunk(chunk_key, HX, HZ, trials, seed, side, ck):
    """Per-side numpy search: side 'X' -> (HX, HZ); 'Z' -> (HZ, HX)."""
    t0 = time.time()
    if side == "X":
        w, sup = surrogate.lightest_logical(HX, HZ, trials=trials, seed=seed)
    else:
        w, sup = surrogate.lightest_logical(HZ, HX, trials=trials, seed=seed)
    rec = {"chunk_key": chunk_key, "cand": ck, "instrument": "numpy",
           "side": side, "trials": trials, "seed": seed,
           "weight": int(w) if w <= HX.shape[1] else None,
           "support": [int(q) for q in sup] if sup else [],
           "secs": round(time.time() - t0, 1), "ts": time.time()}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rung", choices=["r3", "r4", "np"], required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--max-cands", type=int, default=10 ** 9)
    ap.add_argument("--order", choices=["margin", "kd2"], default="kd2")
    ap.add_argument("--trials", type=int, default=None,
                    help="override the rung's trials (smoke tests)")
    ap.add_argument("--require-r3-pass", action="store_true",
                    help="only candidates whose r3 min reading >= reqd")
    ap.add_argument("--seeds", type=str, default=None,
                    help="comma-separated seed subset for the rung")
    args = ap.parse_args()

    cands = {}
    with open(ESCALATE, encoding="utf-8") as f:
        for line in f:
            try:
                c = json.loads(line)
            except Exception:
                continue
            if c.get("verdict") != "advance-screen":
                continue
            ck = cand_key(c)
            if ck not in cands or c.get("margin", -99) > cands[ck].get("margin", -99):
                cands[ck] = c
    if args.order == "margin":
        skey = lambda c: -c.get("margin", -99)  # noqa: E731
    else:
        skey = lambda c: -(c["k"] * min(c["readings"]) ** 2 / c["n"])  # noqa: E731
    keys = sorted(cands, key=lambda k: skey(cands[k]))

    done = load_deep()
    if args.require_r3_pass:
        r3min = {}
        for r in done.values():
            if r.get("weight") is not None and "|r3|" in (r.get("chunk_key") or ""):
                c = r["cand"]
                r3min[c] = min(r3min.get(c, 10 ** 9), r["weight"])
        keys = [k for k in keys
                if k in r3min and r3min[k] >= cands[k].get("reqd", 0)]
        print(f"r3-pass survivors: {len(keys)}", flush=True)
    keys = [k for i, k in enumerate(keys) if i % args.nshards == args.shard]
    if args.rung in ("r3", "r4", "np"):
        # keep only candidates with at least one MISSING chunk of this rung,
        # so max-cands counts actually-undone work
        def _undone(ck):
            c = cands[ck]
            if args.rung in ("r3", "r4"):
                tr, pdd, sds = (R3 if args.rung == "r3" else R4)
                if args.trials:
                    tr = args.trials
                if args.seeds:
                    sds = tuple(int(s) for s in args.seeds.split(","))
                return any(f"{ck}|{args.rung}|{sd}" not in done for sd in sds)
            return any(f"{ck}|np|{sd}|{sd_side}" not in done
                       for sd, sd_side in ((601, "X"), (602, "Z")))
        keys = [k for k in keys if _undone(k)]
    keys = keys[:args.max_cands]

    for ck in keys:
        cand = cands[ck]
        try:
            HX, HZ, info = rebuild(cand)
        except Exception as e:
            append(DEEP, {"chunk_key": f"{ck}|build", "error": repr(e)[:200]})
            continue
        n = int(HX.shape[1])
        k = int(be.compute_k(HX, HZ))
        if not (700 <= n <= 1000) or k <= 0:
            append(DEEP, {"chunk_key": f"{ck}|shape", "n": n, "k": k,
                          "error": "out of window"})
            continue
        meta = {"n": n, "k": k, "Lx": cand["Lx"], "Ly": cand["Ly"],
                "pair": cand["pair"], "tag": cand.get("tag")}

        if args.rung in ("r3", "r4"):
            trials, pd, seeds = R3 if args.rung == "r3" else R4
            if args.trials:
                trials = args.trials
            if args.seeds:
                seeds = tuple(int(s) for s in args.seeds.split(","))
            for seed in seeds:
                ckey = f"{ck}|{args.rung}|{seed}"
                if ckey in done:
                    continue
                try:
                    rec = fast_chunk(ckey, HX, HZ, trials, pd, seed, ck)
                except Exception as e:
                    append(DEEP, {"chunk_key": ckey, "error": repr(e)[:200],
                                  "ts": time.time()})
                    continue
                rec.update(meta)
                append(DEEP, rec)
        else:  # np rung: one chunk per side
            nt = args.trials or 20000
            for side, seed in (("X", 601), ("Z", 602)):
                ckey = f"{ck}|np|{seed}|{side}"
                if ckey in done:
                    continue
                try:
                    rec = numpy_chunk(ckey, HX, HZ, nt, seed, side, ck)
                except Exception as e:
                    append(DEEP, {"chunk_key": ckey, "error": repr(e)[:200],
                                  "ts": time.time()})
                    continue
                rec.update(meta)
                append(DEEP, rec)
        print(f"done {ck} rung {args.rung}", flush=True)

    summarize()


def summarize():
    if not os.path.exists(DEEP):
        return
    best = {}
    with open(DEEP, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("weight") is None or "cand" not in r:
                continue
            c = r["cand"]
            b = best.setdefault(c, {"sides": {}, "n": r.get("n"),
                                    "k": r.get("k"), "Lx": r.get("Lx"),
                                    "Ly": r.get("Ly"), "pair": r.get("pair"),
                                    "tag": r.get("tag"),
                                    "instruments": set()})
            b["instruments"].add(r.get("instrument"))
            s = b["sides"].setdefault(
                r["side"], {"weight": 10 ** 9, "support": [],
                            "trials": 0, "seed": None, "instrument": None})
            if r["weight"] < s["weight"]:
                s.update({"weight": r["weight"], "support": r["support"],
                          "trials": r["trials"], "seed": r["seed"],
                          "instrument": r.get("instrument"),
                          "pd": r.get("pd")})
    rows = []
    for c, b in best.items():
        b = dict(b)
        b["instruments"] = sorted(b["instruments"])
        b["cand"] = c
        ws = [v["weight"] for v in b["sides"].values() if v["weight"] < 10 ** 9]
        b["d_claim"] = min(ws) if ws else None
        b["X"] = b["sides"].get("X")
        b["Z"] = b["sides"].get("Z")
        rows.append(b)
    tmp = DEEP_SUM + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for b in rows:
            f.write(json.dumps(b, separators=(",", ":")) + "\n")
    os.replace(tmp, DEEP_SUM)


if __name__ == "__main__":
    main()
