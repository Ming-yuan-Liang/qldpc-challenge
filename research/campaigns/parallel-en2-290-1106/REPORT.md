# REPORT — lane en2-290 (PHASE 1 EN-2 winner deep read + PHASE 2 q17-s20 continuation)

Campaign dir: `research/campaigns/parallel-en2-290-1106/` (this dir).
Run id for staging: `en2-290-1106` (QLDPC_RUN_ID).
Date: 2026-11-06. Stage-only; nothing here is a submission.

**Staged survivor (gate-passed): `research/candidates/en2-290-1106/544-10-88.json`**
verdict `research/candidates/en2-290-1106/544-10-88.verdict.json` (passed,
board_advancing true, refute clean).

## PHASE 1 — the EN-2 winner's true reading

### Where the winner was

There is no n=290 code: **290 is the screen-cache index** of the winner inside
`research/campaigns/affine-elite-nbhd-544-18-84/screen_cache.json` (the EN-2
lane's cache). The EN-2 winner is the **b3 single-coordinate move of the
[[544,18,84]] q=17 elite**:

- a = [245, 84, 96, 270, 163, 268]  (unchanged elite a)
- b = [245, 252, 47, **59**, 143, 70]  (b[3] 231 -> 59)
- Kasai affine 2BGA on Aff(F_17), n = 2*q*(q-1) = 544, k = 18, max check
  weight 12 (verified on the dense build: HX/HZ 272x544, row weight 12).
- Screen claim (400-trial numpy RIS): [[544,18,96]], eff 304.9.
- It was never deep-read and never staged: the EN-2 lane stopped before its
  refinement rungs, and the b3ridge campaign (EN-3) that wanted it as a center
  never ran either (its dir holds only campaign.json + run.py).

Corroboration: `research/campaigns/affine-elite-nbhd-544-q17-b3ridge/campaign.json`
("The EN-2 winner (b3 single-coordinate move of the [[544,18,84]] elite,
screen [[544,18,96]] eff 304.9)") and the screen cache entry idx 290 itself.

### Deep read (this lane) — final

Instrument: `research/kit/surrogate.py::distance_rand_witness`, numpy backend,
20,000 trials/side, default pair_depth=10 (the lane instrument the screen and
the earlier 20k rungs used). Three fresh seeds (930001-930003); each rung
spent as five 4,000-trial checkpointed chunks (deterministic derived chunk
seeds = rung seed + c*1000003, progress flushed per chunk). Final chunk
readings and rung minima:

| seed | chunks (order) | rung reading d<= |
|------|----------------|------------------|
| 930001 | 88, 86, 88, 90, 88 | **86** |
| 930002 | 90, 90, 88, **84**, 90 | **84** |
| 930003 | 90, **84**, 86, 86, 90 | **84** |

**The EN-2 winner's honest reading is d <= 84** (X-side witnesses at weight 84
from seeds 930002 and 930003 are preserved in
`phase1_witness_seed930002.json` / `phase1_witness_seed930003.json` and their
`.progress` files). The three rungs agree flat at 84 (spread 2), so the
reading itself is solid — it is the SCREEN claim of 96 that was inflated, by
12 units, far beyond the lane's within-2 staging window.

### Decision

**NOT staged, per the lane rule** ("if readings collapse below claim, record
the honest reading and do NOT stage"): lightest 84 vs claimed 96, delta 12.
`phase1_stage.py` records the same decision (run output in the log section
below). Nothing was lost: every chunk's witness support is on disk, so the
supervisor can package [[544,18,84]] at the honest reading without re-running
any search.

### Peer context (why this reading matters)

The incumbent at (544, 18, w12) is [[544,18,82]] (`codes/544-18-82.json`,
whose checks this lane verified byte-identical to the staged 544-18-84), and
CI RIS-fast REFUTED its claim on 2026-11-05 with a valid weight-76 Z-logical
(re-verified by this lane via
`research/campaigns/_12h-portfolio-shared/verify_ci_witness.py` against
codes/544-18-82.json: `is_logical: true`, side Z, weight 76; witness at
`research/campaigns/_12h-portfolio-shared/ci-witnesses/544-18-76.json`).
So at (544, 18, w12) the honest frontier reading is d<=76, and the EN-2
winner's honest d<=84 is a genuine 8-unit d gain at equal (n, k, w) — a
d-only gain, which per AGENTS.md needs the matched-depth peer audit
(`research/audits/leader_audit.py pair`) before any submission. Packaging and
submitting that gain is the supervisor's call; this lane's rule barred it
from staging.

## PHASE 2 — kasai-affine-q17-directed-s20 continuation

The original lane (`research/campaigns/kasai-affine-q17-directed-s20/`) never
ran: its dir holds only campaign.json + run.py, no screen_cache/summary. This
lane executed its generator config on this lane's budget: **100 fresh draws**
of `sample_kasai_affine(100, q_range=(17,17), weight=6, seed=20)` (the first
100 of exactly what that campaign declares).

### Screen (400 trials, board prepass)

- 100/100 screened; prepass audit: 0 not-CSS, 0 k-rejected, 0 repeats,
  0 disconnected, 0 board-exact, 0 board-WL flagged. Clean band.
- Cache: `screen_cache.json` (lane_runner format);
  ranked: `phase2_screen_ranked.json`.

Top 10 by screen efficiency (all n=544, w=12; screen readings are inflated
upper bounds — see briefing bias note):

| idx | screen d | eff | a | b |
|-----|----------|-----|---|---|
| 6 | 98 | 176.5 | 41,46,195,120,100,125 | 4,106,142,66,174,103 |
| 94 | 97 | 173.0 | 174,198,53,265,69,57 | 199,81,111,129,192,11 |
| 3 | 92 | 155.6 | 165,223,27,80,191,187 | 66,145,136,179,199,105 |
| 53 | 97 | 138.4 | 82,189,174,70,258,245 | 225,224,31,64,234,160 |
| 76 | 97 | 138.4 | 95,15,225,142,122,125 | 153,54,95,224,148,250 |
| 88 | 97 | 138.4 | 6,260,120,7,98,16 | 214,245,59,109,114,125 |
| 9 | 96 | 135.5 | 53,206,57,158,200,120 | 33,56,146,139,158,14 |
| 79 | 96 | 135.5 | 8,74,122,169,44,255 | 87,195,72,115,100,101 |
| 84 | 94 | 129.9 | 21,54,180,230,50,130 | 130,68,97,266,205,212 |
| 49 | 99 | 108.1 | 7,128,155,258,83,107 | 68,143,262,103,130,92 |

### Deep read: top-3 k=10 leaders, 3 fresh-seed 20k rungs each

Nine rungs (seeds 10000+idx, 20000+idx, 30000+idx), five 4,000-trial
checkpointed chunks each. Final chunk readings and rung minima:

| idx | screen d | rung 10000+ | rung 20000+ | rung 30000+ | minima | verdict |
|-----|----------|-------------|-------------|-------------|--------|---------|
| 6 | 98 | 90,90,94,90,88 | 92,90,92,88,90 | 90,90,88,92,90 | **88/88/88** | **STAGED + GATE PASSED** |
| 3 | 92 | 88,95,86,89,91 | 93,92,87,93,92 | 89,92,90,89,90 | 86/87/89 | not staged (spread 3) |
| 94 | 97 | 91,90,93,90,92 | 88,92,88,86,85 | 89,92,82,92,93 | 90/85/82 | not staged (spread 8; lightest 82) |

### The staged survivor: [[544,10,88]] w=12

- Path: `research/candidates/en2-290-1106/544-10-88.json`
- Verdict: `research/candidates/en2-290-1106/544-10-88.verdict.json`
- Gate: `passed: true`; dedup clean (no exact/WL duplicate); novelty
  `board_advancing: true`, `advances_by: [d, k, n, w]`, `d_only_gain: false`,
  `dominated_by: []`; refute "no lighter logical in 8000 RIS trials (seed
  827912269)"; verify ok (weight-9plus, unrestricted).
- Claim: d <= 88, confidence upper_bound. Three fresh-seed 20,000-trial rungs
  read 88/88/88 (spread 0 — flat at the claim). Witnesses: X <= 90, Z <= 88
  (Z-side 88 witness found independently in three rungs); per-side
  witness_provenance records the honest chunk budget (found at 4,000-trial
  chunk, survived 60,000 samples/side across the three rungs; tool
  `research/kit/surrogate.distance_rand_witness`).
- Construction: Kasai affine 2BGA Aff(F_17), a=[41,46,195,120,100,125],
  b=[4,106,142,66,174,103]; rebuild spec embedded
  (`bbga_labels.build_2bga_affine`, params q/a/b).
- Frontier note: vs the cell incumbent [[544,18,82]] (honest CI-refuted
  reading 76), this code trades k (10 vs 18) for d (88 vs 82 claimed / 76
  honest) at equal n and w — a Pareto frontier extension, gate-confirmed
  non-dominated.

### Non-staged deep reads (recorded, not lost)

- idx3 [[544,10,86]]: rungs 86/87/89, spread 3 — outside the flat bar; honest
  lightest 86. Witnesses in `p2_idx3_seed*.json`.
- idx94: rungs 90/85/82, spread 8 — the third rung found a weight-82 logical;
  honest lightest 82, at which the code is dominated by [[544,18,82]] at
  equal n/w (k 10 < 18, d 82 <= 82). Textbook instrument-collapse; the
  flatness bar caught it before any staging.
- k=8 draws (idx 53/76/88, screen 97) were DEFERRED, not deep-read: at equal
  n and w the k=10 leaders at honest d 82-88 leave no room for a k=8 code to
  clear the frontier without a substantially higher d, and the lane's CPU
  budget (heavy external contention, see below) went to the required third
  rungs. Recorded as an honest deferral, not a negative.

## Environment note

The machine was heavily oversubscribed during this lane (~60 python
processes; the two sibling lanes plus this lane's jobs on 20 cores, with
memory-thrash making a 4,000-trial chunk cost 1,100+ CPU-seconds). Three
external kill waves (exit 137, not this lane) killed the first two
generations of rungs; since then every rung ran as a detached process with
4,000-trial checkpoint chunks flushed to disk, so kills lost at most one
chunk. One launcher-path bug cost one duplicated chunk per rung (diagnosed
from the .err files, fixed, relaunched). All 60/60 chunks of the planned
protocol completed.

## Deliverables

- Staged survivor: `research/candidates/en2-290-1106/544-10-88.json`
  (verdict: `research/candidates/en2-290-1106/544-10-88.verdict.json`) —
  gate-passed, board-advancing, 3 fresh-seed 20k rungs flat at the claim.
- EN-2 winner honest reading: **d <= 84** (claimed 96 at screen; delta 12;
  not staged per lane rule; witnesses preserved for a supervisor repack).
- All rung witness JSONs and checkpoint progress files in this directory;
  screening cache `screen_cache.json`; nothing staged outside
  `research/candidates/`; `verify/` untouched; no git operations.

---

# 2026-11-06 (follow-up lane L3 "l3-en2") — paired-depth audit of the EN-2 winner + q17 k>=12 breadth

Lane brief: audit the EN-2 winner (screen-cache idx 290, the b3 single-coordinate
move of the [[544,18,84]] q17 elite: a=[245,84,96,270,163,268],
b=[245,252,47,59,143,70], n=544, k=18, w=12) against the merged incumbent
`codes/544-18-76.json` at matched depth; package+gate+stage under
`research/candidates/l3-en2/` only if the honest lightest flat reading is
d<=84 AND it dominates the incumbent on the board's Pareto axes. Phase 2:
widen q=17 screening breadth toward the k>=11 at d>=88 corner, reusing
`screen_cache.json`. Stage-only; gate or it is not a find.

## PHASE 1 — paired-depth audit (instrument: surrogate.distance_rand_witness, numpy backend, default pair_depth=10, 20,000 trials/side per rung spent as five 4,000-trial checkpointed chunks, fresh seeds, chunk seeds = rung seed + c*1000003)

### Winner readings (all rungs on disk in this directory)

| rung seed | provenance | chunks (order) | rung reading |
|------|------------|----------------|--------------|
| 930001 | lane en2-290-1106 | 88, 86, 88, 90, 88 | 86 |
| 930002 | lane en2-290-1106 | 90, 90, 88, 84, 90 | **84** (X) |
| 930003 | lane en2-290-1106 | 90, 84, 86, 86, 90 | **84** (X) |
| 830001 | lane l3-en2 (fresh) | 90, 86, 90, 88, 90 | 86 (Z) |

**Honest lightest flat reading: d <= 84** (four 20k rungs, min 84, spread 2;
no chunk of any rung ever read below 84). Witness inventory across all 20
chunks on disk: lightest X support weight 84 (chunk seed 3930011 = rung 930002
chunk 3; independently, rung-level X@84 supports in
`phase1_witness_seed930002.json` and `phase1_witness_seed930003.json`),
lightest Z support weight 86 (chunk seed 2930009 = rung 930003 chunk 2). A
packaged doc would claim d=84 with witnesses X<=84, Z<=86.

### Incumbent `codes/544-18-76.json` at matched budget (lane l3-en2)

| rung seed | chunks (order) | rung reading |
|------|----------------|--------------|
| 830011 | 90, 88, 88, 90, 88 | 88 (Z) |

Consistent with the known instrument-depth bias: at 20k trials/side the numpy
RIS reads 8-12 units above the deep truth on this profile (the incumbent's
board claim d=76 is CI RIS-fast's 2026-11-05 refutation reading, backed by a
weight-76 Z-logical the previous lane re-verified). Further incumbent rungs
(830012/830013) were planned but CUT by the supervisor's rung-priority hold;
the dominance comparison below does not depend on them (claim vs claim, both
witness-backed).

### Construction pin (coordinator task 1, 2026-11-06 ~11:55)

Pinned from the phase records (screen idx 290 of the affine-elite-nbhd cache;
b3 move of the [[544,18,84]] elite), rebuilt with the COMMITTED primitives —
`research/kit/group_algebra.py`: `mul, _ = metacyclic(17, 16, 3)` (Z_17 x|
Z_16, order 272, primitive root 3), then `HX, HZ = build_2bga(mul, a, b)`:

- **a = [245, 84, 96, 270, 163, 268], b = [245, 252, 47, 59, 143, 70]** (the
  b3 move: elite b[3] 231 -> 59), q=17.
- Rebuild: n=544, k=18, `verify_css` ok, max check row weight 12 on both
  sides. `verify/qldpc_verify.py::css_fingerprint` on the dense rebuild:
  **facbfe8f45fba8e2**. The kit's second build path
  (`research/kit/bbga_labels.build_2bga_affine(17, a, b)`) produces
  byte-identical matrices.
- Witness-to-rebuild validation (`surrogate.validate_logical`, raw matrices):
  `phase1_witness_seed930002.json` X@84 -> ok; `phase1_witness_seed930003.json`
  X@84 -> ok; rung 930002 chunk-3 chunk-level X@84 (chunk seed 3930011) ->
  ok (same support as the rung-level file); rung 930003 chunk-2 Z@86 (chunk
  seed 2930009) -> ok; lane l3-en2 fresh rung 830001 Z@86 -> ok. The
  preserved witnesses belong to exactly this rebuilt code. These params are
  what the supervisor's 1M rung chain should use for the winner.

### Dominance and decision (REVISED ~12:00 by coordinator task 2 — raw-reading dominance is NOT sufficient)

- Raw comparison: winner honest claim d<=84 vs incumbent board claim d=76
  (CI-refuted, witness re-verified), equal n=544, k=18, w=12 -> strict on d
  only. Audit bar (lightest flat reading <= 84): MET (84).
- **CI-offset correction (REVISED in place ~14:20 per supervisor's critical
  correction — the rule previously recorded here was INVERTED)**: a surrogate
  reading is an UPPER bound; a LIGHTER reading means the search FOUND a
  lighter logical, i.e. a SMALLER true distance, which is WORSE for board
  value. Offset form: offset(D) = R_inc(D) - 76 (incumbent surrogate reading
  minus its CI-proven true distance, same n/w/family); the winner's estimated
  true d is est_true = R_win(D) - offset(D); the winner advances iff
  est_true >= 77, i.e. **R_win(D) >= 77 + offset(D) = R_inc(D) + 1**.
  At 20k: offset = 88 - 76 = 12, so the winner needed R >= 89 and read 84 —
  **FAILS**; at matched 20k budget the evidence is that the winner's true d
  is LOWER than the incumbent's, not higher (estimate ~72 — a reading-depth
  artifact, not a property of the code). Both the raw reading (84, lightest
  flat upper bound, witness-backed) and this corrected interpretation stand.
- **Corrected paired-1M decision rule (supervisor-owned probe)**:
  winner_alive iff **R_win(1M) >= 77 + (R_inc(1M) - 76)** — the winner's
  matched-1M reading must EXCEED the incumbent's matched-1M reading, never
  sit below it. Supervisor context: their [[544,10,78]] has
  est_true = 78 - offset(1M) and survives only if R_inc(1M) <= ~78 (expect
  held/pending); the 684 family carries its own lighter offsets (historical
  20k controls 115->110, 116->110, 117->108), which is why the 684
  candidates look genuinely strong.
- **DO NOT PACKAGE anything yet** (supervisor directive ~11:55, reaffirmed
  ~14:20). The supervisor owns all rung scheduling; the winner's 1M rung
  (third in the chain, after 684) will use the pinned params above. This
  lane stages nothing in PHASE 1; the probe decides.

## PHASE 2 — q17 breadth toward k>=11 (k is always even in this family) at d>=88

- Sibling lane `research/campaigns/parallel-q17-k18-1106/` established: k is
  even for Kasai affine 2BGA (k in {12,14,16,18,20,22} for k>=11); their
  260k-draw pool (`pool_draws.jsonl`) labels k per draw; their lane is deep-
  reading the k>=16 corner. This lane takes the untouched k in {12,14} niche.
- Extracted from their pool into `l3p2_pool_k1214.jsonl`: 1,913 draws
  (k=12: 629 w8 / 142 w9 / 578 w10; k=14: 282 w8 / 282 w10; w = per-set
  exponent count, check row weight = 2w), sorted w8-first. This lane's own
  weight-6 screen cache (100 draws) holds no k>10, so the pool reuse avoids
  rescreening-by-generator and goes straight to the k>=12 population.
- Screening: 400-trial numpy RIS behind the kit prepass
  (`search.screen`, within-batch fingerprint dedup), single bounded burst of
  110 draws (w8 k14 first) launched 11:22 as a 3rd-slot short burst. KILLED
  by an external kill wave ~12:35 (harness reports the background task
  stopped, not exited) BEFORE its batch-end write — `l3p2_screened.jsonl`
  does not exist, zero readings captured, ~75 CPU-minutes lost. The batch-end
  write pattern (screen() computes the whole chunk before flushing) is the
  lesson: on resume, screening must run in small slices (--limit 25-35) or
  with a per-draw append, so a kill loses at most one slice. Relaunch DEFERRED
  to the resume per the hold; deep reads (3 fresh-seed 20k rungs per
  candidate, flat bar spread<=2) and any staging likewise deferred.
- Board context for the corner: dominators at n<=544 are [[544,18,76]] w=12
  (need d>76 for k in {12,14,16,18}) and [[514,32,70]] w=16 (need d>70 for
  k in {20,22}); a k>=12 find at d>=88 also dominates the staged
  [[544,10,88]] (k strictly larger).

## Hold status (2026-11-06 ~11:40 supervisor directive; extended ~11:55)

Deep rungs for 544/684 take the CPU. Lane l3-en2 holds: zero new worker
processes; the one live screening burst exits naturally at batch end. PHASE 1
packaging is CANCELLED for this lane pending the supervisor's matched-1M
paired probe (winner vs incumbent, pinned params above; decision rule as
corrected above: R_win(1M) >= 77 + (R_inc(1M) - 76)). On resume this lane:
(1) phase-2 rank + deep-read k>=12 leaders; (2) CPU-free support for the
supervisor's rung chain on request. Supervisor files (`timing_probe.jsonl`,
`progress_1m_w*.jsonl`, `rung_w*.log`, `battery_544_10_88*.log`) untouched
throughout.

### PHASE 2 screening checkpoint 1 (bounded resume, 2026-11-06 ~14:05)

Supervisor bounded-resume directive (~13:45): exactly ONE worker on the
kill-tolerant per-draw screener `l3p2_screen_slice.py` over the k in {12,14}
pool, 400 trials/draw, per-draw flush; no deep reads, no gates, no second
worker. The screener now builds `prescreen.board_index()` ONCE and passes it
to every draw (board exact/WL dedup active per draw; the earlier batch used
index=None). Rate ~44 s/draw under the supervisor's 8-worker load.

Checkpoint after 85 draws (~all k=14 w8; 1,913 in pool; 0 prepass_dropped,
0 board collisions): top-10 by d400:

| pool_i | k | w | d400 | eff | fingerprint |
|--------|---|---|------|-----|-------------|
| 48042 | 14 | 8 | 100 | 257.4 | f996db4ce3b54583 |
| 66069 | 14 | 8 | 100 | 257.4 | 00c557852858aa33 |
| 1787 | 14 | 8 | 98 | 247.2 | b8f2acd6abcc22b0 |
| 2022 | 14 | 8 | 98 | 247.2 | 5e8fd3e3ef5fca88 |
| 23061 | 14 | 8 | 98 | 247.2 | d066419c85d2490c |
| 28636 | 14 | 8 | 98 | 247.2 | c8056df0585045cd |
| 33871 | 14 | 8 | 98 | 247.2 | f6c9e08c08da2f34 |
| 35511 | 14 | 8 | 98 | 247.2 | 7f02d11b7d0af451 |
| 38795 | 14 | 8 | 98 | 247.2 | 897ae69cf185a2fd |
| 46091 | 14 | 8 | 98 | 247.2 | 8e10a989a2e0d142 |

d400 distribution so far (k=14 only): 2 draws at 100, 67 at 90-99, 1 at 80s,
12 at 10-29 (structural duds), 1 at 0-9. Screen readings are inflated upper
bounds (known bias); the deep-read shortlist will be drawn from the
d400 >= 96 tail after the full pass. No deep reads run (rung priority).

### PHASE 2 screening STOP (2026-11-06 ~15:15): two external kills, rule reached

The relaunched per-draw screener was killed by a second external kill wave
(~15:10, mid-draw again; per-draw flush held — all completed draws are on
disk, only the draw in flight was lost). That is the SECOND death under the
bounded-resume directive, so per the supervisor's rule this lane STOPPED:
no further relaunches, zero lane workers now, no deep reads, no gates.

Screening coverage at stop: 195/1,913 pool draws (all of them k=14 w8; the
w8-k14 block is 195/282 done; 0 prepass_dropped, 0 board exact/WL collisions).
Every line is in `l3p2_screened.jsonl` with its spec, so nothing needs
rescreening. Current top-10 by d400 (screen readings are inflated upper
bounds; deep-read shortlist would come from the >=96 tail):

| pool_i | k | w | d400 | eff | fingerprint |
|--------|---|---|------|-----|-------------|
| 48042 | 14 | 8 | 100 | 257.4 | f996db4ce3b54583 |
| 66069 | 14 | 8 | 100 | 257.4 | 00c557852858aa33 |
| 94899 | 14 | 8 | 99 | 252.2 | 9053d5a490be4974 |
| 140783 | 14 | 8 | 99 | 252.2 | 63f9d6e439ee6716 |
| 165965 | 14 | 8 | 99 | 252.2 | a475b3420adc52d1 |
| 179566 | 14 | 8 | 99 | 252.2 | 618b77f100ed6001 |
| 1787 | 14 | 8 | 98 | 247.2 | b8f2acd6abcc22b0 |
| 2022 | 14 | 8 | 98 | 247.2 | 5e8fd3e3ef5fca88 |
| 23061 | 14 | 8 | 98 | 247.2 | d066419c85d2490c |
| 28636 | 14 | 8 | 98 | 247.2 | c8056df0585045cd |

d400 distribution (k=14 w8, 195 draws): 2 at 100, 4 at 99, 8+ at 98 (8 shown,
more in file at 98), 162 at 90-99 band total, 2 at 80s, 29 structural duds
(<=29). Remaining unscreened pool: 1,718 draws (87 k14 w8, 629 k12 w8,
142 k12 w9, 578 k12 w10, 282 k14 w10) — resumable with one command
(`l3p2_screen_slice.py`), zero overlap with what is done.

Lane state at stop: PHASE 1 closed pending the supervisor's paired-1M probe
(corrected rule above); PHASE 2 screening stopped by the two-kill rule; the
shortlist decision (which draws earn 3 fresh-seed 20k rungs) is deferred
until the supervisor signals rungs-done and screening can resume.
