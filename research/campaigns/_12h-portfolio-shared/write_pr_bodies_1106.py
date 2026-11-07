"""Write the corrected PR bodies for the three distance-revision PRs.

Reads the frontier recheck JSON (board_recheck_1105.py output) for the
dominates/frontier lines; everything else is a deterministic edit of the
original bodies. Run after the recheck lands.
"""
import json

RECHECK = "research/campaigns/_12h-portfolio-shared/board_recheck_1105.json"
OUT = "research/candidates/pr-body-{}.md"

jobs = [
    ("684-12-117", "684-12-108", "X: d <= 121 (upper_bound), Z: d <= 108 "
     "(upper_bound)", 827515911, 31051211, 204.6),
    ("544-18-82", "544-18-76", "X: d <= 82 (upper_bound), Z: d <= 76 "
     "(upper_bound)", 1930669708, 31051212, 191.1),
    ("684-8-116", "684-8-114", "X: d <= 114 (upper_bound), Z: d <= 124 "
     "(upper_bound)", 1858076355, 31051213, 151.6),
]

recheck = {r["slug"]: r for r in json.load(open(RECHECK, encoding="utf-8"))}

for old, new, conf, gate_seed, rerun_seed, kd in jobs:
    body = open(f"research/candidates/pr-body-{old}.md",
                encoding="utf-8").read()
    body = body.replace(f"[[{old.replace('-', ',')}]]",
                        f"[[{new.replace('-', ',')}]]")
    body = body.replace(f"codes/{old}.json", f"codes/{new}.json")
    body = body.replace(f"notes/{old}.md", f"notes/{new}.md")
    body = body.replace(f"repro/{old}.json", f"repro/{new}.json")
    # params line
    import re
    body = re.sub(r"- Parameters: \[\[n, k, d\]\] = \[\[[^\]]*\]\]",
                  f"- Parameters: [[n, k, d]] = [[{new.replace('-', ',')}]]",
                  body)
    # distance confidence line
    body = re.sub(r"- Distance confidence: [^\n]*",
                  f"- Distance confidence: {conf}", body)
    # search line
    m = re.search(r"- Search behind the claim: [^\n]*", body)
    search = (f"- Search behind the claim: CI's independent RIS-fast "
              f"refutation search (8,000,000-trial class, seed {gate_seed}) "
              f"found the weight-{new.rsplit('-', 1)[1]} logical the local "
              f"ladder had missed; a fresh-seed gate_changed re-verification "
              f"(29,860 trials, seed {rerun_seed}) and the local ladder "
              f"(108,000 trials over six rungs) found nothing lighter, and "
              f"the witness CI found is carried in the entry")
    body = body.replace(m.group(0), search)
    # kd^2/n numbers
    body = re.sub(r"kd\^2/n = [\d.]+", f"kd^2/n = {kd}", body)
    r = recheck[new]
    kd_score = r["kd2n"]
    body = re.sub(r"Score kd\^2/n = [\d.]+", f"Score kd^2/n = {kd_score}", body)
    # claim-survival sentence: honest revision note
    body = re.sub(
        r"The distance is a witness-backed upper bound whose claim survived "
        r"the independent-seed re-confirmation recorded in the ladder and the "
        r"gate's fresh-seed refutation\.",
        "The distance is a witness-backed upper bound: the original local "
        "claim was refuted by CI's independent RIS-fast search, the entry was "
        "corrected to the CI reading with CI's witness carried, and a "
        "fresh-seed gate_changed re-verification found nothing lighter.",
        body)
    # frontier line
    c0 = r["cells"][0]
    if c0["dominates"]:
        dom = ", ".join(c0["dominates"])
        n_dom = len(dom.split("]], ")) if "]], " in dom else 1
        line = (f"- **unrestricted / any weight**: on the Pareto frontier — "
                f"dominates {dom}")
        if n_dom > 1:
            line += f" (and {n_dom - 1} further entries in the cell)"
    else:
        line = ("- **unrestricted / any weight**: on the Pareto frontier — "
                "frontier extension: dominates no existing entry, and no "
                "entry dominates it (recomputed against the committed board "
                "at the corrected reading)")
    body = re.sub(r"- \*\*unrestricted / any weight\*\*: [^\n]*", line, body)
    with open(OUT.format(new), "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print(f"wrote {OUT.format(new)}")
    print("  frontier line:", line[:160])
print("BODIES-DONE")
