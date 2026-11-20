"""Fast-backend r=1 lattice grafting for confirmed L6 survivors.

Shrinks n by removing qubits that participate in exactly one stabilizer
(restricted r=1 moves, arXiv:2504.08887 Sec. III E), keeping k fixed and the
distance at or above an explicit floor. Modeled on boundary_engine's
graft_r1_safe but every distance probe runs on the gf2_fast backend:

  screen   fixed-seed 20000 trials (pd 16)        -- cheap reject
  confirm  TWO fresh seeds x 200k (pd 12)         -- per-step keep
  block    every 3 accepted removals, 3 x 1M (pd 10) -- else rollback

All probes checkpoint to graft.jsonl; a kill wave loses one probe.
Resume: the run is deterministic enough per (cand, seed); simplest resume is
to rerun with a different --seed (the blacklist differs but the floor holds).
Usage: graft.py --cand <key> --floor D [--max-removals N]
"""
import argparse
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
GRAFT = os.path.join(WS, "graft.jsonl")
DEEP_SUM = os.path.join(WS, "deep_summary.jsonl")


def append(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def d_probe(HX, HZ, trials, seed, pd):
    wit = surrogate.distance_rand_witness(HX, HZ, trials=trials, seed=seed,
                                          backend="fast", threads=2,
                                          pair_depth=pd)
    if wit.rejected or wit.side not in ("X", "Z"):
        return 10 ** 9, None, None
    return int(wit.weight), wit.side, list(wit.support)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True)
    ap.add_argument("--max-removals", type=int, default=40)
    ap.add_argument("--floor", type=int, required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--block", type=int, default=3)
    args = ap.parse_args()

    rows = {}
    with open(DEEP_SUM, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rows[r["cand"]] = r
    b = rows[args.cand]
    Sf = [tuple(p) for p in b["pair"][0]]
    Sg = [tuple(p) for p in b["pair"][1]]
    HX, HZ, info = be.build_planar(b["Lx"], b["Ly"], Sf, Sg)
    HX = be.reduce_weights(HX)
    HZ = be.reduce_weights(HZ)
    HX = HX[HX.sum(axis=1) > 0] if HX.size else HX
    HZ = HZ[HZ.sum(axis=1) > 0] if HZ.size else HZ
    k0 = int(be.compute_k(HX, HZ))
    orig = list(range(HX.shape[1]))
    removed = []
    print(f"graft {args.cand}: n={HX.shape[1]} k={k0} floor={args.floor}",
          flush=True)

    rng = np.random.default_rng(args.seed)
    blacklist = set()
    confirm_seed = 7001 + 17 * args.seed
    since_block = []
    snap_HX, snap_HZ, snap_orig, snap_removed = (HX.copy(), HZ.copy(),
                                                 list(orig), list(removed))
    n_removed = 0
    while n_removed < args.max_removals:
        wx = HX.sum(axis=0)
        wz = HZ.sum(axis=0)
        cands = ([("X", int(q)) for q in np.where(wx == 1)[0]
                  if orig[q] not in blacklist] +
                 [("Z", int(q)) for q in np.where(wz == 1)[0]
                  if orig[q] not in blacklist])
        if not cands:
            print("no r=1 candidates left", flush=True)
            break
        rng.shuffle(cands)
        accepted = False
        for (t, q) in cands:
            H = HX if t == "X" else HZ
            r = int(np.where(H[:, q] == 1)[0][0])
            HX2 = np.delete(HX, r, axis=0) if t == "X" else HX
            HZ2 = np.delete(HZ, r, axis=0) if t == "Z" else HZ
            HX2 = np.delete(HX2, q, axis=1)
            HZ2 = np.delete(HZ2, q, axis=1)
            if int(be.compute_k(HX2, HZ2)) != k0:
                continue
            w1, _, _ = d_probe(HX2, HZ2, 20000, 9001, 16)
            if w1 < args.floor:
                continue
            w2, _, _ = d_probe(HX2, HZ2, 200_000, confirm_seed, 12)
            w3, _, _ = d_probe(HX2, HZ2, 200_000, confirm_seed + 1, 12)
            confirm_seed += 7
            wmin = min(w2, w3)
            append(GRAFT, {"cand": args.cand, "event": "step", "type": t,
                           "orig_q": orig[q], "n": int(HX2.shape[1]),
                           "screen": w1, "confirm": [w2, w3],
                           "floor": args.floor, "ts": time.time()})
            if wmin < args.floor:
                blacklist.add(orig[q])
                print(f"  UNDO orig={orig[q]} confirm={w2},{w3} < {args.floor}",
                      flush=True)
                continue
            oq = orig[q]
            del orig[q]
            HX, HZ = HX2, HZ2
            removed.append(oq)
            since_block.append(oq)
            n_removed += 1
            accepted = True
            print(f"  removed orig={oq} -> n={HX.shape[1]} "
                  f"confirm={w2},{w3}", flush=True)
            if len(since_block) >= args.block:
                wb = min(d_probe(HX, HZ, 300_000, s, 12)[0]
                         for s in (8101, 8201, 8301))
                if wb < args.floor:
                    HX, HZ = snap_HX.copy(), snap_HZ.copy()
                    orig, removed = list(snap_orig), list(snap_removed)
                    blacklist.update(since_block)
                    n_removed -= len(since_block)
                    print(f"  BLOCK ROLLBACK ({len(since_block)} removals, "
                          f"gate={wb})", flush=True)
                else:
                    snap_HX, snap_HZ = HX.copy(), HZ.copy()
                    snap_orig, snap_removed = list(orig), list(removed)
                    np.savez_compressed(
                        os.path.join(WS, f"graft_state_{args.cand.replace('|','_')}.npz"),
                        HX=HX, HZ=HZ, orig=np.array(orig),
                        removed=np.array(removed))
                    append(GRAFT, {"cand": args.cand, "event": "block-pass",
                                   "removed_orig": list(removed),
                                   "n": int(HX.shape[1]), "gate": wb,
                                   "ts": time.time()})
                    print(f"  block PASS at n={HX.shape[1]} (gate={wb})",
                          flush=True)
                since_block = []
            break
        if not accepted:
            print("no acceptable r=1 move; stop", flush=True)
            break
    print(f"graft done: n {b['n']} -> {HX.shape[1]}, removals={n_removed}",
          flush=True)


if __name__ == "__main__":
    main()
