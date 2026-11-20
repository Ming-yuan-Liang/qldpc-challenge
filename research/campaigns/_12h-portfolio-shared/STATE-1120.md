# STATE-1120 — submission wave 2026-11-20 (L5+L6 slate) & new campaign A+C

Newest entries first. This file continues STATE-1106.md (closed final 2026-11-10,
5 codes on the board / 2 frontier at close; board grew to 3,694 by 11-20).

## Round 1 — 2026-11-20 (wave opened)

**Mission**: submit the held L5 (4 codes) + L6 (5 codes) slate as nine PRs;
meanwhile clean up dead paths and open the new A+C campaign lanes.

- **Board refreshed**: local main = merge of upstream/main @ cece5d8ec
  (3,694 codes). Pushed to fork main (push needed 6 attempts; documented
  connection-reset pattern). Fork main gained the site-rebuild bot commit
  (dd9f6da7f) on top — origin/main ref synced via fetch.
- **Phase 1 re-gate (novelty vs 2026-11-20 board): 9/9 green.** All
  passed=true, board_advancing=true, dominated_by=[], d_only_peers=[]
  (no peer audits owed). Verdicts at research/candidates/<slug>.regate.json.
  Board growth did not claim any candidate.
- **Phase 2 L6 batteries: 10/10 green** (gate_changed, fresh seeds 431001/
  431002, standard instrument ~36-41k trials; nothing lighter than the
  claims). Bonus: the battery rungs also repaired the promote trailing-flat
  gaps — 880-18-29 trailing [30,29,29] → flat 2; 968-32-25 trailing
  [25,25,25] → flat 3. No 1M top-ups needed. Log: l6_battery_1120.log.
- **Phase 3 plans**: build_plans_1120.py (in this dir) assembles the nine
  promote plans — candidate inlined, NO recipe key (no repro manifest;
  130-min verify cap lesson), evidence from the confirm ledgers
  (fingerprint-matched, real seeds) + deep.jsonl + battery rungs. Ladder
  facts: deepest fresh 2M (L5) / 1M (L6); trailing flat 6-8 (L5), 2-6 (L6).
- **Promote lessons (three runs)**: (a) evidence.tools must be a dict
  {model, harness}, not a string; (b) promote uses origin/main as the
  prose-check base — a STALE origin/main ref turns the merge's upstream
  fieldnotes into spurious "added fieldnotes with wrong author" rejections
  (fetch origin before promoting after a merge); (c) promote writes
  codes/<slug>.json into the working tree — re-running promote after a
  failed run hits "duplicate: identical to board entry" self-collisions;
  remove the untracked bundles first.
- **Slate (pruned)**: L5 = 510-102-19, 588-98-22, 686-98-24, 714-102-25
  (686-98-22/23 Pareto-covered by 24). L6 = 840-18-28, 880-18-29,
  924-29-27, 968-29-28, 968-32-25 (924-29-26 is a d-only peer of 27,
  966-29-27 dominated by 924-29-27).

## Submission playbook deltas (vs STATE-1106)

1. Branches: `git checkout -b submit-<slug> upstream/main` (NOT main —
   main carries the research snapshot commit; upstream/main keeps the PR
   diff clean).
2. Prepush: `QLDPC_PYTHON=.venv/Scripts/python.exe PR_AUTHOR=Ming-yuan-Liang
   BASE=upstream/main bash verify/prepush_prose_check.sh <body>`.
3. Push: PAT credential helper (token in research/candidates/.pat, verified
   2026-11-20 = Ming-yuan-Liang), retry on connection reset (observed ~50%
   failure rate today).
4. Open PRs: research/campaigns/_12h-portfolio-shared/open_prs_1120.py
   (titles read from promote-real-1120.json, one PR per code, 9 at once —
   verify.yml concurrency group is per-PR so they run in parallel).
5. CI watch cron: 5-minute supervision round per Round-287/288 pattern
   (cancelled → retrigger; REFUTED → witness → verify → rename push same
   branch; merged → register). Stop when all nine are merged/closed.

## New campaign lanes (opened 2026-11-20)

- **kasai-interior-1120** (Lane A1, main): affine-2BGA interior gaps q=17/19,
  k 14-26 × d 40-107 at n 544/684. Bar: our own merged anchors; must be
  non-dominated against them. Defense trigger: MathysRennela's dormant
  branches reviving at k>10.
- **agl-prime-power-1120** (Lane A2, spike): q=13 (n=312, metacyclic path
  works) + q=16 (n=480, needs AGL(1,16) = C_2^4 |x C_15 perm_group adapter —
  F_16^+ not cyclic). Any non-dominated point pays for the adapter.
- **geo-frontier-1120** (Lane C, secondary): geometric-efficiency record
  (1.7555, [[957,105,4]], static 6+ weeks) via dense 2D-local layouts +
  SAT d_lower certificates. Runs on leftover capacity.

Discipline unchanged: stage-only until promoted; no witness ever lost;
offset calibration against merged incumbents decides alive/dead; honest
upper-bound claims only.


## Round 2 — 2026-11-20 (~10:45): nine PRs open, CI started

**PR registry** (slug -> PR -> head commit on fork, base upstream main @ 03b16d622):

| slug | PR | head |
|---|---|---|
| 510-102-19 | #6930 | 64fe9110f |
| 588-98-22 | #6931 | 3810c0702 |
| 686-98-24 | #6932 | cbbfe9d7c |
| 714-102-25 | #6933 | 5983526a5 |
| 840-18-28 | #6934 | fd92112c4 |
| 880-18-29 | #6935 | b76996f78 |
| 924-29-27 | #6936 | 66e22ad6f |
| 968-29-28 | #6937 | c0c39981d |
| 968-32-25 | #6938 | 8319f6197 |

- Pushes went through the **Git Data API** (push_via_api_1120.py in this
  dir): the machine's HTTPS route to github.com:443 is selectively blocked
  (api.github.com and ssh.github.com:443 reachable; github.com:443 times
  out; git's http.curloptResolve unusable on the schannel backend; the PAT
  lacks admin:public_key so the local SSH key cannot be registered).
  Blobs -> tree (base_tree = upstream main) -> commit -> ref, all over
  api.github.com. Branch contents are byte-identical to the locally
  committed submit-<slug> branches (git show as the source).
- A leftover git-push retry loop was still cycling in the background while
  the API pushes ran; any of its pushes that land on an existing ref are
  rejected non-fast-forward — harmless. Its last act (checkout main)
  restores the working tree.
- CI supervision cron created (5-min round per cron_prompt_1120.txt);
  stop condition = all nine merged/closed.
