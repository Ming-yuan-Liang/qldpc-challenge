"""L4 exhaustive weight-4-codeword GB search (the 330-34-14 craft, at k 45-55).

330-34-14's provenance: "Weight-4 codewords enumerated exhaustively per
irreducible factor of x^165-1 by GF(2^m) root tests + meet-in-the-middle;
pair selected by distance screening over 40 sibling pairs."

Reproduction, generalized to the k 45-55 band (deg g in [23,27]):
  - draw designed divisors g of x^m-1 with deg g in [23,27]
  - enumerate ALL weight-4 codewords of <g> by MITM on pair-sums:
      x^i+x^j+x^k+x^l == 0 (mod g); cyclic shifts cover every word, so fix
      one support at 0: (1+x^j) == (x^k+x^l) mod g.  Table of x^e mod g,
      dict over C(m,2) pair-sums, m-1 lookups.  Complete by construction.
  - pair words (spread-ranked, capped) and screen through the dominance
    funnel (200 -> 2000 trials; rejections sound).

Checkpoint per (m, g) chunk."""
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


def poly_mod_table(m, g):
    """[x^e mod g for e in 0..m-1] as int bitsets."""
    rem = [1]
    for _ in range(1, m):
        r = rem[-1] << 1
        if (r >> gf2poly.deg(g)) & 1:
            r ^= g
        rem.append(r)
    return rem


def weight4_codewords(m, g, cap=4000):
    """All weight-4 multiples of g mod x^m-1, one representative per cyclic
    class (support contains 0). Complete enumeration by MITM."""
    rem = poly_mod_table(m, g)
    pairs = {}
    for k in range(1, m):
        rk = rem[k]
        for l in range(k + 1, m):
            v = rk ^ rem[l]
            pairs.setdefault(v, []).append((k, l))
    out = set()
    for j in range(1, m):
        v = rem[j] ^ 1      # (1 + x^j) mod g;  rem[0] = 1
        for (k, l) in pairs.get(v, ()):
            if j == k or j == l:
                continue
            out.add(tuple(sorted((0, j, k, l))))
            if len(out) >= cap:
                return sorted(out)
    return sorted(out)


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
    ap.add_argument("--ms", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--gs-per-m", type=int, default=8)
    ap.add_argument("--top-words", type=int, default=12)
    ap.add_argument("--pairs-per-g", type=int, default=40)
    ap.add_argument("--min-gap", type=int, default=3)
    ap.add_argument("--stages", default="200,2000")
    ap.add_argument("--backend", default="numpy", choices=["numpy", "fast"])
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--bias", type=int, default=0,
                    help="expected reading offset of stage-1 instrument vs "
                         "8M-class claims; promotion line = floor + bias")
    args = ap.parse_args()
    stages = tuple(int(x) for x in args.stages.split(","))
    ms = [int(x) for x in args.ms.split(",")]

    board = Board(os.path.join(HERE, "l4_board_cache.json"))
    ledger_path = os.path.join(HERE, f"ledger_mitm_{args.seed}.json")
    led = load_ledger(ledger_path)
    seen = set(led.get("fps", []))
    deadline = time.time() + args.minutes * 60
    print(f"[mitm seed={args.seed}] ms={ms} deadline {args.minutes:.0f}min",
          flush=True)

    for m in ms:
        if time.time() > deadline:
            break
        prng = _random.Random(777000 + args.seed * 100 + m)
        rng = np.random.default_rng(888000 + args.seed * 100 + m)
        facs = gf2poly.factor_squarefree(gf2poly.x_pow_m_minus_1(m), prng)
        t_chunk = time.time()
        built_this = 0
        for gi in range(args.gs_per_m):
            if time.time() > deadline:
                break
            g = gf2poly.designed_divisor(facs, (23, 27), prng)
            if g is None:
                tally(led, "no_divisor")
                continue
            words = weight4_codewords(m, g)
            if len(words) < 2:
                tally(led, f"codewords_{len(words)}")
                print(f"  [m={m} g={gi}] deg={gf2poly.deg(g)} "
                      f"weight4_codewords={len(words)}", flush=True)
                continue
            # k-filter ALL pairs of the top-spread words first (polynomial
            # gcd is ms; distance screening is seconds) — most weight-4 word
            # pairs of <g> share an extra common factor (gcd > g) and are
            # useless for the designed k band.
            words.sort(key=lambda w: -min_circ_gap(w, m))
            words = words[:args.top_words]
            dg = gf2poly.deg(g)
            valid = []
            for i, j in itertools.combinations(range(len(words)), 2):
                a, b = list(words[i]), list(words[j])
                if gf2poly.designed_k(m, a, b) == 2 * dg:
                    valid.append((a, b))
            if not valid:
                tally(led, "no_exact_gcd_pairs")
                print(f"  [m={m} g={gi}] deg={dg} codewords={len(words)} "
                      f"no exact-gcd pair", flush=True)
                continue
            # most spread pairs first (sum of the two words' min-gaps)
            valid.sort(key=lambda ab: -(min_circ_gap(ab[0], m)
                                        + min_circ_gap(ab[1], m)))
            gpairs = 0
            for a, b in valid[:args.pairs_per_g]:
                if time.time() > deadline:
                    break
                gpairs += 1
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
                rec = {"spec": {"family": "cyclic-gb-mitm", "m": m,
                                "a": a, "b": b},
                       "n": n, "k": k, "w": w, "fp": fp,
                       "track": "w8-mitm", "seed": args.seed}
                best = None
                for si, trials in enumerate(stages):
                    wit = distance_rand_witness(
                        HX, HZ, trials=trials,
                        seed=args.seed + si * 7919 + int(fp[:8], 16),
                        prepared=prep, backend=args.backend,
                        threads=args.threads)
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
                if built_this % 20 == 0:
                    bests = sorted(r.get("d200", 10 ** 9)
                                   for r in led["records"]
                                   if r["spec"]["m"] == m)[:5]
                    print(f"  [m={m} g={gi}] built={built_this} "
                          f"best_d200={bests} ({time.time()-t_chunk:.0f}s)",
                          flush=True)
            if gpairs:
                print(f"  [m={m} g={gi}] deg={gf2poly.deg(g)} "
                      f"codewords={len(words)} screened={gpairs}",
                      flush=True)
        led["fps"] = list(seen)
        save_ledger(ledger_path, led)
        print(f"[m={m}] built={built_this} "
              f"total={led['tally'].get('built', 0)} "
              f"promising={len(led['promising'])} "
              f"dt={time.time()-t_chunk:.0f}s", flush=True)
    save_ledger(ledger_path, led)
    print(f"done: built={led['tally'].get('built', 0)} "
          f"promising={len(led['promising'])} tally={led['tally']}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
