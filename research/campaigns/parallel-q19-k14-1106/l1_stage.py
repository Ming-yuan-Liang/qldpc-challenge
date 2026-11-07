"""Stage flat deep-reading survivors of the q19-k14 RESUME lane (L1).

Resume of lane q19-k14 (campaign parallel-q19-k14-1106) by search lane
l1-q19-resume: same draws (bench_one.draw_pair, base seed 20261106), same
deep protocol (3+ fresh-seed rungs x 20,000 trials/side, chunked per
deep_unit.py). Staging dir pinned to research/candidates/l1-q19-resume/.

A draw is stageable iff its deep rungs agree flat (same lightest weight) on
at least 3 distinct seeds, and the claim is the lightest reading across ALL
of the draw's rungs (never above it). Packaged at the per-side lightest
witness across the rungs via submit.make_submission + coordination.unique_path;
the gate is run separately (coordination.py gate <path>).

Provenance note (inherited from stage_flat.py): make_submission records
``seeds: [seed], [seed+1]`` from its ``seed=`` argument, but the per-side
lightest witnesses can come from different rungs, so the script rewrites each
side's ``seeds`` to the deep seed that actually produced that side's witness.

Usage: python l1_stage.py <draw_index>[,<draw_index>...]
"""
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Pin this lane's staging dir: research/candidates/l1-q19-resume/
os.environ["QLDPC_RUN_ID"] = "l1-q19-resume"

from bench_one import draw_pair  # noqa: E402
from bbga_labels import build_2bga_affine  # noqa: E402
from coordination import staging_dir, unique_path  # noqa: E402
from submit import make_submission, save_submission  # noqa: E402

AUTHOR = "@Ming-yuan-Liang"
TRIALS = 20000
MIN_RUNGS = 3


def deep_records(i):
    """All rung-final records for draw i across every deep JSONL checkpoint."""
    out = []
    for p in sorted(glob.glob(os.path.join(_HERE, f"deep_{i}_*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    if r.get("status") == "final":
                        out.append(r)
    return out


def stage(i):
    recs = deep_records(i)
    seeds = sorted(r["seed"] for r in recs)
    if len(recs) < MIN_RUNGS or len(set(seeds)) < MIN_RUNGS:
        return None, (f"draw {i}: expected >= {MIN_RUNGS} deep records, "
                      f"got {len(recs)}")
    claim = min(r["reading"] for r in recs)
    flat = [r for r in recs if r["reading"] == claim]
    flat_seeds = sorted({r["seed"] for r in flat})
    if len(flat_seeds) < MIN_RUNGS:
        return None, (f"draw {i}: only {len(flat_seeds)} rung(s) flat at the "
                      f"lightest reading {claim} (seeds {seeds}, readings "
                      f"{[r['reading'] for r in recs]})")
    # per-side lightest witness across the flat rungs (tie: earliest seed)
    xr = min(flat, key=lambda r: (r["wx"], r["seed"]))
    zr = min(flat, key=lambda r: (r["wz"], r["seed"]))
    wx, xwit, xseed = xr["wx"], xr["xwit"], xr["seed"]
    wz, zwit, zseed = zr["wz"], zr["zwit"], zr["seed"]
    if min(wx, wz) != claim:
        return None, (f"draw {i}: per-side bests ({wx},{wz}) inconsistent "
                      f"with claimed reading {claim}")
    if wx > claim or wz > claim:
        return None, (f"draw {i}: a side's lightest witness ({wx},{wz}) is "
                      f"heavier than the claimed reading {claim}; claim must "
                      f"not exceed the lightest reading")

    w, a, b = draw_pair(i)
    HX, HZ = build_2bga_affine(19, a, b)
    doc = make_submission(
        HX, HZ, name="placeholder (renamed below once k is recomputed)",
        construction="", authors=[AUTHOR], family="generalized-bicycle",
        confidence="upper_bound",
        witnesses=(wx, xwit, wz, zwit), trials=TRIALS, seed=xseed)
    k = doc["k"]
    doc["distance"]["X"]["witness_provenance"]["seeds"] = [int(xseed)]
    doc["distance"]["Z"]["witness_provenance"]["seeds"] = [int(zseed)]
    doc["name"] = f"[[684,{k},{claim}]] Kasai affine 2BGA Aff(F_19)"
    doc["provenance"].update(
        construction=(
            f"2BGA on the metacyclic realization of Aff(F_19) (Z_19 x| Z_18, "
            f"primitive root 2 acting; Kasai's affine-coset structure): "
            f"weight-{w} random exponent seeds, |a| = |b| = {w}, exponents "
            f"uniform in [0, 342) (campaign draw index {i}). Distance is a "
            f"20,000-trial randomized-information-set (RIS) upper bound per "
            f"side, flat at {claim} across {len(flat_seeds)} fresh seeds "
            f"({', '.join(str(s) for s in flat_seeds)}); the packaged "
            f"witnesses are the lightest per side across those rungs."),
        notes=(f"Lane l1-q19-resume (resume of q19-k14, campaign "
               f"parallel-q19-k14-1106) of the 2026-11-06 parallel portfolio; "
               f"first screened at 400 RIS trials. Honest upper_bound claim "
               f"at the lightest reading; certification pending server "
               f"distance gate."))
    params = {"q": 19, "a": a, "b": b}
    path = unique_path(
        os.path.join(staging_dir(), f"684-{k}-{claim}.json"), doc)
    save_submission(doc, path,
                    spec={"constructor": "bbga_labels.build_2bga_affine",
                          "params": params})
    return (path, claim, k), None


def main():
    results = []
    for tok in sys.argv[1].split(","):
        i = int(tok)
        try:
            ok, err = stage(i)
        except Exception as e:  # noqa: BLE001 - record the refusal, keep going
            ok, err = None, f"draw {i}: {type(e).__name__}: {e}"
        if err:
            print(f"SKIP {err}", flush=True)
            with open(os.path.join(_HERE, "l1_stage_log.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(json.dumps({"i": i, "ok": False, "why": err}) + "\n")
        else:
            path, claim, k = ok
            print(f"STAGED draw {i}: [[684,{k},{claim}]] -> {path}", flush=True)
            with open(os.path.join(_HERE, "l1_stage_log.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(json.dumps({"i": i, "ok": True, "k": k, "d": claim,
                                    "path": path}) + "\n")
            results.append((i, path))
    print(json.dumps({"staged": [str(p) for _, p in results]}))


if __name__ == "__main__":
    main()
