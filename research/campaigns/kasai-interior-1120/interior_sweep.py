"""Lane A1 (kasai-interior-1120): sweep the affine-2BGA interior gaps.

Hunts k in [14, 26] x d >= 40 interior points at q in {17, 19} (n 544/684),
the band between our merged anchors 684-14-107 and 544-20-76 where the
board has no competitor. Interior points must be non-dominated against the
anchors: at n=684 a k=16 draw needs d >= ~90 to beat 684-14-107's eff
234 (16*90^2/684 = 189 — no: eff must EXCEED 234 to advance the cell's
best; but a point can still be board_advancing as a frontier extension on
the k axis while below the anchor's eff — the gate decides).

Usage:
  python interior_sweep.py --q 19 --weight 8 --num 2000 --seed 41001
      [--workers 4] [--min-k 14] [--max-k 26] [--min-d 40]

Check weight = 2*weight (|a| = |b| = weight). Screens with the fast
backend; survivors (screen d >= min-d, k in band, no board collision) are
written as JSONL with witnesses for the deep ladder.
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "kit"))
sys.path.insert(0, str(ROOT / "research"))

from search import sample_kasai_affine, screen  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=int, required=True, choices=[17, 19])
    ap.add_argument("--weight", type=int, required=True,
                    help="|a| = |b|; check weight is 2x this")
    ap.add_argument("--num", type=int, default=2000)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--min-k", type=int, default=14)
    ap.add_argument("--max-k", type=int, default=26)
    ap.add_argument("--min-d", type=int, default=40)
    ap.add_argument("--trials", type=int, default=1000)
    args = ap.parse_args()

    out = Path(__file__).parent / f"screened_q{args.q}_w{args.weight}_s{args.seed}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done.add(r["spec"]["draw_id"])
            except Exception:
                pass

    def tagged():
        for i, (spec, HX, HZ) in enumerate(sample_kasai_affine(
                args.num, q_range=(args.q, args.q), weight=args.weight,
                seed=args.seed)):
            spec["draw_id"] = f"{args.seed}-{i}"
            if spec["draw_id"] not in done:
                yield (spec, HX, HZ)

    n_yield = 0
    t0 = time.time()
    with out.open("a", encoding="utf-8") as fh:
        for r in screen(tagged(), min_k=args.min_k, min_d=args.min_d,
                        trials=args.trials, seed=args.seed + 1,
                        backend="fast", workers=args.workers,
                        threads=2, board="flag"):
            n_yield += 1
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            n = r.get("n"); k = r.get("k"); d = r.get("d")
            if k and d and k * d * d / max(n, 1) > 100:
                print(f"ADVANCE? n={n} k={k} d={d} eff={k * d * d / n:.1f} "
                      f"draw={r['spec']['draw_id']}", flush=True)
    print(f"done: {n_yield} survivors of {args.num} draws in "
          f"{(time.time() - t0) / 60:.1f} min -> {out}")


if __name__ == "__main__":
    main()
