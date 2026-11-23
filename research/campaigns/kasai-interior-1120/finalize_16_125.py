"""Assemble the 684-16-110 submission draft from the 16-125 ladder verdict.

Claim d=110 = lightest witnessed reading (rung9, 8M fast pd10, seed 91925).
distance.Z = replay-recovered ker(HX) witness (side Z, w=110) - same call
signature and side as the merged 684-18-106 artifact's Z block (ground truth:
distance.Z holds ker(HX) witnesses, distance.X holds ker(HZ) witnesses).
distance.X = hunt witness (hunt-zside-125-88002.json, ker(HZ) w=115).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
CAND = HERE.parents[1] / "candidates" / "a1-kasai-1120"

doc = json.loads((CAND / "684-16-125.json").read_text(encoding="utf-8"))
rep = json.loads((HERE / "replay-684-16-125-seed91925.json").read_text(encoding="utf-8"))
hunt = json.loads((HERE / "hunt-zside-125-88002.json").read_text(encoding="utf-8"))

assert rep["weight"] == 110 and len(rep["support"]) == 110, rep
assert hunt["weight"] == 115 and len(hunt["support"]) == 115, hunt

DATE = "2026-11-21"
doc["name"] = "[[684,16,110]]"
doc["distance"] = {
    "d": 110,
    "X": {"value": 115, "confidence": "upper_bound",
          "witness": hunt["support"],
          "witness_provenance": {
              "found_by": ["@Ming-yuan-Liang"], "date": DATE,
              "found_at_samples": hunt["trials"],
              "survived_samples": hunt["trials"],
              "tool": (f"numpy _search_lightest 50k pd{hunt['pair_depth']}, "
                       f"seed {hunt['seed']}"),
              "seeds": [hunt["seed"]]}},
    "Z": {"value": 110, "confidence": "upper_bound",
          "witness": rep["support"],
          "witness_provenance": {
              "found_by": ["@Ming-yuan-Liang"], "date": DATE,
              "found_at_samples": rep["trials"],
              "survived_samples": rep["trials"],
              "tool": (f"distance_rand gf2_fast 8M trials pd{rep['pair_depth']}, "
                       f"seed {rep['seed']} (replay-verified)"),
              "seeds": [rep["seed"]]}},
}
out = CAND / "684-16-110.json"
out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
print("wrote", out, "| d=110 (Z=110 replay seed 91925, X=115 hunt seed 88002)")

# Normalize to the board's 0.2 artifact shape (merged 684-18-106 = ground
# truth: no family key, provenance without search_budget).
doc["schema_version"] = "0.2"
doc.pop("family", None)
prov = doc.get("provenance", {})
prov.pop("search_budget", None)
doc["provenance"] = prov
out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
print("normalized:", sorted(doc.keys()), "| prov:", sorted(prov.keys()))

# schema fixes from the first gate run: origin must be baseline|submission;
# tool strings must stay short (merged artifact's longest = 67 chars).
doc["provenance"]["origin"] = "submission"
z_tool = doc["distance"]["Z"]["witness_provenance"]["tool"]
x_tool = doc["distance"]["X"]["witness_provenance"]["tool"]
assert len(z_tool) <= 67 and len(x_tool) <= 67, (len(z_tool), len(x_tool))
out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
print("origin=submission; tool lens:", len(x_tool), len(z_tool))
