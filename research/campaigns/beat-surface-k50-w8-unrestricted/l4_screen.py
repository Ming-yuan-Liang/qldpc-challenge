"""L4 screening driver: cyclic-GB codes, k 45-55, staged dominance funnel.

Funnel per candidate (rejection is sound at every stage because
distance_rand readings are UPPER bounds and dominance is monotone in d):
  stage 1 (200 trials)  -> optimistic dominance check; dominated => reject
  stage 2 (2000 trials) -> recheck at min reading
  stage 3 (20000 trials, witness captured) -> promising record
Checkpointed to a ledger JSON after every chunk (one chunk = one m).

Usage:
  python -I l4_screen.py --track w8 --seed 51001 --minutes 70
Tracks: w8 (weight 4+4), w5 (2+3), w4 (2+2). m menus come from l4_m_menu.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

KIT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge\research\kit"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
sys.path.insert(0, HERE)

from css import compute_k  # noqa: E402
from search import fingerprint, sample_cyclic_gb, sample_metacyclic  # noqa: E402
from surrogate import distance_rand, distance_rand_witness, prepare_distance_search  # noqa: E402
from prescreen import block_structure  # noqa: E402
import gf2poly  # noqa: E402
from l4_board import Board  # noqa: E402

WEIGHTS = {"w8": (4, 4), "w5": (2, 3), "w4": (2, 2)}
M_RANGE = {"w8": (151, 499), "w5": (151, 499), "w4": (151, 499)}
STAGES = (200, 2000, 20000)


def m_produces(m, wband, attempts=6):
    """Bounded dry-run: can this m yield one in-band candidate?

    Mirrors sample_cyclic_gb's mechanics without its unbounded
    `while built < num` loop (which spins forever on an m whose factor
    degrees cannot realize the k band, starving the driver's deadline
    check). Guards the chunk loop against deg-28-only style m values.
    """
    import random as _random
    prng = _random.Random(777 + m)
    rng = np.random.default_rng(999 + m)
    facs = gf2poly.factor_squarefree(gf2poly.x_pow_m_minus_1(m), prng)
    for _ in range(attempts):
        g = gf2poly.designed_divisor(facs, (22, 27), prng)
        if g is None:
            return False
        words = gf2poly.sparse_multiples(m, g, wband, rng, trials=120)
        if len(words) < 2:
            continue
        for i in range(min(8, len(words))):
            for j in range(i + 1, min(8, len(words))):
                a, b = list(words[i]), list(words[j])
                if 45 <= gf2poly.designed_k(m, a, b) <= 55:
                    return True
    return False


def load_ledger(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"records": [], "promising": [], "tally": {}, "fps": []}


def save_ledger(path, led):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(led, f)
    os.replace(tmp, path)


def tally(led, key):
    led["tally"][key] = led["tally"].get(key, 0) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=list(WEIGHTS) + ["2bga4"], required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--per-m", type=int, default=24,
                    help="candidates to draw per m before rotating")
    ap.add_argument("--m-lo", type=int, default=None)
    ap.add_argument("--m-hi", type=int, default=None)
    ap.add_argument("--stages", default="200,2000,20000")
    args = ap.parse_args()
    stages = tuple(int(x) for x in args.stages.split(","))

    if args.track == "2bga4":
        good_m = list(range(150, 501))    # group orders; n_code = 2*order
    else:
        with open(os.path.join(HERE, "l4_m_menu.json"), encoding="utf-8") as f:
            menu = json.load(f)
        lo, hi = M_RANGE[args.track]
        if args.m_lo is not None:
            lo = args.m_lo
        if args.m_hi is not None:
            hi = args.m_hi
        good_m = sorted(m for m in range(lo, hi + 1, 2)
                        if menu.get(str(m), {}).get("ok"))
        if not good_m:
            print("no feasible m in range; exit")
            return 1
        good_m = [m for m in good_m if m_produces(m, WEIGHTS[args.track])]
        if not good_m:
            print("no producing m in range; exit")
            return 1
    # rotate the menu deterministically by seed
    rng_order = np.random.default_rng(args.seed)
    order = list(good_m)
    rng_order.shuffle(order)

    board = Board(os.path.join(HERE, "l4_board_cache.json"))
    ledger_path = args.ledger or os.path.join(
        HERE, f"ledger_{args.track}_{args.seed}.json")
    led = load_ledger(ledger_path)
    seen = set(led.get("fps", []))
    wband = WEIGHTS.get(args.track, (2, 2))
    deadline = time.time() + args.minutes * 60
    print(f"[{args.track} seed={args.seed}] {len(order)} feasible m, "
          f"ledger={ledger_path}, deadline in {args.minutes:.0f}min", flush=True)

    mi = 0
    while time.time() < deadline and mi < len(order):
        m = order[mi]
        mi += 1
        chunk = []
        t_chunk = time.time()
        if args.track == "2bga4":
            # metacyclic 2BGA, weight-2 supports -> check weight 4; k is not
            # designed, the in-loop k filter rejects out-of-band draws
            gen = sample_metacyclic(args.per_m, order_range=(150, 500),
                                    weight=2, seed=args.seed * 1000 + mi)
        else:
            # one kit sampler instance per m: factors x^m-1 once, cheap draws
            gen = sample_cyclic_gb(args.per_m, m_range=(m, m), weight=wband,
                                   k_band=(45, 55), seed=args.seed * 1000 + m,
                                   trials_per_ideal=120)
        n_drawn = 0
        for spec, HX, HZ in gen:
            n_drawn += 1
            if n_drawn % 4 == 0:
                print(f"  [m={m}] draw {n_drawn}/{args.per_m} "
                      f"({time.time()-t_chunk:.0f}s)", flush=True)
            if time.time() > deadline:
                break
            n = int(HX.shape[1])
            k = int(compute_k(HX, HZ))
            w = int(max(HX.sum(1).max(), HZ.sum(1).max()))
            fp = fingerprint(HX, HZ)
            if fp in seen:
                tally(led, "dup_in_run")
                continue
            seen.add(fp)
            if not block_structure(HX, HZ)["connected"]:
                tally(led, "disconnected")
                continue
            if k < 45 or k > 55:
                tally(led, "k_out_of_band")
                continue
            prep = prepare_distance_search(HX, HZ)
            rec = {"spec": spec, "n": n, "k": k, "w": w, "fp": fp,
                   "track": args.track, "seed": args.seed}
            best = None
            for si, trials in enumerate(stages):
                if si > 0:
                    print(f"    ->stage{si + 1} [[{n},{k},{best}]] w={w} "
                          f"m={m}", flush=True)
                wit = distance_rand_witness(HX, HZ, trials=trials,
                                            seed=args.seed + si * 7919
                                            + int(fp[:8], 16),
                                            prepared=prep)
                d = int(wit.weight) if wit else 10 ** 9
                best = d if best is None else min(best, d)
                rec[f"d{trials}"] = best
                if wit:
                    rec[f"wit{trials}"] = {"side": wit.side,
                                           "support": wit.support}
                if best == 10 ** 9:
                    tally(led, "no_logical")
                    break
                dom, adv = board.verdict(n, k, best, w)
                if dom:
                    # dominated even at the optimistic bound: sound reject
                    tally(led, f"rejected_stage{si + 1}")
                    rec["status"] = f"dominated@stage{si + 1}"
                    rec["dominators_head"] = dom[:2]
                    break
                if si == len(stages) - 1:
                    rec["status"] = "promising"
                    rec["dominators"] = dom
                    rec["advances_n"] = len(adv)
                    rec["advances_head"] = adv[:4]
                    led["promising"].append(rec)
                    print(f"  PROMISING [[{n},{k},{best}]] w={w} m={m} "
                          f"adv={len(adv)} {adv[:2]}", flush=True)
            chunk.append({kk: rec[kk] for kk in rec
                          if kk not in ("spec",)})
            chunk[-1]["spec"] = rec["spec"]
            led["records"].append(rec)
            tally(led, "built")
        led["fps"] = list(seen)
        save_ledger(ledger_path, led)
        print(f"[m={m}] drawn={n_drawn} chunk_dt={time.time()-t_chunk:.0f}s "
              f"built={led['tally'].get('built',0)} "
              f"promising={len(led['promising'])}", flush=True)
        if time.time() > deadline:
            break
    save_ledger(ledger_path, led)
    print(f"done: built={led['tally'].get('built',0)} "
          f"promising={len(led['promising'])} tally={led['tally']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
