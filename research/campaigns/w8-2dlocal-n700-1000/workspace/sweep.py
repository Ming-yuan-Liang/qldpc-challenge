"""L6 lane sweep: weight-8 2D-local bilayer codes, n in [700, 1000].

Phases:
  A  lattice sweep of the recorded seed support pairs across the window
  B  single-monomial mutation search around the B=5 box seeds (k>=19 targets)

Ladder (fast backend, threads=2):
  rung1  3 seeds x (20000 trials, pair_depth 22)
  rung2  3 seeds x (100000 trials, pair_depth 20)   [only if rung1 clears reqd]
Deep runs are a separate script (deep.py) fed by escalate.jsonl.

Checkpointing: one JSONL line per completed stage in progress.jsonl; the
done-set is reloaded on start, so a kill wave loses at most the current item.
"""
import argparse
import hashlib
import json
import os
import random
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
from css import verify_css  # noqa: E402
from prescreen import block_structure  # noqa: E402

WS = os.path.join(ROOT, "research", "campaigns", "w8-2dlocal-n700-1000", "workspace")
PROGRESS = os.path.join(WS, "progress.jsonl")
ESCALATE = os.path.join(WS, "escalate.jsonl")

SEEDS = {
    "TILE4": (be.S_F_TILE4, be.S_G_TILE4_MAIN),
    "TILE4P": (be.S_F_TILE4, be.S_G_TILE4_PUBLISHED),
    "W8": (be.S_F_W8, be.S_G_W8),
    "B5-29": ([0, 0], [1, 3], [2, 1], [4, 4]),  # placeholder, set below
}
SEED_PAIRS = {
    "TILE4": (be.S_F_TILE4, be.S_G_TILE4_MAIN),
    "TILE4P": (be.S_F_TILE4, be.S_G_TILE4_PUBLISHED),
    "W8": (be.S_F_W8, be.S_G_W8),
    "B5-29": ([(0, 0), (1, 3), (2, 1), (4, 4)], [(0, 2), (1, 4), (3, 1), (4, 0)]),
    "B5-32": ([(0, 0), (1, 3), (4, 0), (4, 4)], [(0, 4), (2, 1), (3, 2), (4, 0)]),
    "E08887": (be.S_F_08887, be.S_G_08887),
}

RUNG1 = (20000, 22)
RUNG2 = (100000, 20)
SEEDS_RUNG = (101, 211, 307)
N_MIN, N_MAX = 700, 1000

# ---------------------------------------------------------------- board reqd
def board_reqd_table():
    """max d_b over board entries with layers<=2, w<=8, keyed implicitly.

    Returns list of (n_b, k_b, d_b) for every potential dominator (CSS,
    locality block present, w<=8).  reqd(n, k) = 1 + max d_b over entries
    with n_b <= n and k_b >= k; 0 if the cone is empty.
    """
    import glob
    entries = []
    for f in glob.glob(os.path.join(ROOT, "codes", "*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        loc = d.get("locality")
        if not isinstance(loc, dict):
            continue  # unrestricted: cannot dominate the bilayer cell
        layers = loc.get("layers", 1)
        if layers not in (1, 2, None):
            continue
        ch = d.get("checks") or {}
        wx = max((len(r) for r in ch.get("X", [])), default=0)
        wz = max((len(r) for r in ch.get("Z", [])), default=0)
        if max(wx, wz) > 8:
            continue
        dist = d.get("distance")
        dv = dist if isinstance(dist, int) else (dist or {}).get("d")
        if not isinstance(dv, int) or dv <= 0:
            continue
        entries.append((d["n"], d["k"], dv))
    return entries


_REQD_ENTRIES = None
_DUP_CACHE = {}
_NK_INDEX = None


def _nk_index():
    """One pass over codes/: (n, k) -> [paths] for locality-tagged entries."""
    global _NK_INDEX
    if _NK_INDEX is None:
        import glob
        idx = {}
        for f in glob.glob(os.path.join(ROOT, "codes", "*.json")):
            try:
                with open(f, encoding="utf-8") as fh:
                    d = json.load(fh)
            except Exception:
                continue
            n, k = d.get("n"), d.get("k")
            if isinstance(n, int) and isinstance(k, int) and d.get("checks"):
                idx.setdefault((n, k), []).append(f)
        _NK_INDEX = idx
    return _NK_INDEX


def _board_checks(n, k):
    """X/Z row-support sets of every board entry with this exact (n, k)."""
    key = (n, k)
    if key in _DUP_CACHE:
        return _DUP_CACHE[key]
    outs = []
    for f in _nk_index().get(key, ()):  # noqa: E501
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        if d.get("n") != n or d.get("k") != k:
            continue
        ch = d.get("checks") or {}
        sx = frozenset(tuple(sorted(r)) for r in ch.get("X", []))
        sz = frozenset(tuple(sorted(r)) for r in ch.get("Z", []))
        outs.append((sx, sz, os.path.basename(f)))
    _DUP_CACHE[key] = outs
    return outs


def is_board_dup(HX, HZ):
    """Board entry name if some entry with the same (n, k) spans the same
    X and Z rowspaces (a dedup-level duplicate), else None."""
    import gf2_fast
    n = int(HX.shape[1])
    k = int(gf2_fast.compute_k(np.asarray(HX, np.int8), np.asarray(HZ, np.int8)))
    X = np.asarray(HX, np.int8)
    Z = np.asarray(HZ, np.int8)
    for (bx, bz, base) in _board_checks(n, k):
        if not bx and not bz:
            continue
        BX = np.zeros((len(bx), n), np.int8)
        for i, r in enumerate(sorted(bx)):
            BX[i, list(r)] = 1
        BZ = np.zeros((len(bz), n), np.int8)
        for i, r in enumerate(sorted(bz)):
            BZ[i, list(r)] = 1
        try:
            rx = gf2_fast.gf2_rank(np.vstack([X, BX])) == gf2_fast.gf2_rank(BX)
            rz = gf2_fast.gf2_rank(np.vstack([Z, BZ])) == gf2_fast.gf2_rank(BZ)
            rx = rx and gf2_fast.gf2_rank(np.vstack([X, BX])) == gf2_fast.gf2_rank(X)
            rz = rz and gf2_fast.gf2_rank(np.vstack([Z, BZ])) == gf2_fast.gf2_rank(Z)
            if rx and rz:
                return base
        except Exception:
            if (frozenset(tuple(sorted(np.nonzero(r)[0].tolist())) for r in X) == bx
                    and frozenset(tuple(sorted(np.nonzero(r)[0].tolist())) for r in Z) == bz):
                return base
    return None



def reqd(n, k):
    """Minimal advancing d for a candidate at (n, k) in the bilayer w<=8 cell."""
    global _REQD_ENTRIES
    if _REQD_ENTRIES is None:
        _REQD_ENTRIES = board_reqd_table()
    m = 0
    for (nb, kb, db) in _REQD_ENTRIES:
        if nb <= n and kb >= k and db > m:
            m = db
    return m + 1


# ---------------------------------------------------------------- orbit keys
def _shift(S):
    mp = min(p for p, _ in S)
    mq = min(q for _, q in S)
    return tuple(sorted((p - mp, q - mq) for (p, q) in S))


def orbit_keys(Sf, Sg):
    """Canonical keys for the (Sf, Sg) orbit: dihedral x {swap, no-swap}."""
    keys = set()
    tfs = [(list(Sf), list(Sg)), (list(Sg), list(Sf))]
    for A0, B0 in tfs:
        for t in (lambda x: x, lambda x: [(-p, q) for p, q in x]):
            A1, B1 = t(A0), t(B0)
            for u in (lambda x: x, lambda x: [(q, p) for p, q in x]):
                A2 = u(A1)
                B2 = u(B1)
                # joint shift: union min -> (0, 0)
                mpu = min(p for p, _ in A2 + B2)
                mqu = min(q for _, q in A2 + B2)
                ka = _shift([(p - mpu, q - mqu) for (p, q) in A2])
                kb = _shift([(p - mpu, q - mqu) for (p, q) in B2])
                keys.add((ka, kb))
    return keys


def pair_key(Sf, Sg):
    return json.dumps(min(orbit_keys(Sf, Sg)), separators=(",", ":"))


# ---------------------------------------------------------------- items
def sizes_window():
    """Ordered (Lx, Ly) with product in [350, 500], both dims >= 14."""
    out = []
    for Lx in range(14, 36):
        for Ly in range(max(14, (349 + Lx) // Lx + (1 if (349 % Lx) else 0)), 501 // Lx + 1):
            p = Lx * Ly
            if 350 <= p <= 500:
                out.append((Lx, Ly))
    return sorted(out)


def phase_a_items():
    items = []
    tag_order = ("B5-29", "B5-32", "TILE4", "E08887", "TILE4P", "W8")
    for tag in tag_order:
        Sf, Sg = SEED_PAIRS[tag]
        for (Lx, Ly) in sizes_window():
            items.append(("A", tag, [list(p) for p in Sf], [list(p) for p in Sg], Lx, Ly))
    return items


def mutate(Sf, Sg, box, rng):
    """One single-monomial replacement move, joint-shift normalized."""
    A = [list(p) for p in Sf]
    B = [list(p) for p in Sg]
    tgt = rng.randrange(2)
    S = A if tgt == 0 else B
    i = rng.randrange(len(S))
    used = {tuple(x) for x in A} | {tuple(x) for x in B}
    for _ in range(50):
        cand = (rng.randrange(box + 1), rng.randrange(box + 1))
        if cand not in used:
            S[i] = list(cand)
            break
    else:
        return None
    # joint shift
    mpu = min(min(p for p, _ in A), min(p for p, _ in B))
    mqu = min(min(q for _, q in A), min(q for _, q in B))
    A = [[p - mpu, q - mqu] for p, q in A]
    B = [[p - mpu, q - mqu] for p, q in B]
    return (A, B)


def load_seen_keys():
    seen = set()
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            for line in f:
                seen.add(line.strip())
    return seen


SEEN_FILE = os.path.join(WS, "seen_keys.txt")


def register_key(key):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(key + "\n")


# ---------------------------------------------------------------- checkpoint
def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_progress():
    done = {}
    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                done[rec["key"]] = rec
    return done


# ---------------------------------------------------------------- screening
def screen_code(HX, HZ, trials, pd, threads=2):
    out = []
    for sd in SEEDS_RUNG:
        w = surrogate.distance_rand(HX, HZ, trials=trials, seed=sd,
                                    backend="fast", threads=threads,
                                    pair_depth=pd)
        out.append(int(w))
    return out


def build_one(Sf, Sg, Lx, Ly, reduce_w=True):
    HX, HZ, info = be.build_planar(Lx, Ly, [tuple(p) for p in Sf],
                                   [tuple(p) for p in Sg])
    if reduce_w:
        HX = be.reduce_weights(HX)
        HZ = be.reduce_weights(HZ)
    return HX, HZ, info


def code_facts(HX, HZ):
    import gf2_fast
    n = int(HX.shape[1])
    k = int(gf2_fast.compute_k(np.asarray(HX, np.int8), np.asarray(HZ, np.int8)))
    wx = int(HX.sum(axis=1).max()) if HX.size else 0
    wz = int(HZ.sum(axis=1).max()) if HZ.size else 0
    css = bool(verify_css(HX, HZ))
    st = block_structure(HX, HZ)
    # the gate's own hard criterion is one independent stabilizer block; the
    # known-good tile family reads tanner_components>1 on the raw rows, so
    # only blocks==1 is disqualifying at screen level (gate preflight is the
    # final arbiter)
    conn = (int(st.get("blocks", 99)) == 1)
    return n, k, wx, wz, css, conn, int(st.get("blocks", -1))


# ---------------------------------------------------------------- phases
def run_item(item, stage, trials, pd, rng_seed=None):
    _, tag, Sf, Sg, Lx, Ly = item
    HX, HZ, info = build_one(Sf, Sg, Lx, Ly)
    n, k, wx, wz, css, conn, nblocks = code_facts(HX, HZ)
    rec = {"key": item_key(item, stage), "tag": tag, "Lx": Lx, "Ly": Ly,
           "n": n, "k": k, "wx": wx, "wz": wz, "css": css, "conn": conn,
           "nblocks": nblocks,
           "stage": stage, "trials": trials, "pd": pd,
           "removed": int(info.get("n_removed_qubits", 0)),
           "promoted": int(info.get("n_promoted", 0)), "ts": time.time()}
    if not (css and conn) or not (N_MIN <= n <= N_MAX) or k <= 0:
        rec["readings"] = []
        rec["verdict"] = "reject-structural"
        return rec, HX, HZ
    if max(wx, wz) > 8:
        rec["readings"] = []
        rec["verdict"] = "reject-weight"
        return rec, HX, HZ
    readings = screen_code(HX, HZ, trials, pd)
    best = min(readings)
    r = reqd(n, k)
    rec["readings"] = readings
    rec["reqd"] = r
    margin = best - r
    rec["margin"] = margin
    if best >= r:
        dup = is_board_dup(HX, HZ)
        if dup:
            rec["verdict"] = "board-dup"
            rec["dup_of"] = dup
        else:
            rec["verdict"] = "advance-screen"
            append_jsonl(ESCALATE, dict(rec, Sf=Sf, Sg=Sg,
                                        pair=[Sf, Sg]))
    else:
        rec["verdict"] = "non-advancing"
    return rec, HX, HZ


def item_key(item, stage):
    tag, Sf, Sg, Lx, Ly = item[1], item[2], item[3], item[4], item[5]
    pk = hashlib.sha1(json.dumps(
        [sorted(map(tuple, Sf)), sorted(map(tuple, Sg))]).encode()
    ).hexdigest()[:10]
    return f"{stage}|{tag}|{Lx}x{Ly}|{pk}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["A", "B"], required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--max-items", type=int, default=10 ** 9)
    ap.add_argument("--box", type=int, default=5, help="mutation box (phase B)")
    ap.add_argument("--seed-base", type=int, default=0, help="mutation rng seed base")
    ap.add_argument("--min-mv", type=int, default=19, help="min mixed volume (B)")
    ap.add_argument("--lx", type=int, default=20, help="phase B screen Lx")
    ap.add_argument("--ly", type=int, default=22, help="phase B screen Ly")
    args = ap.parse_args()

    done = load_progress()
    rng = random.Random(args.seed_base * 1000 + args.shard)

    if args.phase == "A":
        items = phase_a_items()
        items = [it for i, it in enumerate(items) if i % args.nshards == args.shard]
    else:
        # mutation walk around the B5 seeds (k>=29 family; the k=18 TILE4
        # line needs d>=32 to advance, handled by a separate pass if ever)
        items = []
        seen_keys = load_seen_keys()
        parents = [("B5-29", SEED_PAIRS["B5-29"]), ("B5-32", SEED_PAIRS["B5-32"])]
        n_generated = 0
        while n_generated < args.max_items:
            ptag, (Pf, Pg) = parents[rng.randrange(len(parents))]
            mv = mutate(Pf, Pg, args.box, rng)
            if mv is None:
                continue
            A, B = mv
            key = min(orbit_keys([tuple(p) for p in A], [tuple(p) for p in B]))
            kj = json.dumps(key, separators=(",", ":"))
            if kj in seen_keys:
                continue
            seen_keys.add(kj)
            register_key(kj)
            import surrogate as _s
            if _s.mixed_volume([tuple(p) for p in A],
                               [tuple(p) for p in B]) < args.min_mv:
                n_generated += 1
                continue
            # screen size: configurable, default the 21x22 winner size
            Lx, Ly = args.lx, args.ly
            items.append(("B", ptag + "-mut", A, B, Lx, Ly))
            n_generated += 1

    ran = 0
    t0 = time.time()
    for item in items:
        if ran >= args.max_items:
            break
        k1 = item_key(item, "r1")
        if k1 in done:
            continue
        try:
            rec, HX, HZ = run_item(item, "r1", *RUNG1)
        except Exception as e:  # never die mid-sweep: log and continue
            append_jsonl(PROGRESS, {"key": k1, "error": repr(e)[:200],
                                    "ts": time.time()})
            ran += 1
            continue
        append_jsonl(PROGRESS, rec)
        # rung 2 on screen advances
        if rec.get("verdict") == "advance-screen":
            k2 = item_key(item, "r2")
            if k2 not in done:
                rec2, _, _ = run_item(item, "r2", *RUNG2)
                append_jsonl(PROGRESS, rec2)
        ran += 1
        if ran % 5 == 0:
            print(f"shard {args.shard}: {ran} items, {time.time()-t0:.0f}s",
                  flush=True)
    print(f"shard {args.shard} done: {ran} items in {time.time()-t0:.0f}s",
          flush=True)


if __name__ == "__main__":
    main()
