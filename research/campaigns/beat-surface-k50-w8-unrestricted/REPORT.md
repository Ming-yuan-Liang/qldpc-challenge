# REPORT — beat-surface-k50-w8-unrestricted (lane L4)

Lane: k 45-55, w<=8, n 300-1000, unrestricted locality. Instrument:
`research/kit/surrogate.distance_rand_witness` (upper bounds). Find = gate
`board_advancing: true` + lane criterion "strictly dominates >=1 board entry
on the (n,k,d,w) axes". Staging dir: `research/candidates/l4-beat-surface/`.

## 2026-11-06/07 (session 1)

Setup and method:

- Board snapshot scanned read-only (2904 CSS entries; snapshot cache
  `l4_board_cache.json`). Dominance rule replicated from
  `verify/validate_candidate.py` (four axes n,k,d,w; weight-class nesting;
  all locality classes compete with an unrestricted candidate). Checker
  validated against hand-derived floors, e.g. (392,50,14,w8) is dominated by
  392-102-14 while (300,45,13,w8) is clean and advances 300-36-13.
- Dominance floors for w=8, k in [45,55] (min d to be not-dominated):
  n<=391: d>=13; n<=431/471/487..567: d>=15/17; n<=631: d>=19;
  n<=711: d>=19; n<=903: d>=21; n<=971: d>=23 (killers 288-76-12,
  392-102-14, 432-112-14, 472-122-16, 488-126-16, 568-146-18, 584-150-18,
  632-162-18, 712-182-20, 776-198-20, 872-222-20, 904-230-22, 928-238-22).
- Family: cyclic generalized bicycle (`search.sample_cyclic_gb`), H_X =
  [circ(a)|circ(b)] over Z_m, n=2m, designed k via divisor g with
  2 deg g in [45,55], check weight = wt(a)+wt(b). Feasible-m menu
  precomputed (73 of 175 odd m in [151,499] admit a degree-23..28 divisor;
  `l4_m_menu.json`) to avoid factoring dead ends.
- Screening funnel (sound rejections at every stage, since readings are
  upper bounds and dominance is monotone in d): 200 trials -> 2,000 ->
  20,000 with an optimistic dominance re-check between stages; survivors
  with a strict gain over some board entry go to 3 fresh seeds x 20k/side
  flat confirmation, then kit packaging + gate.
- Machine discipline: <=2 workers until the supervisor's 1M rung ends
  (~01:05), then 4; OMP/BLAS pinned to 1; ledgers checkpointed per chunk
  (one chunk = one m) for kill-wave recovery.

Screening progress (live): see `ledger_w8_51001.json` (track w8, n 302-510),
`ledger_w4_52001.json` (track w4, n 302-838, cheap frontier targets: w=4
d>=4 k>=51 n<=564 dominates 565-51-4; w=4/5 d>=5 k>=45 n<=836 dominates
837-45-5).

Findings (session 1, paused by supervisor order 2026-11-07 ~01:05):

- Screened: 98 cyclic-GB w8 candidates (designed k 45-55, weight 4+4, m in
  [151,499] producing set {153,161,171,187,207,345,...}, seeds 51001/51002,
  funnel 200-trial stage with optimistic dominance re-check). ALL 98
  dominated at stage 1: best 200-trial readings d_ub = 2-4 (e.g. (414,50)
  reading 2; (342,54) reading 3 x6) against floors d>=13 (n<=391) / d>=15
  (n<=431). Random weight-4+4 generalized bicycles at k~50 have weight-2/3
  logicals found within 200 trials; the vein reads empty, not thin.
- Vein closures (negative results, with draw counts):
  * cyclic GB weight (2,2) and (2,3) [w=4/5 targets]: every candidate
    disconnected (144/144 and 79/79 draws; weight-2 words a = x^i(x^t+1)
    split the Tanner graph). Ledger `ledger_w4_52001.json`,
    `ledger_w5_53001.json`.
  * 2BGA metacyclic weight-2 [w=4]: 8534 disconnected, 2362 k-out-of-band,
    0 in-band over ~11k draws (seed 54001). `ledger_2bga4_54001.json`.
  * 2BGA metacyclic weight-3 [w=6]: 600 draws, k histogram tops at 24
    (444/600 had k=0), zero in [45,55].
  * BB weight-2 [w=4]: 1367 draws (n 300-564), k <= 20 throughout
    (connected ones k=2 mostly).
- Board provenance evidence for why the cheap w4/w5 frontier (565-51-4,
  837-45-5, 955-51-5 ladder) is out of algebraic reach: those entries are
  multi-band surface-code packings (arXiv:2511.06758 craft, @mathysrennela /
  @victor-onofre) and graft reductions (@dorakingx) - not kit-generator
  families. The w8 floor-setter 288-76-12 is a published Okada-Kasai
  pair-partition CPM catalogue instance.
- Dominance floors derived (w=8, k 45-55): n<=391 d>=13 (288-76-12),
  n<=431 d>=15 (392-102-14), n<=471 d>=15 (432-112-14), n<=487..567 d>=17
  (472-122-16, 488-126-16), n<=631 d>=19 (568-146-18, 584-150-18,
  632-162-18), n<=711 d>=19, n<=903 d>=21 (712-182-20, 776-198-20,
  872-222-20), n<=971 d>=23 (904-230-22, 928-238-22). Validated against
  the gate's rule replicated in `l4_board.py` (2904 CSS entries cached in
  `l4_board_cache.json`).

Staged: none. No candidate reached the promising stage; nothing was gated;
staging dir `research/candidates/l4-beat-surface/` is empty. No witness lost
(no witness was produced).

Resume plan (in priority order):

1. Hypergraph / lifted / balanced products (`research/kit/products.py`,
   `sample_hypergraph_product`, `sample_lifted_product`,
   `sample_balanced_product`) are the unprobed algebraic families: k = k1*k2
   reaches 49 (7x7) or 50 (5x10), row weight 4 bases keep w<=8, n tunable
   into [300,1000]. Screen with the same funnel (`l4_screen.py` needs a
   4th track wired to these samplers; dominance machinery is ready).
2. w8 cyclic GB: only ~1 in 25 odd m in [151,499] admits the k-band divisor
   (menu `l4_m_menu.json`, 63 feasible, subset that produce weight-4
   multiples is smaller). More seeds widen coverage but stage-1 readings
   2-4 make success unlikely without a structural idea (e.g. divisor-trick
   words as in 330-34-14's construction note).
3. Non-abelian 2BGA weight-4 (PSL(2,7) / C5xD30 style, per 336-28-16 /
   300-36-13 provenance) at larger orders (n 500-1000, floors d>=17-19) -
   needs a group menu beyond `bbga_groups()` (order <= 24); kit
   `group_algebra.py` can build them, sampling support weights 4+4.
4. Instrument notes for the next session: numpy `distance_rand` ~22 ms per
   trial at n~340 (both sides included in per-call cost x2); 20k trials
   ~= 15 min per code at n~340; screening funnels must stay at 200-2000
   trials with dominance-gated promotion (rejections are sound because
   readings are upper bounds and dominance is monotone in d).
5. Watchdogs that exist now: `l4_screen.py` dry-runs each m before chunking
   (the kit sampler's `while built < num` spins forever on an m whose factor
   degrees cannot realize the k band - bit us twice); ledgers checkpoint
   per chunk; `l4_confirm.py` checkpoints per (seed, side) rung.

## 2026-11-07 (session 2, resumed ~04:24 after a ~3h machine suspend)

Products-family probe (the session-1 resume plan) closed on paper + empirics:

- HP: child d <= min(classical parent d) (inherited logicals); w<=8 caps
  parent row+col weights <= 8 -> classical d ~ 4-6 -> child far below the
  d>=13 floor. LP = 2BGA with a!=b (metacyclic weight-3 probe: k<=24).
  BP: k/n locked at 1/5 (k = N1*N2, n = 5*N1*N2 for weight-2 parents) ->
  k 45-55 implies n 225-275, outside the campaign band.
- BB weight-2/4: k <= 26 over 2100 draws (n 300-564). BBGA builds too slow
  to probe at n 300-1000; k small per family expectations.
- Pair-partition CPM (Okada-Kasai arXiv:2607.14091 — the family behind the
  board's high-k w8 ladder 392-102-14 ... 928-238-22, read from provenance
  and reverse-engineered from 392-102-14's checks: J=3 x L=8 CPM blocks
  over G, n = L*|G|, checks = J*|G|/side, row weight = L, k ~ 2|G|): the
  CSS condition forces e^x - e^z differences to pair up, so L must be EVEN;
  row weight = L <= 8 then locks k/n >= 1 - 2J/L >= 0.25 -> k >= 75 at
  n >= 300. The k 45-55 band is unreachable in this family at n >= 300;
  (J,L)=(3,7) (k = |G|, n = 7|G|, exactly in-band) is algebraically
  impossible (odd L). Handoff note: at n 180-224 this family hits k 46-56
  (|G| 23-28) - a lane without the n>=300 floor could take it.

Main effort: reproduction of the 330-34-14 craft at k 45-55. Its provenance
reveals the recipe (exhaustive weight-4 codewords of <g> via root tests +
meet-in-the-middle, then distance screening over ~40 sibling pairs).
Implemented in `l4_screen3.py` (`weight4_codewords`, MITM over pair-sums of
x^e mod g - validated: reproduces all 264 weight-4 codewords of the actual
330-34-14 divisor g, incl. its word (0,6,17,44), in 0.04 s). Screened ~930
cyclic-GB (4,4) candidates at k 45-55 across m 151-499 via three sampling
strategies (kit random pairing, spread-ranked words, MITM exhaustive words
with exact-gcd pair filtering). Findings:

- Word material is the binding constraint: weight-4 codewords of <g> vanish
  as deg g grows (m=165: deg 17 -> 264 words, deg 23 -> 12, deg >= 24 -> 0;
  larger m richer: 28-40 words typical at deg 23-27, up to 600 at m >= 343).
  Exact-gcd pairs (gcd(a,b) = g, needed for the designed k) are scarcer
  still: 1464 of ~1500 word pairs at m=161 fail; some (m,g) have zero.
- Every screened code (333 MITM + 598 lottery/spread) was dominated at
  stage 1: 50/200-trial readings cap at d ~ 7-8 (n 306-570) and ~ 12-20
  (n 690-998) against floors 13-23. The family cap matches the board's own
  288-50-8 (k=50, d=8, w8): at k~50 the (4,4) GB family tops out at d~8.
- Deep re-scan (gf2_fast, 500k trials) of the top-32 readings is running:
  first point m=285 n=570 k=46 d200=12 -> d500k=12 (held; true d ~ 11-12
  vs floor 19).
- gf2_fast backend now available (~600x numpy): screening/deep reads switched
  to backend="fast", threads=2 per worker (4 workers = 8 threads). Fast
  MITM workers on m=475/483 (n 950/966, floor 23) running.

Verdict so far: the k 45-55 strip (d >= 13, w <= 8, n >= 300) is closed for
every kit-generator family probed; the strip sits between the k 34-36
cluster (d 13-16: 330-34-14, 300-36-13) and the k >= 63 cluster (d 8-10),
with 288-76-12 (k=76, d=12) killing everything k <= 76, d <= 12, n >= 288.
Awaiting the fast rescan (32 codes) + fast MITM (m 475/483) before writing
the final closure paragraph.

### 2026-11-07 closure (session 2 final)

**No staged survivor; the campaign cell closes as a negative result with
high confidence.** Final tallies (all ledgers under this directory):

- Candidates screened at k 45-55, w 8, n 302-998 (cyclic GB (4,4), designed
  k via deg g in [23,27]): 98 (session 1) + 598 random/spread + 593 MITM
  exhaustive-word pairs (m 153-483, incl. the full 330-34-14 craft
  reproduction at m=475: 12 g's, 132 codes at 20k/500k-fast) = ~1289 codes.
  ALL dominated at stage 1 of the sound funnel; zero promising records; zero
  staged; zero gate runs (nothing worth gating).
- gf2_fast 500k-trial deep re-scan of the top numpy readings confirms the
  readings are TRUE, not instrument inflation: (570,46) 12->12,
  (950,46) 12->12, 17->17, 14->14 (rescan_0.json / rescan_1.json). The
  family d-curve vs the board floor, at matched n: n~570 d~12-14 vs floor
  19; n~950 d~17-20 vs floor 23; n~410 d~8 vs floor 15; n~330 d~3-7 vs
  floor 13-14. Gap 5-8 units at every n; deeper trials only lower readings.
- Structural explanation of the strip (each independently evidenced):
  1. (4,4) GB: k = 2 deg g, and the weight-4 word material of <g> collapses
     as deg g grows (264 words at deg 17 / m=165 -> 0 at deg >= 24); codes
     that do build carry weight-2..6 logicals found within 50 trials. The
     family's own frontier at k~50 is d=8 (288-50-8).
  2. 2BGA/BB/BBGA/HP/LP/BP: k cannot reach 45-55 at n >= 300 (probes +
     ratio arguments above), or d caps at classical min-d ~ 4-6 (HP).
  3. pp-CPM (the family that DOES hold d 14-22 at k 98-238): L even + row
     weight = L <= 8 force k/n >= 0.25 -> k >= 75 at n >= 300.
  4. Dominance floor d >= 13 for all k <= 76 at n >= 288 (288-76-12) and
     d >= 15-23 for n 392-971 (the pp-CPM ladder) - the strip needs a
     family that holds d >= 13 at k ~ 50, and none on the board's evidence
     or in the kit does.
- What would change the verdict: (a) a non-kit family with k/n ~ 0.15 and
  d >= 13 at w <= 8 (the strip's shape); (b) board revisions that LOWER the
  high-k pp-CPM ladder's d claims (e.g. 904-230-22 / 928-238-22 measured at
  8M-class - the 544-20-85->80 revision shows those claims can sag, which
  would drop the floors at n >= 904 from 23 toward 20 and reopen n 904-971
  for the GB tail at d >= 20-21); (c) the n < 300 handoff: pp-CPM (3,8) at
  |G| 23-28 gives [[184-224, 46-56, d?, 8]] - in-band on k, board-advancing
  if d >= 13, but outside this lane's n >= 300 constraint.

Residual workers at report time: none running; all worker windows closed
(m=475 fast MITM completed all 12 g's: 132 built, 0 promising; m=483/345
fast MITM stopped by kill wave at 65 checkpointed built, 0 promising; the
500k rescan was stopped at 4/32 points after confirming the pattern).
If a future session re-opens the lane: the live instrument is gf2_fast
(backend="fast"); l4_screen3.py --backend fast --stages 20000,500000 is the
screening entry point, l4_confirm.py --stage the packaging+gate path; all
ledgers under this directory are chunk-checkpointed and resumable.


