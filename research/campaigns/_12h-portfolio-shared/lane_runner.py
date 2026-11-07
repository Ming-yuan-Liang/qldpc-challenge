"""Shared lane runner for the 12h unattended portfolio (2026-10-27).

One parameterized QUICKSTART loop used by the portfolio's campaign run.py
shims: load the campaign, generate candidates, screen at the declared depth,
deepen what the card's criterion selects, package and gate survivors, and
write the ledger, summary, and report path. Everything is recorded per
candidate; survivors are staged under research/candidates/ for human review.
Nothing here is a submission.

The deepening/gating criterion is a parameter: ``select`` receives the
candidate list with screen readings and returns the indexes to refine
(top-by-efficiency above a flat bar for the weight-capped cells; top-K for
the any-weight cell, where kd^2/n is set by weight-30+ codes and Pareto
dominance, decided by the gate, is the currency -- see TRACKS.md).
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (os.path.join(_ROOT, "research", "kit"), os.path.join(_ROOT, "verify")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from campaign import Ledger, load_campaign, write_summary  # noqa: E402
from coordination import gate_and_record, staging_dir, unique_path  # noqa: E402
from prescreen import board_index  # noqa: E402
from search import PREPASS_COUNTS, screen  # noqa: E402
from submit import make_submission, save_submission  # noqa: E402
from surrogate import distance_rand  # noqa: E402

AUTHOR = "@LiangMingyuan"  # confirm before any human promotion


def select_above_bar(cands_recs, bar):
    """Default criterion: indexes whose screen efficiency reads above bar."""
    return [i for i, r in enumerate(cands_recs)
            if r is not None and r["efficiency"] > bar]


def select_top_k(cands_recs, k_refine=6, k_gate=3):
    """Any-weight criterion: refine the top-k_refine by screen efficiency,
    gate the best k_gate of those by deep reading. Returns two index lists."""
    have = [(i, r) for i, r in enumerate(cands_recs) if r is not None]
    have.sort(key=lambda t: -t[1]["efficiency"])
    return [i for i, _ in have[:k_refine]], [i for i, _ in have[:k_gate]]


def run(here, cfg):
    camp = load_campaign(os.path.join(here, "campaign.json"))
    led = Ledger(camp)
    print(f"campaign {camp.id}: {camp.name}", flush=True)

    trials = camp.c["methods"]["screening"]["trials_per_candidate"]
    deep = camp.c["direction"]["abandon_criterion"]["trials_cap"]
    index = board_index()
    print("board index ready", flush=True)

    audit = {}
    cands = list(cfg["generator"](audit=audit, **cfg.get("generator_kwargs", {})))
    print(f"generator -> {len(cands)} built: {audit}", flush=True)

    # Stage 1: screen everything at the declared depth, in one batch so the
    # board prepass and dedup run once. The readings are cached beside the
    # campaign so a crash after the batch does not re-pay the screen.
    cache_path = os.path.join(here, "screen_cache.json")
    spec_keys = [json.dumps(s, sort_keys=True) for s, _, _ in cands]
    rec_list = None
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        if cache.get("spec_keys") == spec_keys:
            rec_list = cache["recs"]
            cfg.setdefault("screen_audit", cache.get("screen_audit", {}))
            print(f"screen cache hit: {len(rec_list)} readings", flush=True)
    if rec_list is None:
        recs = screen(cands, min_k=1, min_d=4, trials=trials, seed=0,
                      index=index, audit=cfg.setdefault("screen_audit", {}))
        spec_to_rec = {json.dumps(r["spec"], sort_keys=True): r for r in recs}
        rec_list = [spec_to_rec.get(kk) for kk in spec_keys]
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"spec_keys": spec_keys, "recs": rec_list,
                       "screen_audit": cfg["screen_audit"]}, f)
        print("screen cache written", flush=True)
    n_screened = sum(1 for r in rec_list if r is not None)
    n_dropped = len(cands) - n_screened
    print(f"screened {n_screened}/{len(cands)}; prepass dropped {n_dropped}; "
          f"counts {dict(cfg.get('screen_audit', {}))}", flush=True)

    survivors = []
    sel = cfg["select"](rec_list)
    if isinstance(sel, tuple):
        refine_idx, gate_idx = sel
    else:
        refine_idx = gate_idx = sel
    print(f"selected for refinement: {refine_idx}", flush=True)

    for i, (spec, HX, HZ) in enumerate(cands):
        params = cfg["spec_params"](spec)
        led.start_experiment(cfg["family"], seed=i, mode="novel_generation",
                             params=params)
        led.spend(candidates_screened=1)
        rec = rec_list[i]
        if rec is None:
            led.record_screen(trials=trials, backend="numpy")
            led.record_negative("dropped in prepass",
                                "direct sum, a fingerprint the board already "
                                "holds, or below min_k/min_d")
            led.record_verdict("not_run")
            led.end_experiment()
            continue

        n, k, d = rec["n"], rec["k"], rec["d"]
        eff = rec["efficiency"]
        led.record_screen(trials=trials, d=d, backend="numpy", n=n, k=k)

        if i not in refine_idx:
            led.record_verdict("not_run")
            led.end_experiment()
            continue

        # Refinement: two fresh-seed rungs (the schema's ladder minimum);
        # keep the tightest upper bound.
        r1 = distance_rand(HX, HZ, trials=deep, seed=10_000 + i,
                           backend="numpy")
        r2 = distance_rand(HX, HZ, trials=deep, seed=20_000 + i,
                           backend="numpy")
        d_deep = min(d, r1, r2)
        led.record_screen(trials=deep, d=d_deep, backend="numpy", rung=2,
                          n=n, k=k)
        bar = cfg.get("bar")
        if bar is not None and k * d_deep * d_deep / n <= bar:
            led.record_negative("deep rungs dropped the ladder",
                                f"deep bound d<={d_deep} reads kd^2/n "
                                f"{k*d_deep*d_deep/n:.2f} at or below the "
                                f"bar {bar}")
            led.record_verdict("not_run")
            led.end_experiment()
            continue
        if i not in gate_idx:
            led.record_negative("refined, not gated",
                                f"deep bound d<={d_deep} (eff "
                                f"{k*d_deep*d_deep/n:.2f}) outside the "
                                "gate slice")
            led.record_verdict("not_run")
            led.end_experiment()
            continue

        doc = make_submission(
            HX, HZ, name=cfg["name"](spec, n, k, d_deep),
            construction=cfg["construction"](spec, n, k, d_deep),
            authors=[AUTHOR], family=cfg["family"],
            confidence="upper_bound", trials=deep)
        try:
            path = unique_path(
                os.path.join(staging_dir(), f"{n}-{k}-{d_deep}.json"), doc)
            save_submission(doc, path,
                            spec={"constructor": cfg["constructor"],
                                  "params": params})
            verdict, _ = gate_and_record(path)
        except Exception as e:  # noqa: BLE001 - keep the run alive, record it
            led.record_negative("staging or preflight refused",
                                f"{type(e).__name__}: {e}")
            led.record_verdict("not_run")
            led.end_experiment()
            continue

        if verdict.get("passed"):
            led.record_verdict("passed")
            row = led.record_candidate(doc, verdict)
            survivors.append((row, path))
            print(f"  PASSED [[{row['n']},{row['k']},{row['d']}]] -> {path}",
                  flush=True)
        else:
            labels = "; ".join(verdict.get("labels") or [])
            txt = labels.lower()
            v = ("duplicate" if "duplicate" in txt
                 else "dominated" if "dominat" in txt
                 else "refuted" if "refut" in txt else "not_run")
            led.record_negative("gate rejected", labels)
            led.record_verdict(v)
            print(f"  gate: {v} ({labels})", flush=True)
        led.end_experiment()

    fired = led.stop_reason()
    print(f"  stopped by: {fired}" if fired
          else "  no stopping condition fired; candidate list exhausted",
          flush=True)
    summary = led.summary(report=os.path.join(here, "REPORT.md"))
    out = os.path.join(here, "summary.json")
    write_summary(summary, out)
    print(f"  summary -> {os.path.relpath(out, _ROOT)}", flush=True)
    print(json.dumps({"survivors": [str(p) for _, p in survivors]},
                     indent=2), flush=True)
    return summary
