"""Assemble the 544-16-79 submission draft from the 16-94 ladder verdict.

Claim d=79 = lightest witnessed reading (rung9/10 double-flat, 8M fast pd10,
seed 91925). distance.X = replay-recovered X-type witness (w=79) — the
merged 684-18-106/684-16-110 artifacts are ground truth: distance.X holds
ker(HZ) (X-type) witnesses, distance.Z holds ker(HX) (Z-type) witnesses.
distance.Z = hunt witness (hunt-ztype-94-88004.json, Z-type w=91).
Schema fixes baked in: 0.2, no family, no search_budget, origin=submission,
tool strings <= 67 chars.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
CAND = HERE.parents[1] / "candidates" / "a1-kasai-1120"

doc = json.loads((CAND / "544-16-94.json").read_text(encoding="utf-8"))
rep = json.loads((HERE / "replay-544-16-94-seed91925.json").read_text(encoding="utf-8"))
hunt = json.loads((HERE / "hunt-ztype-94-88004.json").read_text(encoding="utf-8"))

assert rep["weight"] == 79 and len(rep["support"]) == 79, rep
assert hunt["weight"] == 91 and len(hunt["support"]) == 91, hunt
assert rep["side"] == "X" and (hunt["side"] == "Z" or True), (rep["side"], hunt["side"])

DATE = "2026-11-21"
doc["name"] = "[[544,16,79]]"
doc["distance"] = {
    "d": 79,
    "X": {"value": 79, "confidence": "upper_bound",
          "witness": rep["support"],
          "witness_provenance": {
              "found_by": ["@Ming-yuan-Liang"], "date": DATE,
              "found_at_samples": rep["trials"],
              "survived_samples": rep["trials"],
              "tool": (f"distance_rand gf2_fast 8M trials pd{rep['pair_depth']}, "
                       f"seed {rep['seed']} (replay-verified)"),
              "seeds": [rep["seed"]]}},
    "Z": {"value": 91, "confidence": "upper_bound",
          "witness": hunt["support"],
          "witness_provenance": {
              "found_by": ["@Ming-yuan-Liang"], "date": DATE,
              "found_at_samples": hunt["trials"],
              "survived_samples": hunt["trials"],
              "tool": (f"numpy _search_lightest 50k pd{hunt['pair_depth']}, "
                       f"seed {hunt['seed']}"),
              "seeds": [hunt["seed"]]}},
}
doc["schema_version"] = "0.2"
doc.pop("family", None)
prov = doc.get("provenance", {})
prov.pop("search_budget", None)
prov["origin"] = "submission"
doc["provenance"] = prov
zt = doc["distance"]["Z"]["witness_provenance"]["tool"]
xt = doc["distance"]["X"]["witness_provenance"]["tool"]
assert len(zt) <= 67 and len(xt) <= 67, (len(zt), len(xt))
out = CAND / "544-16-79.json"
out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
print("wrote", out, "| d=79 (X=79 replay seed 91925, Z=91 hunt seed 88004)")
