# REPORT — beat-surface-k100-w8-unrestricted (lane L5)

Lane: k 95-105, w<=8, n 500-1000, unrestricted locality. Instrument:
`research/kit/surrogate.distance_rand_witness(..., backend="fast", threads=2)`
(gf2_fast C++ backend; calibrated ~2.0-2.2k trials/s/worker at n 510-714;
pair_depth recorded per rung in every confirm ledger). Find = gate
`board_advancing: true` + lane floors on the ff'd board. Staging dir:
`research/candidates/l5-beat-surface/` (QLDPC_RUN_ID=l5-beat-surface).

## 2026-11-07 (session 1)

Setup and board state (ff 7ea802a1f, cache `l5_board_cache.json`, 2905 CSS
entries; scanner `l5_scan.py`):

- Dominance floors for w=8, k 95-105 (need d strictly above the max entry d
  with n_e <= n, k_e >= 105, w_e <= 8): n<=567 d>=17 (472-122-16);
  568-711 d>=19 (568-146-18, 576-148-18, 584-150-18, 664-170-18);
  712-903 d>=21 (712-182-20); 904-927 d>=23 (904-230-22, 912-234-22);
  928-971 d>=23 (928-238-22); 972-993 d>=35 (972-166-34); 994-1000 d>=41
  (994-142-40). The campaign spec's bar slug 392-102-14 (kd2/n = 51.0) is
  stale: the ff'd board's own cell frontier is 994-142-40 (kd2/n 228.6);
  floors are computed against the full ff'd board throughout.
- Board-provenance discovery that set the lane's direction: codes/994-142-40,
  996-166-32/34, 972-166-34, 1000-200-29 are OUR repo's irregular
  pair-partition CPM templates (Okada-Kasai arXiv:2607.14091 commutation rule
  applied to irregular BxL column-pair templates at design rate 1/5-1/7, w=8,
  k = 2(P-B)*N): 4x10 rate 1/5 (1000-200-29, P=100), 5x12 rate 1/6
  (996-166-*, P=81-83), 6x14 rate 1/7 (994-142-40, P=71). For k = 2N with
  k in [96, 104] the lifts are N in [48, 52], giving n = 2PL in [500, 936]:
  the lane cell (k 95-105 at n 500-1000) is exactly the under-sized end of
  the published templates' lift range. Linear scaling of the published
  distances (0.29-0.56 per unit lift) predicts d 20-29 at N = 48-52 vs floors
  17-23: the cell is the natural extension target.
- Builder: `l5_pp.py` rebuilds all three templates + their published pairings
  verbatim from the provenance (validated: rebuilding 994-142-40's S arrays
  at N=71 reproduces CSS=True, k=142, 0 4-cycles). Exponent draws are exact
  integer solutions of the paired-difference system (RREF over Q, free
  variables on the denominator-lcm lattice) reduced mod N, so composite N is
  admissible; draws filtered to k in [95,105], CSS, 4-cycle-free. Two solver
  bugs found and fixed during validation (free-variable storage, sign of the
  dependent solution); every draw now re-checks all pairing equations mod N
  before use.
- Screening funnel (`l5_screen.py`, sound rejections: readings are upper
  bounds and dominance is monotone in d): 1000 -> 10000 -> 100000 trials with
  optimistic margins floor+7/+4/+2 vs the per-n floor; per-draw checkpointed
  ledgers. Deep instrument: `l5_deep.py` (500k triage -> multi-seed 500k
  ladder -> 2M rung -> Z-side swapped-matrix rung -> 500k @ pair_depth 48;
  every reading persisted with its support immediately - no witness lost).

Batch results (240 screened draws + 3 template configs):

- pp410 (4x10, rate 1/5) N=51 (n=510, k=102, floor 17): 60 draws, 59
  rejected at stage 0 (readings 13-23, matching the linear-scaling
  pessimism d ~ 0.29N ~ 15). One survivor (draw 45: 25->21->19 at 100k,
  still descending) - recorded, not staged (margin 2 over floor with a
  falling ladder; the 4x10 template at this size reads dominated-curve).
- pp512 (5x12, rate 1/6) N=49 (n=588, k=98, floor 19): 60 draws, 27
  promising; 100k readings cluster at exactly 22 (template-structural
  logical weight); 500k triage of the top 4 held 22.
- pp614 (6x14, rate 1/7) N=49 (n=686, k=98, floor 19): 60 draws, 45
  promising; 500k triage of the top 6 held 22/23/24 (all non-dominated).
- pp614 N=51 (n=714, k=102, floor 21): 60 draws, 51 promising; 500k triage
  of the top 6 held 23-26 (all non-dominated).

STAGED FINDS (gate passed=True, board_advancing=True, verdicts beside the
candidates under research/candidates/l5-beat-surface/):

1. [[588,98,22]] w=8 - 5x12 template, N=49, draw 13 of seed 99201.
   Readings: 3 fresh seeds x 500k = 22/22/22, 2M = 22, Z-side (swapped
   matrices) 2M = 22, 500k @ pair_depth 48 = 22 - flat at 22 everywhere.
   Gate: passed, board_advancing=True ("advances the weight-8 x unrestricted
   board"), refute=False. kd2/n = 98*484/588 = 80.7 (campaign bar 51.0).
   Dominance: dominated_by=[] ; dominates 2 board entries.
   Files: 588-98-22.json (+ .verdict.json, .recipe.json), confirm ledger
   confirm_pp512_N49_d13_8c869129.json.

(2-4: pp614 entries - see the staged list below; filled as their ladders
completed.)

Family closures / negative results (with draw counts):

- Non-abelian 2BGA weight-8 (4+4 supports), the L4 resume-plan item: k-scan
  over 4 groups x 2000 draws (`l5_2bga.py`, committed Cayley tables built via
  perm_group: PSL(2,7) 168 [order-verification histogram 1/21/56/42/48],
  PSL(2,7)xC2 336, A6 360, A5xC7 420, GL(2,5) 480). k reached the band
  [95,105] in 3 of ~8400 draws (GL(2,5) only: k=96 twice, k=100 once);
  A6 max 71, PSL(2,7)xC2 max 88, A5xC7 max 44. ALL three in-band instances
  read d <= 4 at 20k fast trials (need d >= 23 at n 960): the family's rate
  can occasionally reach 0.20-0.21 but the high-k instances carry weight-3/4
  logicals - closed for this cell, consistent with L4's GB/2BGA trend.
- 4x10 rate-1/5 template at n 500-520: closed by the batch above (59/60
  stage-0 rejections; predicted d ~ 0.29N < floor 17).
- pp-CPM complete (J,L) ladder at w<=8 cannot reach the cell (structural,
  extends L4's argument): rate = 1 - 2J/L >= 1/4 for J >= 3 (J = 2 caps d at
  the column-graph girth <= 12; J >= 4 gives rate 0), so k ~ 100 forces
  n ~ 400 < 500; any rate above 1/4 needs shift-class degeneracy t which
  buys k += t but caps d <= 2N/t - both horns exclude k 95-105 at n >= 500.
  The irregular low-rate templates are the only w<=8 pp-CPM route into the
  cell, and they are what this lane mined.
- HGP w<=8: proven out by Singleton: k = 2*k1*k2 >= 95 with d >= 17 needs
  (k1+16)(k2+16) <= n1*n2 <= 500, but the minimum over k1*k2 >= 47.5 is
  (6.9+16)^2 > 525 > 500. (Child d <= min(parent d) inherited.)
- Ladder 8M re-measure (904/928, the L4 handoff #2): SKIPPED as redundant -
  the board entries already carry deep evidence (904-230-22: 50M GPU
  deep-kernel + 8M gf2_fast reads at 22; 928-238-22: 2M x 4-chunk gf2_fast
  + Stern ladder + branch-and-bound proving no logical of weight <= 21),
  so the "claims may sag at 8M" risk is already retired by existing records.

Notes on method and discipline:

- Machine: 4 workers x threads=2 after the supervisor's battery cleared
  (max 8 threads); OMP/BLAS pinned to 1; all ledgers checkpointed per draw /
  per rung (kill-wave safe; the one crash that occurred - a packaging
  NameError - lost nothing: rungs are persisted before packaging).
- The uniform 100k readings (22 on pp512 draws, 22-24 on pp614) are
  template-structural logical weights, not instrument saturation: the deep
  ladders confirm them flat across seeds/budgets/sides, and the gate's
  independent refute search agrees.
- Odd lifts N are preferred (49, 51): even N's small quotient lifts (Z_{N/2},
  factor 2) would bind claims ~2w; N=49's only quotient is Z_7 (factor 7,
  cap 7w >= 154, non-binding); N=51's Z_17 (x3) caps at 3w, non-binding for
  claims <= 26. Quotient caps recorded per candidate in the confirm ledgers.

## 2026-11-07 (session 1, closing)

**Six staged survivors, all gate passed=True + board_advancing=True, all
flat across multi-seed deep ladders.** The campaign's frontier_advance
stopping condition is met; the kd2/n bar of the campaign spec (51.0 vs
392-102-14) is beaten by every survivor. Final slate (staging dir
`research/candidates/l5-beat-surface/`, verdicts beside each candidate):

| candidate | template / lift | kd2/n | floor | margin | deep evidence |
|---|---|---|---|---|---|
| 510-102-19 | 4x10 rate 1/5, Z_51 | 72.2 | 17 | +2 | 2x500k + 2M + Z-2M + 500k@pd48, all 19 |
| 588-98-22 | 5x12 rate 1/6, Z_49 | 80.7 | 19 | +3 | 3x500k + 2M + Z-2M + 500k@pd48, all 22 |
| 686-98-22 | 6x14 rate 1/7, Z_49 | 69.2 | 19 | +3 | 2x500k + 2M + Z-2M + 500k@pd48, all 22 |
| 686-98-23 | 6x14 rate 1/7, Z_49 | 75.6 | 19 | +4 | 2x500k + 2M + Z-2M + 500k@pd48, all 23 |
| 686-98-24 | 6x14 rate 1/7, Z_49 | 82.3 | 19 | +5 | 2x500k + 2M + Z-2M + 500k@pd48, all 24 |
| 714-102-25 | 6x14 rate 1/7, Z_51 | 89.4 | 21 | +4 | 3x500k + 3x2M (X and Z) + 500k@pd48, min 25 |

All six: claimed d is the lightest reading (confidence upper_bound, witnesses
embedded X and Z, quotient caps recorded in the confirm ledgers and
non-binding). Board relation: dominated_by=[] everywhere; the candidates
advance 1-7 board entries each (e.g. 714-102-25 dominates seven). Note for
the commit merge: 686-98-24 subsumes 686-98-22/23 on the Pareto axes (same
n,k, larger d, different exponent draws - distinct codes with independent
witnesses); the supervisor may keep just the d=24 instance at that corner.
The six (n,k) corners (510/588/686/714 x k 98-102) are pairwise incomparable
and all extend the unrestricted weight-8 frontier inside the lane cell.

Campaign direction vs outcome: the spec's example bars (d>=17 at k=95 n=500;
d>=23 at k=105 n=1000) are realized as d=19 at k=102 n=510 through d=25 at
k=102 n=714 - the achievable corners of the same cell, each far above the
kd2/n bar. The k 95-105 strip at n 500-1000 is NOT saturated: it is the
under-lifted end of the repo's own irregular pair-partition template family,
and the lift knob (N 48-52) fills it densely (100-reading clusters at
template-structural logical weights 19-26 per (template, N)).

Structural closure for the rest of the cell (everything probed besides the
irregular pp-CPM templates):
1. Complete (J,L) pp-CPM at w<=8: rate >= 1/4 for J >= 3 (J = 2 caps d at
   girth <= 12; J >= 4 rate 0) -> k ~ 100 lands at n ~ 400 < 500; the
   degeneracy escape (k = 2N + t, d <= 2N/t) is doubly excluded at n >= 500.
2. 4x10 at N 48-49 (n < 500): out of band; at N 50-52 the batch shows the
   dominated curve except the one 510-102-19 keeper above.
3. Non-abelian 2BGA w8: closed empirically (4 groups x 2000 draws, 3
   in-band instances all with weight-4 logicals; A6/PSL27xC2/A5xC7 never
   reach k 89 at n <= 960).
4. HGP w<=8: Singleton-proven out ((k1+d1-1)(k2+d2-1) > 500 for 2k1k2 >= 95,
   d >= 17).
5. GB/BB/abelian-2BGA at k ~ 100: inherited from L4 (weight-4 word material
   collapses for deg g >= 24; k = 2 deg g >= 96 is far past the collapse).
6. Ladder 8M re-measure skipped: 904/928 already carry 2M-50M-trial evidence
   plus a branch-and-bound lower bound; L4's handoff concern is retired.

Ledgers and evidence (all under this directory, checkpointed per draw/rung):
l5_board_cache.json + l5_scan.py (floors), l5_pp.py (builder, validated
against 994-142-40), l5_screen.py + ledger_pp_pp410_51_99301.json (60),
ledger_pp_pp512_49_99201.json (60), ledger_pp_pp614_49_99001.json (60),
ledger_pp_pp614_51_99101.json (60), l5_deep.py + confirm_*.json (per-
candidate rungs with supports), l5_2bga.py + ledger_2bga_*.json (8000-draw
k-scans). Unpromising-but-recorded: pp614 N=51 draws 4/30/38/6/42 (500k-held
25/25/24/23/23, non-dominated, not deep-laddered - batch-spawnable by the
supervisor if more corners are wanted), pp614 N=49 draws 3/9/46 (24/24/23
held at 500k, same status), pp410 N=51 draws 1-59 (dominated).

Residual workers at report time: none (all ladders/stagings completed; all
windows closed cleanly).
