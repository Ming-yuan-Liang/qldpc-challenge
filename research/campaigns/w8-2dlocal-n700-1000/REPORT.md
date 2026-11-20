# REPORT — Lane L6: w8-2dlocal-n700-1000 (weight-8 2D-local bilayer, n 700-1000)

**Status: CLOSED (positive) — 6 gate-passed board_advancing survivors staged.**

## Mission

Sweep the weight-8 x local-2d-bilayer cell at n in [700,1000] for
board_advancing codes (Pareto over n lower / k higher / d higher / w lower,
competed only against codes with locality class <= bilayer and weight class
<= weight-8).

Cell frontier at lane start (from codes/): the k=18 TILE4 line
(721/760/792..800/882/899..924/968 -18-24..31, incl. grafted n-reductions),
800-29-24 and 800-32-22 (B=5-box supports at 20x20, the cell's kd2/n leader
20.9), and the low-d w5/w6 lines (d<=10). The k 19-40 x d>=11 region above
the k=18 line was empty; the k=18 line had nothing beyond d=31.

## Method

- Generator: `research/local2d/boundary_engine.py::build_planar` (exact
  half-infinite boundary gauge over F2[t], corner completion, cleanup),
  `reduce_weights`, bilayer layout `planar.grid_coordinates(layers=2)`.
- Phase A: 6 seed support pairs (TILE4, TILE4P, W8, E08887, B5-29, B5-32) x
  ~94 lattice sizes (Lx*Ly in [350,500], both orientations, both dims>=14).
- Phase B: single-monomial mutation search around the B5 seeds, screened at
  21x22, box 6, MV>=19; 360 mutants screened, 24 screen advances.
- Instruments: `surrogate.distance_rand_witness`, backend="fast" (gf2_fast,
  threads=2/worker, <=4 workers). Ladder per candidate: screen 3x20k (pd22)
  -> 3x100k (pd20) -> deep 3x200k (pd16) -> 1M-class x4 (pd12) fresh seeds
  -> numpy per-side cross-checks (5k/side). Claim = lightest WITNESSED
  reading across all rungs (upper_bound, never "exact").
- Escalation bar: `reqd(n,k) = 1 + max{d_b : n_b<=n, k_b>=k, w_b<=8,
  locality<=bilayer}` computed live from codes/; candidates whose screen
  cleared it went to the deep ladder. Board-dup guard: rowspace comparison
  against every codes/ entry with the same (n,k) — caught the known twins
  (19x20->760-18-25, 20x20->800-18-27/29-24/32-22, 21x22->924-18-31,
  22x22->968-18-31) and kept them out of the deep budget.
- Checkpointing: one JSONL line per stage (progress.jsonl, deep.jsonl,
  graft.jsonl); 6 external kill waves absorbed, loss <= 1 chunk each.

## Staged survivors (research/candidates/l6-2dlocal/)

All six: gate `passed=true`, `board_advancing=true`, `dominated_by=[]`,
verdict at `<file>.verdict.json`; each carries per-side witnesses
(H.v=0, outside own rowspace, weight == claimed) re-checked by the gate's
own refute step, plus the bilayer layout (layers=2, radius 4*sqrt(2)).

| file | code | kd2/n | claim basis | cell context |
|---|---|---|---|---|
| 968-29-28.json | [[968,29,28]] | 23.5 | 1M x4 fast flat 28 (503/509/521/531), r3 29-30, np 34/38 | new cell kd2/n leader (old best 20.9 = 800-29-24) |
| 924-29-27.json | [[924,29,27]] | 22.9 | 1M x4 fast flat 27, r3 200k x3 flat 27, np 30/31 | beats 800-29-24 on d (+3) at n +124 |
| 966-29-27.json | [[966,29,27]] | 21.9 | 1M x4 fast flat 27, r3 flat 27 | same B5-29 family, largest lattice |
| 968-32-25.json | [[968,32,25]] | 20.7 | 1M x4 fast 25-26, np X 27 / Z 36 | k=32 point at d=25 (old: 800-32-22, d=22) |
| 880-18-29.json | [[880,18,29]] | 19.3 | 1M x4 fast 29-30 | k=18 d=29 below n=899 (old: 899-18-31 grafted line) |
| 840-18-28.json | [[840,18,28]] | 18.0 | 1M x4 fast 28-29 | k=18 d=28 at n=840 (old: 792-18-27) |

Constructions (per file provenance + <file>.recipe.json spec):
- 924/966/968-29-27/28: `build_planar(21,22 | 21,23 | 22,22, S_f=((0,0),(1,3),(2,1),(4,4)), S_g=((0,2),(1,4),(3,1),(4,0)))` — the B5-29 supports at
  three lattices; the family's d grows with L (24 at 20x20 -> 28 at 22x22).
- 968-32-25: `build_planar(22,22, S_f=((0,0),(1,3),(4,0),(4,4)), S_g=((0,4),(2,1),(3,2),(4,0)))` (B5-32).
- 840/880-18-28/29: `build_planar(21,20 | 22,20, S_F_TILE4, S_G_TILE4_MAIN)` —
  the recorded k=18 tile pair at TRANSPOSED assemblies (20x21, 22x20): the
  orientation swap changes the boundary truncation and lands d=28/29 where
  the board's own 21x22/19x20 assemblies give 31/25. These are genuinely
  different check matrices from the board twins (rowspace-verified), not
  re-measurements.

## Post-report addendum (2026-11-20)

- A seventh survivor was staged after this REPORT closed:
  **[[924,29,26]]** (B5-29@22x21, verdict `recorded_at 2026-11-10T00:55Z`,
  gate passed, board_advancing, dominated_by empty). It is a d-only peer of
  the staged [[924,29,27]] at equal (n, k, w) -- submitting both would be a
  self-domination sequence -- so the submission slate prunes it in favor of
  924-29-27. File kept with its verdict for the record.
- The six REPORT survivors were re-gated against the 2026-11-20 board
  (3,694 codes; validator updated upstream since staging): all advancing
  verdicts held, dominated_by empty everywhere. Gate_changed fresh-seed
  batteries 10/10 green (seeds 431001/431002, nothing lighter than the
  claims; log at `_12h-portfolio-shared/l6_battery_1120.log`). Submission
  slate: 840-18-28, 880-18-29, 924-29-27, 968-29-28, 968-32-25.

## Negative / bounded results

- TILE4@22x21 (the k=18 d-record hope at n=924): r4 seed 509 found a
  weight-29 Z-logical -> claim collapses to <=29 < reqd 32. Dead.
- TILE4@21x23 (n=966): r2 seed found 31 < 32. Dead.
- B5-29 at 840-880 (k=29): deep r3 read 24 < 25 — the screen bar (25) was
  optimistic; dead for advancement.
- B5-29@19x21 (798, k=18): deep r3 26 < 28. Dead.
- Grafting [[924,29,27]] at floor 27: only 3 accepted r=1 removals
  (924->921, block gate passed at 27, checkpoint graft_state_*.npz);
  kd2/n gain +0.08 — abandoned as not worth the confirmation budget.
- W8 pair (k=12) and TILE4P: screened, all non-advancing at 20k (d<=18-21
  vs reqd>=25). E08887 never reached (Phase A repeatedly killed by external
  kill waves; low priority anyway — needs d>=26 at k<=17).
- Phase A never completed TILE4 sizes 23x20/19x24+ and TILE4P/W8/E08887
  (kill waves; see Resume plan).

## Honesty notes

- Every claim is an upper bound at the lightest reading found anywhere in
  this lane's runs (fast and numpy); the board's own dup-calibration shows
  the fast instrument reads +1..+9 over true d at these sizes, so the true
  distances are likely 1-5 below the claims. The gate's refute passed all
  six; CI's deeper RIS battery may still tighten them (that is a correction
  path, not a retraction — the witnesses carry).
- `board_advancing` was judged by the gate against codes/ as of 2026-11-09;
  the six staged files dominate nothing on the current board (dominated_by
  empty everywhere) but do extend the bilayer cell's frontier on the d and
  k axes, and 968-29-28 raises the cell's kd2/n from 20.9 to 23.5.

## Artifacts

- research/candidates/l6-2dlocal/ — 6 survivors + .verdict.json + .recipe.json
- research/campaigns/w8-2dlocal-n700-1000/workspace/
  - sweep.py, deep.py, stage.py, graft.py (drivers)
  - progress.jsonl (746 rows: screens + r2), escalate.jsonl (166),
    deep.jsonl (182 chunks: r3/r4/np), graft.jsonl,
    graft_state_9362cad6d2_21x22.npz (grafted [[921,29,27]] state,
    unconfirmed), REPORT_draft.md
- Best non-staged leads for the next session: [[882,29,26]] (B5-29@21x21,
  r3 flat 26 >= reqd 25, r4 was in flight), [[882,32,24]] (B5-32@21x21,
  r3 24 >= 23), 281ac0da4f mutant [[906,28,25+]] (B5-32-mut, r1/r2 25-27).

## Resume plan

1. `deep.py --rung r4 --require-r3-pass --seeds 503,509,521,531 --shard 0
   --nshards 1 --max-cands 6` — finishes the 21x21 pair (+ the k=28 mutant)
   whose r3 already passed; stage anything that clears reqd.
2. `deep.py --rung r3 --shard 0 --nshards 1 --max-cands 30` — ~130
   escalations still lack deep rungs (mostly B5-29 Tier B small sizes).
3. `sweep.py --phase A --shard 0 --nshards 1` — finishes TILE4 tail sizes +
   E08887/TILE4P/W8 screens (done-set skips the 746 screened).
4. `sweep.py --phase B --box 6 --min-mv 19 --lx 21 --ly 22 --seed-base 14+`
   — mutation search is productive (24 screen advances in 360 mutants);
   the k=28/d>=25 mutant class deserves a dedicated deep pass.
5. Grafting: restartable via `graft.py --cand 9362cad6d2|21x22 --floor 27
   --seed 1` (deterministic replay to n=921, then continues); only worth
   resuming if >=10 removals look reachable.
6. Stage via `stage.py --cand <key>` (packaging is manual-then-verified:
   make_submission refuses the tile family on a stricter-than-gate tanner
   count; build_doc mirrors the schema and save_submission+gate enforce the
   real criteria).
