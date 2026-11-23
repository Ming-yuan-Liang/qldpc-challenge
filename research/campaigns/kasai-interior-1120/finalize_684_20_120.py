"""Assemble the 684-20-106 submission draft from the 120 ladder verdict.

Claim d=106 = lightest witnessed reading (rung10, 8M fast pd10, seed 92030).
distance.X = replay-recovered X-type witness (w=106) — ground truth rule:
distance.X holds ker(HZ) (X-type) witnesses, distance.Z holds ker(HX)
(Z-type) witnesses. distance.Z = hunt witness (hunt-ztype-94-88005.json,
Z-type w=120). Schema fixes baked in (0.2 / no family / no search_budget /
origin=submission / tool <= 67 chars).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
CAND = HERE.parents[1] / "candidates" / "a1-kasai-1120"

doc = json.loads((CAND / "684-20-120.json").read_text(encoding="utf-8"))
rep = json.loads((HERE / "replay-684-20-120-seed92030.json").read_text(encoding="utf-8"))
hunt = json.loads((HERE / "hunt-ztype-94-88005.json").read_text(encoding="utf-8"))

assert rep["weight"] == 106 and len(rep["support"]) == 106, rep
assert hunt["weight"] == 120 and len(hunt["support"]) == 120, hunt

DATE = "2026-11-22"
doc["name"] = "[[684,20,106]]"
doc["distance"] = {
    "d": 106,
    "X": {"value": 106, "confidence": "upper_bound",
          "witness": rep["support"],
          "witness_provenance": {
              "found_by": ["@Ming-yuan-Liang"], "date": DATE,
              "found_at_samples": rep["trials"],
              "survived_samples": rep["trials"],
              "tool": (f"distance_rand gf2_fast 8M trials pd{rep['pair_depth']}, "
                       f"seed {rep['seed']} (replay-verified)"),
              "seeds": [rep["seed"]]}},
    "Z": {"value": 120, "confidence": "upper_bound",
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
out = CAND / "684-20-106.json"
out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
print("wrote", out, "| d=106 (X=106 replay seed 92030, Z=120 hunt seed 88005)")
