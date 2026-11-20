# Search agent briefing (read this first)

Repo root: `C:\Users\Frieren\Documents\QEC\qldpc\qldpc-challenge` (Windows, Git Bash shell).
Machine: Intel Ultra 7 255H, 16C/16T, 31.4 GB RAM (updated 2026-11-06).

## Hard rules (violating any of these is a failed task)

1. **Stage-only**: NEVER write into `codes/`, NEVER `git commit`, NEVER open PRs.
   The supervising session handles publication. You stage candidates under
   `research/candidates/` only.
2. **Never edit anything under `verify/`** — it is the trust anchor. Run it
   unchanged. Do not write your own distance check as a substitute for the gate.
3. **A find is not a find until the gate passes**: run
   `uv run --no-sync python research/kit/coordination.py gate <path>` (the
   `--no-sync` flag matters: without it uv tries to rebuild the env and fails
   on pynauty). The verdict lands in `<path>.verdict.json`.
4. **Never lose a witness**: stage through
   `research/kit/submit.make_submission` + `submit.save_submission(doc,
   coordination.unique_path(f"{coordination.staging_dir()}/<n>-<k>-<d>.json", doc))`.
   If a search finds a valid logical and the save fails, STOP and report it —
   that is a hard error. `save_submission` preflights and moves failures to
   `rejected/` beside the path; read the report.
5. **Dominated codes are not finds**: gate novelty verdict
   `board_advancing: false` means record it in your report as non-frontier and
   move on. Do not stage.

## Environment quirks

- Python: `.venv/Scripts/python.exe` (has numpy, jsonschema, scipy, ldpc,
  pysat, pycryptosat). Long-running work: `uv run --no-sync python ...`.
- **pynauty is NOT installed** on this machine (no Windows wheel, no
  make/gcc). Both consumers fall back automatically: `research/kit/supports.py`
  uses networkx VF2++ (capped), and `verify/heuristic_distance.py` runs
  structural-symmetry-only. The gate runs without it; do NOT try to install it.
- Set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` per process;
  parallelism comes from running several processes, not threads.
- **Machine-wide worker cap (user authorization 2026-11-06): concurrency is
  open, but keep the total python worker processes across ALL lanes ≤ 14** so
  the supervisor's battery and gate runs keep a slot. 2 long workers per lane
  is the baseline; a 3rd slot is allowed for short screening bursts. The
  supervisor checks `tasklist | grep -i python` every round and throttles.
- Bash background jobs spawned with bare `&` die when the wrapper exits. Long
  jobs must run inside the harness's `run_in_background` Bash calls.
- Network to GitHub needs the proxy (already in repo-local git config) and can
  blip (`SSL_ERROR_SYSCALL`, `Connection was reset`) — retry with backoff.

## The distance instrument and its known bias

- Kit surrogate: `research/kit/surrogate.py::distance_rand(hx, hz, trials, seed,
  backend="numpy")` (randomized information-set decoding), returns lightest
  logical weight found (upper bound on d; lower readings = stronger claims).
- **Known bias**: staged lane readings ran 1-6 units above what independent
  seeds found, and CI's deeper `RIS-fast` (8M-trial class, see
  `verify/gate_changed.py`) refuted three of our four submitted claims on
  2026-11-05 (117→108, 82→76, 116→114). Screen readings (400 trials) sit much
  higher still.
- **Therefore**: a candidate is stage-worthy only after ≥3 fresh-seed rungs at
  ≥20,000 trials/side agree flat at the claimed reading. Even then the claim in
  any report is "upper_bound at the lightest reading", never "exact".
- `distance_rand_witness(...)` returns a namedtuple `(weight, side, support,
  rejected)`; `support` is the witness to embed. `if not res:` means nothing
  found.

## Construction primitives (committed kit code)

- `research/kit/group_algebra.py`: `metacyclic(q, q-1, r)` returns
  `(mul, labels)`; `r` = smallest primitive root mod q (2 for q=19, 3 for
  q=17). `build_2bga(mul, a, b)` builds HX, HZ for exponent sets a, b.
  These are Kasai affine 2BGA codes; n = 2*q*(q-1) (684 for q=19, 544 for
  q=17).
- `research/kit/bbga_labels.py` (local, untracked): `build_2bga_affine(q, a, b)`
  composes the above.
- Board prepass (do it before spending RIS): CSS check, connectivity, exact
  fingerprint (`verify/qldpc_verify.py::css_fingerprint` on dense H), then the
  gate's dedup catches the rest.

## Known traps

- q=19, n=684, k=10 draws repeat one WL signature (the board's 684-10-90
  class) — sampler trap, avoid that corner.
- Random BB trinomial/quadnomial pairs on 100<n<=240 are ~93% direct sums;
  that area is closed.
- Non-abelian BBGA and metacyclic 2BGA at n<=320: closed, no gate pass.
- Board moved 2026-11-06 (our own merges, now in codes/ on main): **[[684,12,108]]**, **[[544,18,76]]**, **[[684,8,110]]** (Kasai affine 2BGA, w=12). A new find must dominate these, not just the older board.

## What "good" looks like

- Anything passing the gate with `board_advancing: true` in the
  (unrestricted, weight-9plus) cell is worth staging, even a pure frontier
  extension that dominates nothing.
- kd^2/n = k*d^2/n is only a headline; the board is a Pareto frontier over
  (n smaller, k larger, d larger, w smaller).

## Deliverable (every search agent)

1. Stage survivors (gate-passed, multi-seed-confirmed) under this session's
   staging dir with the kit's save path.
2. Write `<campaign-dir>/REPORT.md`: draws screened, gate passes/failures with
   verdict paths, best readings with their seeds, dominated misses, and the
   exact candidate paths.
3. Your final message: a compact summary of the above (the supervisor only
   sees your text, not your files).
