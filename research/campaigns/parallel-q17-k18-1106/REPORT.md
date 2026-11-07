# REPORT — lane q17-k18 (Kasai affine 2BGA over Aff(F_17), n = 544)

Campaign dir: `research/campaigns/parallel-q17-k18-1106/` (this directory).
Date: 2026-11-06. Staging run id: `q17-k18-1106`
(`research/candidates/q17-k18-1106/`). Stage-only; nothing here is a
submission. Author on staged docs: `@Ming-yuan-Liang`.

## Lane assignment

Kasai affine 2BGA over Aff(F_17) (metacyclic realization Z_17 x| Z_16, order
272, primitive root 3; n = 2 x 272 = 544). ~250 random seed-exponent draws
with |a| = |b| in {8, 9, 10}, exponents uniform in [0, 272); target the
k = 16-22 corner. Screen with the gate's preflight then a 400-trial RIS
reading behind within-batch css_fingerprint dedup; re-read the top draws at
3 fresh seeds x 20,000 trials/side; stage only draws whose deep readings
agree flat, with witnesses embedded, and record the gate verdict.

## What was run

Scripts (all in this directory): `pool_search.py` (uniform draws + fast
bit-packed GF(2) rank k-filter, validated against kit `compute_k`), 
`screen_corner.py` (kit `search.screen`: CSS, k-filter, within-batch
fingerprint dedup, connectivity, board exact/WL dedup, then 400-trial numpy
RIS), `deep_read2.py` (resumable deep readings), `analyze_and_stage.py`
(flat-rule analysis + kit-path staging), `board_landscape.py` (domination
thresholds from the committed board).

- Draw pool: 260,000 uniform draws
  (`pool_draws.jsonl`). k histogram: k=0: 42,557, k=2: 92,085, k=4: 71,978,
  k=6: 35,141, k=8: 11,226, k=10: 4,844, k=12: 1,349, k=14: 564, k=16: 174,
  k=18: 49, k=20: 25, k=22: 5, k=24: 3.
- Corner yield: the k in [16,22] corner is ~1/1,050 draws (0/500 in the first
  probe; 253/260,000 in the pool). k is always even for this family
  (rank(HX) = rank(HZ) because HZ = [Rb^T | La^T]), so the corner is
  k in {16, 18, 20, 22}; no k = 17/19/21 exists.
- Screened: 200 of the 253 corner draws
  (`screened_draws.jsonl`; k=16: 131+4 dropped, k=18: 40, k=20: 21,
  k=22: 4). The remaining 53 unscreened draws are ~all k=16 (lowest value:
  they need d > 82 to advance, see below); screening was truncated there
  under the shared-machine budget. Audit across chunks: 4
  `rejected_disconnected`, 0 repeats, 0 board-exact/WL collisions.
- Domination thresholds (from `board_landscape.py` over the committed board;
  a [[544, K, W]] CSS candidate is dominated iff some CSS entry has
  n <= 544, k >= K, d >= claimed, w <= W, one strict): for K in {16, 18} the
  dominator is [[544,18,82]] w=12 -> need d > 82; for K in {20, 22} it is
  [[514,32,70]] w=16 -> need d > 70. (Note: the board's 82 claim was refuted
  to 76 by CI on 2026-11-05; the gate compares against the committed board.)

## Deep readings (the honest part)

Instrument: `research/kit/surrogate.lightest_logical` (numpy RIS,
pair_depth 10), 20,000 trials per side per rung, 3 fresh seeds. Each
20,000-trial rung-side was executed as 4 sub-searches of 5,000 trials with
decorrelated seeds (rung_seed*1000 + j), lightest kept — same total budget
per rung per side; sub-chunking exists because the shared machine kills long
background jobs. Every sub-witness is persisted in `deep_subjobs.jsonl`.

| pool_i | k | w | d400 | rung readings (min over sides) | verdict |
| --- | --- | --- | --- | --- | --- |
| 24989 | 22 | 8 | 98 | 911001: 24 (weight-24 Z-logical, witness persisted); 911002/911003 partial 86-94 | DEAD: d <= 24, dominated miss |
| 53244 | 20 | 10 | 97 | (in flight) | pending |
| 74545 | 20 | 10 | 96 | (in flight) | pending |
| 96205 | 20 | 8 | 95 | (in flight) | pending |
| 42514 | 20 | 10 | 94 | (in flight) | pending |
| 84342 | 20 | 10 | 94 | (in flight) | pending |

The weight-24 Z-logical on the k=22 draw (screen reading 98 four hundred
trials earlier) is the lane's clearest demonstration of the screen-inflation
bias the briefing warns about.

## Staged survivors / gate verdicts

(filled at the end of the run)

## Dominated misses

(filled at the end of the run)

## Resume 2026-11-06 (session L2 q17-k18-resume, ~11:00-12:00 UTC+8 window)

Resumed from `deep_subjobs.jsonl` (61 sub-search records) + the empty
`deep_rungs.jsonl` (the previous session's rungs never aggregated; the raw
sub-searches are the source of truth and every witness is persisted there).
No deliverable from the previous `analyze_and_stage.py` run exists: nothing
was staged under `research/candidates/q17-k18-1106/` or anywhere else in
`research/candidates/`, and the REPORT's "Staged survivors" section was
unfilled. Recovered state from the checkpoint, re-confirmed against the
current board (`cli/qldpc.py brief --cell unrestricted/weight-any`;
[[544,18,76]], [[684,12,108]], [[684,8,110]] landed 2026-11-06):

- Domination thresholds recomputed (`board_landscape.py`, committed board):
  k in {16, 18} now need d > 76 (dominator [[544,18,76]] w=12; the old
  table's 82 is stale after the merge), k in {19..22} need d > 70
  (dominator [[514,32,70]] w=16).
- i=24989 (k=22, w=8, d400=98): DEAD, dominated miss. Rung 911001 complete
  with the weight-24 Z-logical (screen read 98 four hundred trials earlier;
  the clearest local demonstration of screen inflation). Rung 911002 partial
  (5/8 subs) — not extended, the draw cannot advance.
- i=53244 (k=20, w=10, d400=97): 5 complete fresh-seed rungs at 20,000
  trials/side: 911001: 89, 911002: 93, 911003: 88, 911004: 90, 911005: 89.
  Lightest reading 88 (one rung). Far above the k=20 bar (d > 70) but not
  yet stageable under the lane rule (see below).
- i=74545 (k=20, w=10, d400=96): 4 complete rungs: 911001: 91, 911002: 89,
  911003: 91, 911004: 90. Lightest 89 (one rung). Rung 911005 X-side has
  2/4 subs done (89, 94) when the supervisor wind-down landed.

### Rule used for stage-worthiness (recorded explicitly)

The lane task says a candidate needs ">=3 fresh-seed rungs at >=20,000
trials/side agree flat at the claimed reading", claims at the lightest
reading. `analyze_and_stage.py` implements the strict all-rungs-equal rule,
which is unsatisfiable for any draw whose already-recorded rungs disagree
(both leaders). The resume uses `analyze_resume.py`: stageable iff >= 3
complete rungs read exactly R = the lightest reading over all completed
rungs (no rung can read below R by definition; per-side witnesses are the
per-side minima over all complete rungs, each >= R). This is the only
reading that satisfies both the "3-agree" and "lightest-reading" clauses at
once, and it is stricter than the precedent the merged [[544,18,76]] set
(4 non-flat rungs 88/88/86/82, packaged at the lightest 82, later corrected
to 76 by CI). Under it neither leader is stageable yet.

### What this session ran (before the supervisor wind-down)

- Calibrated the instrument: 300-trial probe on 53244 reads 98 at ~33
  trials/s single-thread uncontended (the contended 14-worker session ran
  ~5,000-trial subs at 201-2,889 s, median 976 s).
- Queued and partially ran rungs 911004/911005 for the two leaders (2
  workers, `deep_read2.py`, per-sub checkpoint flushes): 26 new sub-search
  records, `deep_subjobs.jsonl` now 87 records. Stopped per supervisor
  directive (544/684 rungs need the CPU); no orphaned worker remains.
- Wrote tier draw files for the resume queue (from `screened_draws.jsonl`,
  top band per k, no board/WL collisions): `top_draws_tier2a.json`
  k=20: 125976 (d400 97, w=8), 96205 (95), 42514 (94), 84342 (94);
  `top_draws_tier2b.json` k=18: 133665 (99, w=10), 98119 (98), 111434 (98),
  122889 (98), 122922 (98, w=8); `top_draws_tier2c.json` k=16: 36260 (100,
  w=10), 152739 (100), 7536 (99, w=8), 185399 (99), 2220 (98, w=8). The
  k=18/k=16 tiers are worth deep rungs only after the board move: they need
  d > 76 and their screens sit at 98-100.
- Fixed a latent `NameError` in `analyze_and_stage.stage()` (notes f-string
  referenced undefined `w`; would have crashed the first staging call).
- Consolidated `deep_rungs.jsonl` (10 rung records, per-rung readings and
  winning witnesses; `deep_subjobs.jsonl` remains the authoritative
  checkpoint for resume dedup).

### Staged survivors / gate verdicts

None this window. No gate pass, no gate failure, nothing staged under
`research/candidates/l2-q17-resume/` (directory created by a dry-run of the
save path only; no candidate file written). Staging path itself is verified
end-to-end (make_submission witness re-validation, k=20 confirmed by
`css.compute_k`, `unique_path` -> `544-20-89.json` if 74545 qualifies).

### Checkpoint state for the next resume

1. Leaders need 2 more rungs at their lightest (53244: two rungs reading
   exactly 88; 74545: two reading exactly 89, or any lighter rung resets R
   and needs 2 more at the new R). Resume command: `deep_read2.py --draws
   top_draws_v3.json --seeds 911005 911006 911007 911008` (skips the 30
   done subs, ~6 remain for 911005/911006 across both draws), then analyze
   with `analyze_resume.py --rungs deep_subjobs.jsonl --stage --run-id
   l2-q17-resume`, then `uv run --no-sync python research/kit/coordination.py
   gate <staged path>`.
2. Then tier2a -> tier2b -> tier2c with seeds 911001-911003 each (files
   listed above); same analyze/stage/gate path.
3. 53 unscreened k=16 pool draws remain unqueued (they need d > 82 to have
   mattered under the old board; at the new bar d > 76 the top few are in
   tier2c already).

## Resume 2026-11-06, part 2 (staging + gate, ~23:00-06:05 UTC)

Deep-ladder continuation after the supervisor's wave-1 rungs freed the
machine (2-3 workers, resumable `deep_read2.py`, seeds 911005..911023; two
external throttle-kills absorbed with zero witness loss — per-sub checkpoint
flushes held every time). Final leader state at 20,000 trials/side:

- i=53244 (k=20, w=10): 19 complete fresh-seed rungs, chronological
  readings [911001:89, 911002:93, 911003:88, 911004:90, 911005:89,
  911006:87, 911007:90, 911008:87, 911009:90, 911010:89, 911011:91,
  911012:88, 911013:88, 911014:89, 911015:91, 911016:88, 911017:89,
  911018:89, 911019:90]. Floor 87 reproduced at rung seeds 911006 & 911008
  (both X-side); no rung ever read below 87.
- i=74545 (k=20, w=10): 19 complete rungs, floor 87 at seeds 911005 &
  911006 (both Z-side); no rung below 87.
- Sibling check: 53244 and 74545 have distinct exact fingerprints but the
  SAME Weisfeiler-Leman signature class (verify/qldpc_verify.signature,
  hash a76c1ee56001cd1d) — one find, not two.
- The strict 3-rungs-at-lightest bar was not reached by either draw
  (empirical P(rung reads exactly 87) ~ 1/10; 2 agreeing rungs each after
  19 rungs). Coordinator authorized staging at the 2-agree + stable-floor
  evidence level (promote's MIN_FLAT_RUNGS=2 satisfied by the packaging
  witness + trusted-gate refute tail).

### Staged survivor / gate verdict

- **research/candidates/l2-q17-resume/544-20-87.json** — [[544,20,87]]
  Kasai affine 2BGA Aff(F_17), q=17, r=3, a=[21,38,57,60,186,196,209,217,
  219,251], b=[4,35,54,55,152,180,206,230,240,246] (w=10, check weight 20).
  Claim d <= 87 (upper_bound at the lightest reading): X <= 87 with two
  independent weight-87 witnesses (rung seeds 911006, 911008; primary
  embedded, second in the sidecar and checkpoint), Z <= 88 (seed 911003).
  Sidecar `544-20-87.evidence.json` carries the full ladder, both floor
  supports and the sibling corroboration. Rebuild spec embedded
  (bbga_labels.build_2bga_affine, q=17, a, b).
- Gate (`research/kit/coordination.py gate`): **passed** —
  `research/candidates/l2-q17-resume/544-20-87.verdict.json`: dedup clean,
  novelty `board_advancing: true` with `advances_by: [d, k, n, w]`,
  `dominated_by: []`, and `refute: {refuted: false}` at seed 268056721
  (the gate's own refutation search found nothing lighter than 87).
  Labels: "advances the weight-9plus x unrestricted board".
- A 1,000,000-trial-per-side rung is supervisor-owned and pending; per the
  +5 offset(1M) family calibration the expected reading is 84-87 and the
  entry repackages at the lightest reading per playbook. True d estimated
  78-82; [[544,20,>=77]] dominates the merged [[544,18,76]].
- One packaging attempt was quarantined to `rejected/` (schema: extra
  `note` key in witness_provenance); fixed and re-saved. The saved doc
  preflights clean (save_submission preflight passed on the live copy).
- i=24989 (k=22): confirmed dominated miss (weight-24 Z-logical at rung
  911001; screen had read 98). i=74545: not staged (same WL class as the
  staged find; corroborates the 87 floor on its Z side).

### Post-staging screening (tier2a, 2 workers)

`screen_corner.py` over the 53 not-yet-screened k in [16,22] corner draws
(k-descending order, 400-trial RIS behind the kit prepass, appended to
`screened_draws.jsonl`). Results appended to this section when the chunk
completes. No deep ladders: the 1M rung on 544-20-87 is supervisor-owned.

### Checkpoint state for the next resume

- `deep_subjobs.jsonl` (authoritative resume state): 316+ sub-search
  records, every witness persisted. Leaders complete through seed 911019;
  partials exist at 911020 (53244 Z-side only). Resume command if the 1M
  rung leaves headroom: `deep_read2.py --draws top_draws_v3.json --seeds
  911020 911021 ...` (skips done subs).
- `deep_rungs.jsonl`: consolidation index (re-run the aggregation snippet
  in analyze_resume / stage scripts after any resume).
- tier2a/2b/2c draw files (k=20/18/16 next tiers) remain queued with zero
  deep work; screen first, then decide.

### Screening results (completed 06:5x local)

The 53-draw chunk completed: the ENTIRE corner pool is now screened,
253/253 (249 `screened`, 4 `prepass_dropped`; zero board-exact/WL
collisions anywhere). Top of the new chunk, by 400-trial reading:

- k=16 (bar now d > 76): 236335 (99, w=10), 209689/237250/257595 (98, w=10),
  218135/249157/254979 (98, w=8) — plus the earlier 36260/152739 (100),
  7536/185399 (99). Seven draws at 98-100 in this tier alone.
- k=18 (bar d > 76): 235692 (97, w=10), 248699 (97, w=8) — new; earlier
  133665 (99), 98119/111434/122889 (98), 122922/159043 (98, w=8).
- k=20 (bar d > 70): 125976 (97, w=8) — never deep-read; 143947/157378/
  242078 (96).
- k=22: 208430 (95), 162564 (94).

Next-lane priority if the supervisor orders another ladder after the 1M
rung: the k=16 98-100 band (offset framework puts their true d at ~78-84
vs bar 77 — advance candidates with w=8 available), then k=18 97-99, then
k=20 125976 (w=8). All past the kit prepass with no board WL collisions.
