"""L4 targeted spread-word search: cyclic GB, divisor-trick class, w8.

Recipe hypothesis from board entry 330-34-14 (GB over Z_165, k=34, d=14,
words "1+x^6+x^17+x^44" style): crafted sparse multiples of a designed
divisor g with wide-spread supports beat random pairings by orders of
magnitude in d. This driver draws many sparse multiples of g (deg 23-27 =>
k 45-55), ranks words by circular min-gap (spread), pairs the most spread
words, and screens each pair through the dominance funnel.

Checkpoint per (m, g) chunk. Rejections sound (upper bounds, dominance
monotone in d)."""
import argparse
import itertools
import json
import os
import random as _random
import sys
import time

import numpy as np

KIT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge\research\kit"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
sys.path.insert(0, HERE)

import gf2poly  # noqa: E402
from css import compute_k  # noqa: E402
from search import fingerprint  # noqa: E402
from surrogate import distance_rand_witness, prepare_distance_search  # noqa: E402
from prescreen import block_structure  # noqa: E402
from l4_board import Board  # noqa: E402


def min_circ_gap(word, m):
    s = sorted(e % m for e in word)
    gaps = [s[(i + 1) % len(s)] - s[i] for i in range(len(s))]
    gaps[-1] = s[0] + m - s[-1]
    return min(gaps)


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
    led["tally"][key] = led.get("tally", {}).get(key, 0) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True, help="comma list of odd m values")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--word-trials", type=int, default=400)
    ap.add_argument("--top-words", type=int, default=10)
    ap.add_argument("--min-gap", type=int, default=4)
    ap.add_argument("--pairs-per-g", type=int, default=20)
    ap.add_argument("--gs-per-m", type=int, default=6)
    ap.add_argument("--stages", default="200,2000")
    ap.add_argument("--min-d", type=int, default=13,
                    help="dominance floor hint for early reject logging")
    args = ap.parse_args()
    stages = tuple(int(x) for x in args.stages.split(","))
    ms = [int(x) for x in args.ms.split(",")]

    board = Board(os.path.join(HERE, "l4_board_cache.json"))
    ledger_path = os.path.join(HERE, f"ledger_spread_{args.seed}.json")
    led = load_ledger(ledger_path)
    seen = set(led.get("fps", []))
    deadline = time.time() + args.minutes * 60
    print(f"[spread seed={args.seed}] ms={ms} deadline {args.minutes:.0f}min",
          flush=True)

    for m in ms:
        if time.time() > deadline:
            break
        prng = _random.Random(555000 + args.seed * 100 + m)
        rng = np.random.default_rng(666000 + args.seed * 100 + m)
        facs = gf2poly.factor_squarefree(gf2poly.x_pow_m_minus_1(m), prng)
        degs = sorted(gf2poly.deg(p) for p in facs)
        t_chunk = time.time()
        built_this = 0
        for gi in range(args.gs_per_m):
            if time.time() > deadline:
                break
            g = gf2poly.designed_divisor(facs, (22, 27), prng)
            if g is None:
                tally(led, "no_divisor")
                continue
            words = gf2poly.sparse_multiples(m, g, (4, 4), rng,
                                             trials=args.word_trials)
            words = [list(w) for w in words
                     if min_circ_gap(w, m) >= args.min_gap]
            # most spread first
            words.sort(key=lambda w: -min_circ_gap(w, m))
            words = words[:args.top_words]
            if len(words) < 2:
                tally(led, "no_spread_words")
                continue
            pairs = list(itertools.combinations(range(len(words)), 2))
            rng.shuffle(pairs)
            for i, j in pairs[:args.pairs_per_g]:
                if time.time() > deadline:
                    break
                a, b = words[i], words[j]
                if not (45 <= gf2poly.designed_k(m, a, b) <= 55):
                    tally(led, "k_out_of_band")
                    continue
                HX, HZ = gf2poly.cyclic_gb(m, a, b)
                n = int(HX.shape[1])
                k = int(compute_k(HX, HZ))
                w = int(max(HX.sum(1).max(), HZ.sum(1).max()))
                fp = fingerprint(HX, HZ)
                if fp in seen:
                    tally(led, "dup")
                    continue
                seen.add(fp)
                if not block_structure(HX, HZ)["connected"]:
                    tally(led, "disconnected")
                    continue
                prep = prepare_distance_search(HX, HZ)
                rec = {"spec": {"family": "cyclic-gb-spread", "m": m,
                                "a": a, "b": b},
                       "n": n, "k": k, "w": w, "fp": fp,
                       "track": "w8-spread", "seed": args.seed}
                best = None
                for si, trials in enumerate(stages):
                    wit = distance_rand_witness(
                        HX, HZ, trials=trials,
                        seed=args.seed + si * 7919 + int(fp[:8], 16),
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
                led["records"].append(rec)
                tally(led, "built")
                built_this += 1
                if built_this % 10 == 0:
                    bests = sorted((r.get("d200", 10 ** 9)
                                    for r in led["records"]
                                    if r["spec"].get("m") == m))[:5]
                    print(f"  [m={m} g={gi}] built={built_this} "
                          f"best_d200={bests} "
                          f"({time.time()-t_chunk:.0f}s)", flush=True)
        led["fps"] = list(seen)
        save_ledger(ledger_path, led)
        print(f"[m={m}] built={built_this} "
              f"total_built={led['tally'].get('built', 0)} "
              f"promising={len(led['promising'])} "
              f"dt={time.time()-t_chunk:.0f}s", flush=True)
    save_ledger(ledger_path, led)
    print(f"done: built={led['tally'].get('built', 0)} "
          f"promising={len(led['promising'])} tally={led['tally']}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
