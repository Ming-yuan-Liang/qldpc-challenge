"""Scoped batch-7 doc build (42013-626 + 42014-985 + 42014-1374)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

import numpy as np
from search import sample_kasai_affine, fingerprint

OUT = ROOT / "research" / "candidates" / "a1-kasai-1120"

TRIAGE = [
    (42013, 19, 626, 684, 16, 126, "684-16-126b"),
    (42014, 17, 985, 544, 20, 92),
    (42014, 17, 1374, 544, 14, 96),
]


def gf2_rank(m):
    m = m.copy()
    r = 0
    for c in range(m.shape[1]):
        piv = None
        for i in range(r, m.shape[0]):
            if m[i, c]:
                piv = i
                break
        if piv is None:
            continue
        m[[r, piv]] = m[[piv, r]]
        for i in range(m.shape[0]):
            if i != r and m[i, c]:
                m[i] ^= m[r]
        r += 1
    return r


def supports(m):
    return [np.flatnonzero(row).tolist() for row in m]


def regen(seed, q, want_idx):
    for i, (spec, HX, HZ) in enumerate(sample_kasai_affine(
            want_idx + 1, q_range=(q, q), weight=8, seed=seed)):
        if i == want_idx:
            return spec, np.asarray(HX), np.asarray(HZ)
    raise SystemExit(f"draw {want_idx} not reached for seed {seed}")


def main():
    for t in TRIAGE:
        seed, q, idx, n, k, d = t[:6]
        slug_ov = t[6] if len(t) > 6 else None
        spec, HX, HZ = regen(seed, q, idx)
        n2 = HX.shape[1]
        kk = n2 - gf2_rank(HX) - gf2_rank(HZ)
        fp = fingerprint(HX, HZ)
        assert n2 == n and kk == k, f"{seed}-{idx}: got n={n2} k={kk}, want {n},{k}"
        slug = slug_ov or f"{n}-{k}-{d}"
        doc = {
            "schema_version": "0.3",
            "name": f"[[{n},{k},{d}]] Kasai affine 2BGA Aff(F_{q}) A1-1120 screen reading",
            "code_type": "CSS",
            "n": n, "k": k,
            "checks": {"X": supports(HX), "Z": supports(HZ)},
            "distance": {"d": d,
                         "confidence": "provisional_fast_screen_instrument"},
            "provenance": {
                "authors": ["@Ming-yuan-Liang"],
                "construction": (
                    f"Kasai affine 2BGA over Aff(F_{q}) (metacyclic "
                    f"Z_{q} x| Z_{q-1}), two-block group algebra; |a|=|b|=8 "
                    f"(check weight 16); a={spec['a']}, b={spec['b']}; "
                    f"draw seed {seed} idx {idx}"),
                "date": "2026-11-22",
                "model": "GLM-5.3-Flash",
                "origin": "research",
                "search_budget": {
                    "candidates_screened": 2000,
                    "tool": f"interior_sweep.py fast screen seed {seed}",
                    "ris_trials_per_side": 1000,
                },
            },
            "family": "generalized-bicycle",
        }
        fp_ok = fp == json.loads(next(
            l for l in (HERE / f"screened_q{q}_w8_s{seed}.jsonl")
            .read_text(encoding="utf-8").splitlines()
            if json.loads(l)["spec"]["draw_id"] == f"{seed}-{idx}"
        ))["fingerprint"]
        path = OUT / f"{slug}.json"
        path.write_text(json.dumps(doc, indent=1), encoding="utf-8")
        print(f"{slug}: n={n} k={k} screen-d={d} fingerprint-match={fp_ok}", flush=True)


if __name__ == "__main__":
    main()
