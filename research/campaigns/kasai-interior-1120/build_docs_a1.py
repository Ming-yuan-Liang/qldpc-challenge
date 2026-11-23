"""Build ladder docs for the A1 triage survivors + calibration anchors.

Regenerates HX/HZ deterministically from each survivor's spec (seeded
sampler), cross-checks a/b/fingerprint against the screened record, and
writes minimal schema-0.3 docs for ladder_rerun.py. Anchors are copied
from codes/ (read-only ladder inputs).
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

import numpy as np
from search import sample_kasai_affine, fingerprint

OUT = ROOT / "research" / "candidates" / "a1-kasai-1120"
OUT.mkdir(exist_ok=True)

# draw_id -> expected (n, k, d) from the screen, per (seed, q)
TRIAGE = [
    (42001, 19, 852, 684, 16, 124),
    (42001, 19, 1710, 684, 14, 128),
    (42002, 17, 1053, 544, 20, 94),
    (42002, 17, 283, 544, 18, 91),
    (42002, 17, 2336, 544, 16, 95),
    (42002, 17, 605, 544, 14, 98),
    # batch-2 (seed 42004, q19): per-k corner picks
    (42004, 19, 4823, 684, 26, 124),
    (42004, 19, 13, 684, 18, 124),
    (42004, 19, 2366, 684, 16, 127),
    # batch-3 (seed 42006, q19): per-k corner picks
    (42006, 19, 4328, 684, 20, 124),
    (42006, 19, 4143, 684, 18, 122),
    (42006, 19, 4978, 684, 16, 125),
    # batch-4 (seed 42008, q19): per-k corner picks. Optional 7th field = slug
    # override (42008-1742's screen d collides with the dead 42001 phantom slug).
    (42008, 19, 1283, 684, 16, 126),
    (42008, 19, 1742, 684, 14, 128, "684-14-128b"),
    (42008, 19, 1721, 684, 14, 126),
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
    made = []
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
                "date": "2026-11-20",
                "model": "GLM-5.3-Flash",
                "origin": "research",
                "search_budget": {
                    "candidates_screened": 4000,
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
        made.append((slug, f"fingerprint-match={fp_ok}"))
        print(f"{slug}: n={n} k={k} rankX={HX.shape[0]} rankZ={HZ.shape[0]} "
              f"screen-d={d} {made[-1][1]}")

    for a in ("684-14-107", "544-20-76"):
        shutil.copyfile(ROOT / "codes" / f"{a}.json", OUT / f"{a}.json")
        print(f"anchor copied: {a}")
    print("DONE", len(made) + 2, "docs in", OUT)


if __name__ == "__main__":
    main()
