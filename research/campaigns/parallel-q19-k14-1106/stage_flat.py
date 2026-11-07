"""Stage flat deep-reading survivors of the q19-k14 lane.

For each draw: read its three deep JSONL records (3 fresh seeds x 20,000
trials/side). Move on only if the three readings agree flat (same lightest
weight). Package at the per-side lightest witness across the rungs with
``submit.make_submission(witnesses=...)``, stage through
``submit.save_submission`` under this lane's staging dir, and print the path.
The gate itself is run separately with the briefing's exact command.

Provenance note: make_submission records ``seeds: [seed], [seed+1]`` from its
``seed=`` argument, but the per-side lightest witnesses can come from
different rungs, so the script rewrites each side's ``seeds`` to the deep seed
that actually produced that side's witness (structured provenance stays
truthful; the witnesses themselves are re-validated by make_submission).

Usage: python stage_flat.py <draw_index>[,<draw_index>...]
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

# Pin this lane's staging dir: research/candidates/parallel-q19-k14-1106/
os.environ["QLDPC_RUN_ID"] = "parallel-q19-k14-1106"

from bench_one import draw_pair  # noqa: E402
from bbga_labels import build_2bga_affine  # noqa: E402
from coordination import staging_dir, unique_path  # noqa: E402
from submit import make_submission, save_submission  # noqa: E402

AUTHOR = "@Ming-yuan-Liang"
TRIALS = 20000


def deep_records(i):
    """The three rung-final records for draw i (chunked JSONLs: final only)."""
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
    if len(recs) != 3 or len(set(seeds)) != 3:
        return None, f"draw {i}: expected 3 deep records, got {len(recs)}"
    readings = [r["reading"] for r in recs]
    if len(set(readings)) != 1:
        return None, (f"draw {i}: not flat, readings {readings} "
                      f"(seeds {seeds})")
    d = readings[0]
    # per-side lightest witness across the rungs (tie: earliest seed)
    xr = min(recs, key=lambda r: (r["wx"], r["seed"]))
    zr = min(recs, key=lambda r: (r["wz"], r["seed"]))
    wx, xwit, xseed = xr["wx"], xr["xwit"], xr["seed"]
    wz, zwit, zseed = zr["wz"], zr["zwit"], zr["seed"]
    if min(wx, wz) != d:
        return None, (f"draw {i}: per-side bests ({wx},{wz}) inconsistent "
                      f"with flat reading {d}")

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
    doc["name"] = f"[[684,{k},{d}]] Kasai affine 2BGA Aff(F_19)"
    doc["provenance"].update(
        construction=(
            f"2BGA on the metacyclic realization of Aff(F_19) (Z_19 x| Z_18, "
            f"primitive root 2 acting; Kasai's affine-coset structure): "
            f"weight-{w} random exponent seeds, |a| = |b| = {w}, exponents "
            f"uniform in [0, 342) (campaign draw index {i}). Distance is a "
            f"20,000-trial randomized-information-set (RIS) upper bound per "
            f"side, flat at {d} across 3 fresh seeds "
            f"({seeds[0]}, {seeds[1]}, {seeds[2]}); the packaged witnesses "
            f"are the lightest per side across those rungs."),
        notes=(f"Lane q19-k14 of the 2026-11-06 parallel portfolio; first "
               f"screened at 400 RIS trials. Honest upper_bound claim; "
               f"certification pending server distance gate."))
    params = {"q": 19, "a": a, "b": b}
    path = unique_path(
        os.path.join(staging_dir(), f"684-{k}-{d}.json"), doc)
    save_submission(doc, path,
                    spec={"constructor": "bbga_labels.build_2bga_affine",
                          "params": params})
    return (path, d), None


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
            with open(os.path.join(_HERE, "stage_log.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(json.dumps({"i": i, "ok": False, "why": err}) + "\n")
        else:
            path, d = ok
            print(f"STAGED draw {i}: d<={d} -> {path}", flush=True)
            with open(os.path.join(_HERE, "stage_log.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(json.dumps({"i": i, "ok": True, "d": d,
                                    "path": path}) + "\n")
            results.append((i, path))
    print(json.dumps({"staged": [str(p) for _, p in results]}))


if __name__ == "__main__":
    main()
