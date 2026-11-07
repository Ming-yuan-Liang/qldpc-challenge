"""PHASE 2 staging: package flat, deep-read q17 s20 survivors and gate them.

Reads p2_idx<idx>_seed<seed>.json for the given indexes (three fresh-seed
20,000-trial rungs each, chunked 5x4000). A survivor must have three rungs
whose readings agree flat (spread <= 2) at the lightest reading; the doc is
packaged AT the lightest reading with witnesses embedded (CI-refutation
lesson: the claim must equal the lowest reading).

Per-side witnesses: the rung chunks record the lighter side only, so the
stager collects the best X-side and Z-side operators across every chunk of
every rung of that candidate. A side no chunk ever returned is searched fresh
(lightest_logical, 20,000 trials, fresh seed) rather than left unwitnessed.

    python phase2_stage.py <idx> [<idx> ...]

Stages under QLDPC_RUN_ID's staging dir (research/candidates/<run_id>/) and
gates each staged doc. Nothing here is a submission.
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "research", "kit"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from bbga_labels import build_2bga_affine
from coordination import gate_and_record, staging_dir, unique_path
from submit import make_submission, save_submission
from surrogate import lightest_logical

AUTHOR = "@Ming-yuan-Liang"
FLAT_SPREAD = 2


def rung_json(idx, seed):
    path = os.path.join(_HERE, f"p2_idx{idx}_seed{seed}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def side_best(chunks, side):
    best = None
    for c in chunks:
        if c["side"] == side and c["weight"] is not None and c["support"]:
            if best is None or c["weight"] < best["weight"]:
                best = c
    return best


def main():
    idxs = [int(x) for x in sys.argv[1:]]
    rc = 0
    for idx in idxs:
        seeds = [10000 + idx, 20000 + idx, 30000 + idx]
        rungs = [rung_json(idx, s) for s in seeds]
        if any(r is None for r in rungs):
            print(f"idx {idx}: missing rung JSONs {[s for s, r in zip(seeds, rungs) if r is None]}; skip", flush=True)
            rc = 1
            continue
        readings = [r["weight"] for r in rungs]
        if any(w is None for w in readings):
            print(f"idx {idx}: a rung found no logical; skip", flush=True)
            rc = 1
            continue
        lightest = min(readings)
        spread = max(readings) - lightest
        print(f"idx {idx}: rung readings {dict(zip(seeds, readings))} "
              f"lightest {lightest} spread {spread}", flush=True)
        if spread > FLAT_SPREAD:
            print(f"idx {idx}: rungs not flat (spread {spread} > "
                  f"{FLAT_SPREAD}); NOT staging", flush=True)
            rc = 2
            continue

        spec = rungs[0]["spec"] if "spec" in rungs[0] else None
        q, a, b = rungs[0]["q"], rungs[0]["a"], rungs[0]["b"]
        n, k = rungs[0]["n"], rungs[0]["k"]

        all_chunks = []
        for r in rungs:
            with open(os.path.join(_HERE, f"p2_idx{idx}_seed{r['seed']}.json.progress"),
                      encoding="utf-8") as f:
                all_chunks.extend(json.load(f)["chunks"])

        HX, HZ = build_2bga_affine(q, a, b)
        HX = np.asarray(HX, dtype=np.int8) % 2
        HZ = np.asarray(HZ, dtype=np.int8) % 2

        wit = {}
        chunk_meta = {}
        for side in ("X", "Z"):
            c = side_best(all_chunks, side)
            if c is not None:
                wit[side] = (c["weight"], c["support"])
                chunk_meta[side] = c
        fresh = {}
        for side in ("X", "Z"):
            if side not in wit:
                w, sup = lightest_logical(
                    HX, HZ, trials=20000, seed=40000 + idx + (1 if side == "Z" else 0))
                wit[side] = (int(w), [int(x) for x in sup])
                fresh[side] = True
                print(f"idx {idx}: no chunk witness on {side}; fresh search "
                      f"read {side}<={w}", flush=True)
        wx, xwit = wit["X"]
        wz, zwit = wit["Z"]
        dval = min(wx, wz)
        print(f"idx {idx}: witnesses X<={wx} Z<={wz} -> claim d<={dval}",
              flush=True)

        doc = make_submission(
            HX, HZ,
            name=f"[[{n},{k},{dval}]] Kasai affine 2BGA Aff(F_{q}) "
                 f"(q17 directed s20 continuation)",
            construction=f"2BGA on the metacyclic realization of Aff(F_{q}) "
                         f"(Z_{q} x| Z_{q-1}, primitive root acting; Kasai's "
                         f"affine-coset structure): weight-6 random seed draw "
                         f"(a={a}, b={b}); distance is the lightest of three "
                         f"fresh-seed 20,000-trial RIS upper-bound readings "
                         f"(seeds {seeds}), upper bound.",
            authors=[AUTHOR], family="generalized-bicycle",
            confidence="upper_bound", trials=4000,
            witnesses=(wx, xwit, wz, zwit),
            notes="Continuation of research/campaigns/"
                  "kasai-affine-q17-directed-s20 (lane en2-290-1106): screen "
                  "400 trials, then three fresh-seed 20,000-trial rungs spent "
                  "in 4,000-trial checkpointed chunks per seed; claim equals "
                  "the lightest reading.")
        path = unique_path(
            os.path.join(staging_dir(), f"{n}-{k}-{dval}.json"), doc)
        # Honest per-side witness provenance: chunk-sourced witnesses were
        # found in a 4,000-trial checkpoint (tool distance_rand_witness) and
        # survived every chunk on their side across all three rungs (3 x 5 x
        # 4,000 = 60,000 samples/side); fresh-searched sides ran 20,000.
        import datetime
        total_side_samples = 20000 if not all_chunks else sum(
            c["trials"] for c in all_chunks)
        for side, wv in (("X", (wx, xwit)), ("Z", (wz, zwit))):
            if side in fresh:
                continue
            c = chunk_meta[side]
            doc["distance"][side]["witness_provenance"] = {
                "found_by": [AUTHOR],
                "date": datetime.date.today().isoformat(),
                "found_at_samples": int(c["trials"]),
                "survived_samples": int(total_side_samples),
                "tool": "research/kit/surrogate.distance_rand_witness",
                "seeds": [int(c["chunk_seed"])],
            }
        save_submission(doc, path,
                        spec={"constructor": "bbga_labels.build_2bga_affine",
                              "params": {"q": q, "a": a, "b": b}})
        print(f"idx {idx}: staged -> {path}", flush=True)
        verdict, vpath = gate_and_record(path)
        nov = verdict.get("novelty", {})
        print(json.dumps({"idx": idx, "passed": verdict.get("passed"),
                          "labels": verdict.get("labels"),
                          "board_advancing": nov.get("board_advancing"),
                          "advances_by": nov.get("advances_by"),
                          "d_only_gain": nov.get("d_only_gain"),
                          "dominated_by": nov.get("dominated_by"),
                          "verdict": str(vpath)}, indent=1), flush=True)
        if not verdict.get("passed"):
            rc = 3
    return rc


if __name__ == "__main__":
    sys.exit(main())
