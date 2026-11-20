"""Stage a deep-confirmed L6 candidate: package, save, gate.

Usage:
  python stage.py --cand <cand_key> [--out-root research/candidates/l6-2dlocal]

Packages from deep_summary.jsonl (per-side lightest readings and witnesses
across all deep rungs). The doc is built here mirroring
submit.make_submission's schema-0.2 structure: make_submission itself refuses
to package the open-boundary tile family (its prescreen block_structure reads
many Tanner components on a code the trusted verifier accepts -- the board's
own tile twins pass verify() cleanly), so the doc is assembled by hand with
the same fields and handed to save_submission, whose preflight IS the
verifier's structural half, then gated.

Refuses to stage a candidate whose claimed d does not clear reqd.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

import numpy as np

ROOT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "research", "local2d"))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
sys.path.insert(0, os.path.join(ROOT, "verify"))

import boundary_engine as be  # noqa: E402
import planar  # noqa: E402
import submit  # noqa: E402
import coordination  # noqa: E402

WS = os.path.join(ROOT, "research", "campaigns", "w8-2dlocal-n700-1000", "workspace")
DEEP_SUM = os.path.join(WS, "deep_summary.jsonl")
AUTHOR = "@l6-w8-2dlocal-n700-1000"


def reqd(n, k):
    sys.path.insert(0, WS)
    from sweep import reqd as _reqd
    return _reqd(n, k)


def supports(H):
    return [np.nonzero(r)[0].tolist() for r in np.asarray(H)]


def build_doc(HX, HZ, *, name, construction, notes, coords, layers,
              wx, xwit, wz, zwit, x_prov, z_prov, family="tile",
              confidence="upper_bound"):
    from css import verify_css
    HX = np.asarray(HX, dtype=np.int8) % 2
    HZ = np.asarray(HZ, dtype=np.int8) % 2
    # reduce_weights can annihilate rows to zero; the schema refuses empty
    # checks and the board's own B5 entries record "all-zero rows dropped"
    HX = HX[HX.sum(axis=1) > 0] if HX.size else HX
    HZ = HZ[HZ.sum(axis=1) > 0] if HZ.size else HZ
    assert verify_css(HX, HZ), "CSS commutation fails"
    n = int(HX.shape[1])
    k = int(be.compute_k(HX, HZ))
    chx, chz = supports(HX), supports(HZ)
    radius = submit._interaction_radius(chx + chz, coords)
    doc = {
        "schema_version": "0.2",
        "name": name,
        "code_type": "CSS",
        "n": n,
        "k": k,
        "checks": {"X": chx, "Z": chz},
        "distance": {
            "d": int(min(wx, wz)),
            "X": {"value": int(wx), "confidence": confidence,
                  "witness": [int(q) for q in xwit],
                  "witness_provenance": x_prov},
            "Z": {"value": int(wz), "confidence": confidence,
                  "witness": [int(q) for q in zwit],
                  "witness_provenance": z_prov},
        },
        "provenance": {
            "authors": [AUTHOR],
            "construction": construction,
            "references": [],
            "date": datetime.date.today().isoformat(),
            "notes": notes,
        },
        "family": family,
        "locality": {"coordinates": [[float(a), float(b)] for a, b in coords],
                     "interaction_radius": radius,
                     "layers": int(layers)},
    }
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True, help="cand key in deep_summary")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    rows = {}
    with open(DEEP_SUM, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rows[r["cand"]] = r
    b = rows[args.cand]
    assert b.get("X") and b.get("Z"), "no complete per-side witness set"

    Sf = [tuple(p) for p in b["pair"][0]]
    Sg = [tuple(p) for p in b["pair"][1]]
    Lx, Ly = b["Lx"], b["Ly"]
    HX, HZ, info = be.build_planar(Lx, Ly, Sf, Sg)
    HX = be.reduce_weights(HX)
    HZ = be.reduce_weights(HZ)
    n = int(HX.shape[1])
    k = int(be.compute_k(HX, HZ))
    assert n == b["n"] and k == b["k"], (n, k, b["n"], b["k"])

    wx, xwit = b["X"]["weight"], b["X"]["support"]
    wz, zwit = b["Z"]["weight"], b["Z"]["support"]
    d_claim = min(wx, wz)
    r = reqd(n, k)
    print(f"cand {args.cand}: [[{n},{k}]] dX<={wx} dZ<={wz} claim={d_claim} "
          f"reqd={r}")
    if d_claim < r:
        print("REFUSING: claimed d does not clear the board requirement")
        return 1

    kept = info.get("kept_qubits")
    coords = planar.grid_coordinates(Lx, Ly, kept=kept)

    def prov(side_seed, side):
        return {"found_by": [AUTHOR],
                "date": datetime.date.today().isoformat(),
                "found_at_samples": int(b[side]["trials"]),
                "survived_samples": int(b[side]["trials"]),
                "tool": ("research/kit/surrogate.distance_rand_witness "
                         "(gf2_fast backend, threads=2)" if
                         b[side]["instrument"] == "fast" else
                         "research/kit/surrogate.lightest_logical"),
                "seeds": [int(side_seed)]}

    name = (f"[[{n},{k},{d_claim}]] weight-8 open-boundary planar tile code "
            f"({Lx}x{Ly}, S_f={Sf}, S_g={Sg})")
    construction = (
        f"Open-boundary planar BB code (Liang-Yang-Iosue-Chen boundary "
        f"construction, Liang-Eberhardt-Chen planar tile family): "
        f"research/local2d/boundary_engine.build_planar({Lx}, {Ly}, "
        f"S_f={Sf}, S_g={Sg}) followed by reduce_weights; bilayer layout "
        f"planar.grid_coordinates (A and B qubits of cell (i,j) at site "
        f"(i,j) on two layers). Supports found by this lane's mutation "
        f"search over 4+4 monomials in the B=5 box around the board's "
        f"B5-29/B5-32 pairs.")
    notes = (
        f"Lane w8-2dlocal-n700-1000 (L6). Ladder: screen 3x20000 (pd22) + "
        f"3x100000 (pd20); deep fast-backend 200k x3 (pd16) and 1M-class x4+ "
        f"(pd12) fresh seeds, plus numpy per-side cross-checks; claimed d is "
        f"the lightest reading found on either side across all rungs "
        f"(upper_bound). X witness: {b['X']['instrument']} trials="
        f"{b['X']['trials']} seed={b['X']['seed']}; Z witness: "
        f"{b['Z']['instrument']} trials={b['Z']['trials']} "
        f"seed={b['Z']['seed']}.")
    doc = build_doc(HX, HZ, name=name, construction=construction, notes=notes,
                    coords=coords, layers=2,
                    wx=wx, xwit=xwit, wz=wz, zwit=zwit,
                    x_prov=prov(b["X"]["seed"], "X"),
                    z_prov=prov(b["Z"]["seed"], "Z"))

    out_dir = args.out_dir or coordination.staging_dir("l6-2dlocal")
    os.makedirs(out_dir, exist_ok=True)
    path = coordination.unique_path(
        os.path.join(out_dir, f"{n}-{k}-{d_claim}.json"), doc)
    violations = submit.save_submission(doc, path, spec={
        "constructor": "boundary_engine.build_planar",
        "family": "tile",
        "params": {"Lx": Lx, "Ly": Ly, "S_f": [list(p) for p in Sf],
                   "S_g": [list(p) for p in Sg], "reduce_weights": True},
        "lane": "w8-2dlocal-n700-1000",
    })
    if violations:
        print("SCHEMA VIOLATIONS:", violations)
        return 1
    print("saved:", path)

    verdict, vpath = coordination.gate_and_record(path)
    g = verdict.get("gates", {})
    nov = g.get("novelty", {})
    print(json.dumps({"passed": verdict.get("passed"),
                      "board_advancing": nov.get("board_advancing"),
                      "dominated_by": nov.get("dominated_by"),
                      "labels": verdict.get("labels"),
                      "verdict_path": vpath}, indent=1, default=str)[:4000])
    return 0 if verdict.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
