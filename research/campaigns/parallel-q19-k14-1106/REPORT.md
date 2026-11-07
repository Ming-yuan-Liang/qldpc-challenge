# REPORT — lane q19-k14 (Kasai affine 2BGA over Aff(F_19), n = 684)

Campaign dir: `research/campaigns/parallel-q19-k14-1106/` (this directory).
Date: 2026-11-06. Stage-only lane: nothing is written to `codes/`, nothing
committed; staging goes to `research/candidates/parallel-q19-k14-1106/`.

## Protocol

- Draws: 250 deterministic draws (`bench_one.py::draw_pair`, base seed
  20261106 + draw index): |a| = |b| = w with w uniform in {7, 8, 9}, exponents
  uniform in [0, 342), distinct within a side (F_2[G] support). Group:
  metacyclic realization of Aff(F_19) = Z_19 x| Z_18 (primitive root 2),
  `bbga_labels.build_2bga_affine(19, a, b)`; n = 2*19*18 = 684, check weight
  = 2w in {14, 16, 18}.
- Corner: k in [12, 16] kept (the k=10 sampler-trap corner avoided by filter:
  draws with k outside [12, 16] are recorded `k_out` and never read).
- Screen: gate prepass (CSS by construction, `prescreen.block_structure`
  connectivity), within-batch dedup on `verify/qldpc_verify.py::css_fingerprint`
  (cross-chunk dedup in `select_top.py`), then a 400-trial RIS reading
  (`surrogate.distance_rand_witness`, numpy backend, pair_depth=10 default).
- Deep: each selected draw re-read at 3 fresh seeds (910001, 920002, 930003),
  20,000 trials per side per rung. Instrument: `surrogate.lightest_logical`
  per side on the same spawned SeedSequences `distance_rand_witness` uses.
  Kill-resistant form: each side's 20k trials split into 8 x 2,500-trial
  sub-chunks on independently spawned sub-seeds (statistically the same
  per-trial distribution; progress persisted per chunk). A rung's reading is
  min over all chunks of both sides; per-side witnesses are the lightest
  across that side's chunks, re-validated with `surrogate.validate_logical`.
  Only draws whose three rung readings agree flat (same lightest weight) are
  staged.
- Gate: `uv run --no-sync python research/kit/coordination.py gate <path>`;
  verdict at `<path>.verdict.json`. Only `passed` + `board_advancing: true`
  count as finds; `board_advancing: false` is recorded as a dominated miss.

## Screening (250 draws)

Raw chunk files: `screen_0.jsonl` ... `screen_9.jsonl` (25 draws each);
merged selection: `select.json`.

- 250/250 built and passed the CSS-by-construction check.
- 245 draws fell outside k in [12, 16] (recorded `k_out` with full a, b in
  the chunk JSONLs): k distribution concentrated at k = 0, 2, 4 with w = 9
  draws reading the smallest k.
- 0 disconnected, 0 errors, 0 fingerprint duplicates (within chunk or
  cross-chunk).
- 5 unique in-range draws, all read at 400 trials:

| draw | w | k | screen reading | side | eff k*d^2/n | fingerprint |
|------|---|---|----------------|------|-------------|-------------|
| 229 | 8 | 14 | d <= 120 | Z | 294.74 | 1feea67bdb46f22b |
| 106 | 7 | 12 | d <= 124 | X | 269.75 | 0d6f18523b515869 |
| 12 | 7 | 12 | d <= 126 | X | 278.53 | 7f5fa8769f77d598 |
| 70 | 7 | 12 | d <= 126 | Z | 278.53 | edc92c4224cca80f |
| 72 | 8 | 12 | d <= 127 | X | 282.96 | c5fde47be3024775 |

Fewer than the planned ~8 in-range draws: the k = 12-16 corner is sparse
under |a| = |b| in {7, 8, 9} (a 60-draw probe before the full run showed the
same yield), so all 5 reads were deepened.

Board context at n = 684 (any-weight, unrestricted CSS cell): 684-12-45/51/54,
684-12-117 (w=16), 684-14-54, 684-14-115 (w=16), 684-20-36, plus high-k
entries. All five draws have check weight 14 or 16.

## Deep readings (3 fresh seeds x 20,000 trials/side)

(raw chunk records: `deep_<draw>_<seed>.jsonl`; final lines carry the rung
readings and both witnesses)

(to be filled on completion)

## Staging + gate verdicts

(to be filled on completion)

## Honest-claims notes

- Every distance in this report is an upper bound at the lightest reading;
  none is exact.
- The chunked deep form keeps the instrument (`lightest_logical`, numpy,
  pair_depth=10) and the 20,000-trials/side budget per rung, but splits each
  side's budget into 8 spawned sub-seed chunks; rung reading = min over
  chunks. This was forced by a harness kill of the first 15 unchunked units
  (~1.5 h of compute lost, no partial output); chunking bounds any future
  loss to one 2,500-trial chunk.
- Known instrument bias (briefing): staged lane readings ran 1-6 units above
  what independent seeds found; CI's RIS-fast 8M-trial class has refuted
  higher claims. Readings here are reported as upper bounds only.

---

## RESUME 2026-11-06 (lane l1-q19-resume, after the previous session's lane died)

Resumed from the 15 deep rungs already in `deep_*.jsonl` (5 draws x 3 seeds);
no redraws. Staging dir: `research/candidates/l1-q19-resume/` (run id pinned
by `l1_stage.py` / `QLDPC_RUN_ID`). New scripts this session (campaign dir):
`l1_stage.py` (flat-survivor staging at the lightest reading across ALL rungs,
>=3 rungs flat at the claim), `l1_screen.py` (continuation stream, base seed
20261107, w in {6,7,8}), `l1_deep_unit.py` (deep_unit protocol for the
continuation stream), `l1_verify_recon.py` (reconstruction proof).

### Reconstruction of `research/kit/bbga_labels.py`

The untracked module was lost with the dead lane's session. Rebuilt from the
committed primitives (`group_algebra.metacyclic(q, q-1, r)` + `build_2bga`,
r = smallest primitive root = 2 for q=19) and **proven exact** before any use:
all five recorded `css_fingerprint`s reproduce (229 `1feea67bdb46f22b`,
106 `0d6f18523b515869`, 12 `7f5fa8769f77d598`, 70 `edc92c4224cca80f`,
72 `c5fde47be3024775`) and all ten per-side lightest witnesses from the 15
checkpointed rungs validate under `surrogate.validate_logical` on the rebuilt
matrices.

### Checkpoint tally at resume (15 rungs, previous session)

| draw | k | w | readings by seed (910001/920002/930003) | lightest | flat at lightest |
|------|---|---|------------------------------------------|----------|------------------|
| 70   | 12 | 7 | 120 / 120 / 120 | 120 | 3 -> stageable |
| 106  | 12 | 7 | 120 / 116 / 116 | 116 | 2 |
| 229  | 14 | 8 | 116 / 120 / 116 | 116 | 2 |
| 12   | 12 | 7 | 120 / 118 / 120 | 118 | 1 |
| 72   | 12 | 8 | 122 / 119 / 120 | 119 | 1 |

### Deep rungs completed this session

- `deep_106_940004.jsonl`: reading **116** (wx=116 witness at X chunk 3,
  validated) -> draw 106 has **3 rungs flat at 116** (920002, 930003, 940004).
- `deep_229_940004.jsonl`: reading **118** (wx=122, wz=118; new Z witness at
  118, validated) -> draw 229 stays at 2 rungs flat at 116; its claim is still
  116 (lightest across all rungs), one more 116 rung needed.

Rung pace this session ~150-180 s per 2,500-trial chunk (16 chunks/rung).

### Staged + gate verdicts (both PASSED, board-advancing)

| candidate | draw | claim | gate verdict path | refute | novelty |
|-----------|------|-------|-------------------|--------|---------|
| `684-12-120.json` | 70 | d<=120 (upper bound, 3 flat rungs) | `research/candidates/l1-q19-resume/684-12-120.verdict.json` | not refuted, 8000 RIS trials (seed 1749581554) | advances weight-9plus x unrestricted CSS board on d,k,n,w; no dedup/WL collision |
| `684-12-116.json` | 106 | d<=116 (upper bound, 3 flat rungs: 920002/930003/940004) | `research/candidates/l1-q19-resume/684-12-116.verdict.json` | not refuted, 8000 RIS trials (seed 513260671) | advances weight-9plus x unrestricted CSS board on d,k,n,w; no dedup/WL collision |

Both beat the merged [[684,12,108]] on d at equal n/k, and neither is
d-only-gain flagged. Claims are upper bounds at the lightest reading (never
"exact"); certification pending server distance gate.

Gate failures / dominated misses this session: none so far.

### Screening burst (slot 3, finished before the hold)

`l1_screen_0.jsonl`: 150 continuation draws (base seed 20261107, w in
{6,7,8}, k in [12,16] filter): 149 k_out (k concentrated at 0/2/4/6: 24/54/
37/21; 4 draws at the k=10 trap corner, excluded), **1 read**:

- new-stream draw **84**: w=6, k=12, connected, screen d<=126 (Z side,
  400 trials), fp `5e091ef5b6f62eb2`, eff 278.53.

The w=6 shift did NOT lift the in-range yield: the k>=12 corner of this
family is sparse (~1-2%). Draw 84 is deep-read-pending (needs 3 fresh rungs
via `l1_deep_unit.py`, ~45 min each at current pace).

### Supervisor CPU directive + checkpoint state (hold window)

Supervisor rungs (544/684) took the CPU: chain wrappers for the queued
950005 rungs were killed (no new workers); the two mid-flight rungs
`deep_12_940004.jsonl` and `deep_72_940004.jsonl` (started 11:56) were
allowed to finish naturally and both landed before the hold:

- `deep_12_940004.jsonl`: reading **118** (wx=118 AND wz=118) -> draw 12 now
  120/118/120/118, **2 rungs flat at 118**.
- `deep_72_940004.jsonl`: reading **117** (wx=122, wz=117; new Z witness,
  validated) -> a NEW lightest for draw 72: its claim DROPS to 117
  (122/119/120/117), only 1 rung at 117; the earlier 119 reading is
  superseded, never claim above the lightest.

Zero lane worker processes remain (verified); the lane holds until the
supervisor signals its rungs done. Kill-resume is safe: `deep_unit.py` /
`l1_deep_unit.py` skip completed (side, chunk) pairs from the JSONL.

Full tally now (19 rungs on the original stream):

| draw | k | w | readings (seeds 910001/920002/930003/940004) | claim | flat at claim |
|------|---|---|-----------------------------------------------|-------|---------------|
| 70   | 12 | 7 | 120 / 120 / 120 | 120 | 3 -> STAGED+PASSED |
| 106  | 12 | 7 | 120 / 116 / 116 / 116 | 116 | 3 -> STAGED+PASSED |
| 229  | 14 | 8 | 116 / 120 / 116 / 118 | 116 | 2 |
| 12   | 12 | 7 | 120 / 118 / 120 / 118 | 118 | 2 |
| 72   | 12 | 8 | 122 / 119 / 120 / 117 | 117 | 1 |

Next-resume queue (fresh seeds, 20,000 trials/side, priority order):

1. **229** (k=14): one more rung reading exactly 116 -> stage
   `[[684,14,116]]` (would beat the [[684,14,110]] PR on d). Highest value.
2. **new-stream 84** (k=12): three fresh rungs via `l1_deep_unit.py`.
3. **72** (k=12): two more rungs at 117 -> `[[684,12,117]]`.
4. ~~**12**: one more rung at 118~~ — DROPPED, see the WL scan below: draw 12
   is WL-equivalent to the already-staged 70/106 pair; a third entry of the
   same class adds nothing.

All claims at the lightest reading across all rungs, never above it; a rung
reading BELOW a pending claim lowers the claim to that reading.

### WL-signature scan of the candidate pool (`l1_wl_scan.py`, hold window)

`qldpc_verify.signature` over all six in-range draws (foreground, seconds):

| draw | k | WL signature |
|------|---|--------------|
| 70   | 12 | `f366a1c8ef4edc75` |
| 106  | 12 | `f366a1c8ef4edc75` |
| 12   | 12 | `f366a1c8ef4edc75` |
| 229  | 14 | `0776e8bcbdb50009` |
| 72   | 12 | `67ded76f3a0a15a5` |
| new-84 | 12 | `aa16acc8f19ce0c2` |

**Draws 70, 106 and 12 are one WL class** — almost certainly the same code up
to qubit relabeling. The two staged candidates `684-12-120.json` and
`684-12-116.json` are therefore probably isomorphic, and their claims
(120 vs 116) are readings of ONE true distance; the honest class claim is the
lightest, **d<=116**. The gate could not see this (it dedups against the
board only, and the board has no entry of this signature), but
`verify/check_pr_duplicates.py` will flag the pair at publication. Supervisor
should treat the pair as ONE find, claim d<=116, and prefer the 116 witness
set; the 120 claim is exactly the 1-6-unit instrument bias the briefing
warns about. The same-class draw 12 (claim would have been 118) is dropped
from the queue for the same reason.

The k>=12 corner of this family has ~4 structural classes per ~400 draws
screened (250 old + 150 new): this is the same sampler-trap shape as the
k=10 corner the briefing warns about, just one class larger. Distinct
classes worth rungs: 229 (k=14), 84, 72.

### Post-signal rungs (supervisor rungs-done signal, resumed queue)

Workers relaunched after the signal (two harness kills at ~70-min cadence
during this phase; the chunked checkpoints limited each loss to <=1 chunk,
every unit resumed from its JSONL). Rungs completed:

| (draw, seed) | reading | note |
|--------------|---------|------|
| 229/950005   | 120 | wx=120, wz=121 |
| 12/950005    | **116** | wz=116 witness; draw 12's claim drops to 116 — mirrors its WL class (70/106/12 all bottom at 116) |
| 229/960006   | 121 | wx=121, wz=122 |
| 229/970007   | 117 | wx=117 witness (heavier than 116; claim unchanged) |
| 72/950005    | none | **no nontrivial logical found in 20k+20k trials** (sentinel 20001): draw 72's distance sits at the RIS edge; claim stays 117 (1 flat) |
| 84/940004    | 115 | wx=115 |
| 84/950005    | **112** | wx=112; new-stream 84's claim 112 (1 flat) |
| 84/960006    | 113 | wz=113 (claim stays 112) |
| 229/980008   | 119 | wx=119 |

Draw 229 after 8 rungs (910001/920002/930003/940004/950005/960006/970007/
980008): readings 116/120/116/118/120/121/117/119. Lightest **116**
(two validated witnesses, X and Z of seed 910001), 2 rungs flat at 116 —
[[684,14,116]] still needs ONE more 116 rung; attempts queued (990009,
100010). Supervisor calibration note: inc684 family offset(1M) = +5 ->
est true ~111 if the 116 claim holds; supervisor schedules the 1M rung once
staged.

Draw 84 (new stream, distinct WL class): readings 115/112/113, claim 112
(1 flat). Draw 72: claim 117 (1 flat; one rung found no logical at all).

Pool state at this checkpoint:

| draw | k | class | rungs | claim | flat at claim |
|------|---|-------|-------|-------|---------------|
| 70   | 12 | f366a1c8 | 3 | 120 | 3 -> **STAGED+PASSED** |
| 106  | 12 | f366a1c8 | 4 | 116 | 3 -> **STAGED+PASSED** |
| 12   | 12 | f366a1c8 | 5 | 116 | 1 (WL-covered by the staged pair; closed) |
| 229  | 14 | 0776e8bc | 10 | **115** | 1 -> receding target, staging window closed this session |
| 72   | 12 | 67ded76f | 5 | 117 | 1 |
| 84   | 12 | aa16acc8 | 4 | 112 | 1 (970008 read 117: readings 115/112/113/117) |

### Draw 229 final state (the k=14 line)

Ten rungs (910001/920002/930003/940004/950005/960006/970007/980008/990009/
100010): readings 116/120/116/118/120/121/117/119/**115**/122. The lightest
kept receding as fresh seeds found lighter logicals — 116 (x2), then a valid
117 X witness (970007), then a valid **115** X witness (990009 chunk 6,
`validate_logical` passed) — so the claim is now d<=115 with 1 flat rung.
[[684,14,116]] was staged-blocked when the 115 landed; [[684,14,115]] needs
2 more 115 rungs (~3-6% per pair at the observed distribution). With the
supervisor's inc684 offset (+5 at the 1M class), est true ~110 — an
[[684,14,115]] claim would still dominate the [[684,14,110]] PR if it ever
reaches 3-flat and survives the 1M rung. All nine rungs' witnesses are
preserved and validated in `deep_229_*.jsonl` (nothing lost); the next
resume should weigh whether the receding-target dynamics justify more rungs
or whether the 1M-class instrument should take over this draw directly.

### Session totals

- Gate runs: 2/2 PASSED, both board-advancing (see the table above); no
  refutations, no dominated misses recorded.
- Deep rungs completed this session: 16 (4 before/during the first CPU
  hold, 12 after the rungs-done signal) across draws 229, 106, 12, 72,
  84-new; zero workers running at report close.
- Rungs hit by harness kills: 5 partial (each resumed, <=1 chunk lost).
- Screening: 250 (previous session) + 150 (this session) draws; 6 in-range
  total; the k>=12 corner yields ~1.5% under |a|=|b| in {6..9}.
