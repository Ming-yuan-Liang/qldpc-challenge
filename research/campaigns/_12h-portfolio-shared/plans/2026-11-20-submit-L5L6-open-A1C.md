# 方案：交 L5/L6 → 清理 → 新战役 A+C 双线

## 背景

上一波战役 2026-11-10 关闭，当前榜上 5 码 / 2 前沿（684-14-107 eff 234.3、544-20-76 eff 212.4），无竞争对手能支配这两个点（k≥14@d≥107 与 k≥20@d≥76 角落独占）。板面 10 天涨了 ~550 码（主要是 MathysRennela 的 code-calculus 小码灌水 + GB n=301-465 扫描 + 大规模降读数）。押着 13 个过了门禁的候选未交。用户指令：全部执行——①交 L5+L6，②清理，③新战役 A+C 双线（已确认）；研究快照全量推 fork（已确认）。唯一约束：快、高效。

**剪枝决定**（内部支配关系）：L5 只交 4 码 —— 510-102-19、588-98-22、686-98-24、714-102-25（686-98-22/23 被 24 支配，且后交会触发 peer_audit）；L6 只交 5 码 —— 840-18-28、880-18-29、924-29-27、968-29-28、968-32-25（924-29-26 是 d-only、966-29-27 被 924-29-27 支配）。

## Phase 0 — 板面刷新（一切的地基）

1. `git fetch upstream`（本地已有 cece5d8e）。
2. 提交本地未收尾内容：STATE-1106.md 修改 + `research/campaigns/w8-2dlocal-n700-1000/`（REPORT 留到 Phase 6 写完再一并提交）；`.pyd` 留 untracked（`make fast` 可重建）。commit 信息不加 Co-Authored-By（AGENTS.md 规则）。
3. `git merge upstream/main`（本地仅多 research/ 提交，预期干净合并）。
4. `git push fork main`（用户已确认全量推）。

## Phase 1 — 对 2026-11-20 新板重新过 novelty 门

9 个候选逐个 `uv run --no-sync python verify/validate_candidate.py research/candidates/<lane>/<slug>.json`（boardcache 按条目哈希自动刷新，无需清缓存）。检查 `board_advancing / dominated_by / d_only_peers`。已知风险：510-102-19 距被 512-128-19 支配仅差 2 个量子比特；L6 是纯前沿延展点，新板可能已占位。被支配者从名单剔除并记入 STATE。

## Phase 2 — L6 新种子电池（L5 已 12/12 通过）

5 码 × 2 新种子，`verify/gate_changed.py <cand> --seed S` 并行 5 进程（每个 ≤600s，约 20 分钟总耗时）。被反驳且诚实读数仍 advancing → `repackage_at_reading.py` 改包后保留；否则剔除。

## Phase 3 — Promote 打包 9 码

- 以 `research/candidates/l2-q17-resume/build_plan_544_20_80.py` 为模板写 9 个 plan JSON：**candidate 内联、不带 recipe 键**（避免生成 repro manifest，守住 CI 130 分钟上限——上一波的核心教训）；evidence 从 L5 `confirm_pp*.json` 台账 + battery 日志、L6 `workspace/deep.jsonl` + 新电池组装；`--authors @Ming-yuan-Liang`。
- 先 `uv run --no-sync python research/kit/promote.py <plans...> --dry-run`（会强制最深新鲜 rung ≥1M trials、尾部 ≥2 个平齐 rung；L6 读数 28-29 类抖动按诚实纪律取低值申报）。
- 正式跑 + `--json bundles.json --script open-prs.sh`，产出 codes/ + notes/ + pr-body + git 命令。

## Phase 4 — 开 9 个 PR

每码：`submit-<slug>` 分支（基于 upstream/main）只含该码的 codes/+notes/ → commit → `QLDPC_PYTHON=.venv/Scripts/python.exe PR_AUTHOR=Ming-yuan-Liang BASE=upstream/main bash verify/prepush_prose_check.sh <body>`（必须 exit 0）→ PAT credential helper 推 fork（SSL 重试）→ 复制 `fork_and_prs_1105.py` 的 prs-only 模式开 PR（head `Ming-yuan-Liang:submit-<slug>`）。**9 个全部一次开**——verify.yml 并发组按 PR 号隔离，可并行。开工前先验证 `.pat` 仍有效（脚本自带身份断言），失效则立即向用户要新 token（阻塞项）。

## Phase 5 — CI 监督 cron（条件式，复用上波验证过的机制）

CronCreate 每 5 分钟：轮询 9 个 PR 的 check-runs；cancelled → commit-tree 空提交重触发；REFUTED → 下载日志提 witness → `verify_ci_witness.py` 独立验证 → 按诚实读数改名重推同分支 + PATCH body；merged → 登记。**停止条件：9 个全部 merged/closed 后 CronPauseSelf**。每轮更新 STATE（新开 STATE-1120.md 或续写）。

## Phase 6 — 清理（与 CI 等待并行）

1. 修死路径：父目录 `battery_harvest_runner.py`、`update_cron.py` 的 ROOT → `Documents\QEC\qldpc\qldpc-challenge`；`AGENT-BRIEFING.md`（repo + workspace 两份）的 `C:\Users\liang\Desktop\...` → 现路径。
2. 删死物：父目录 `corr-4678/`、`submit-544-20-85/`（.git 指向已消失的 Desktop 主库）、空 `retrigger-4678/`、空 `runlogs_42673457220.zip`。
3. 补 REPORT：q17/q18 两 lane 的占位符章节按 STATE 记录收尾（角落死于偏移校准）；新写 `w8-2dlocal-n700-1000/REPORT.md`（从 deep.jsonl + 暂存判决 + 电池结果）。
4. 归档父目录散件（pr.json、cr.json、job_*.log、verify4678.log、prom*/fmt*/prepush*.txt、tmpidx*、merge*.txt、reproduce_5079.log、prose_fail.log、684-14-107.* 等）→ `_archive-2026-11/`（保留不删，CI 证据链）。
5. workspace-private 同步：拷贝活 STATE + 完成的 REPORT。
6. 最终快照 commit（含 L6 REPORT + STATE 收尾）推 fork main。

## Phase 7 — 新战役 A+C（PR 推出后即启动，与 CI 等待并行）

**Lane A（主攻，Kasai 2BGA 护城河）**：
- A1 内部空白扫：q=17/19（n=544/684）目标 k∈[14,26] × d∈[60,107] 内部点位——684 带 k=16-20@d≥90 是 eff 金矿（如 684-20-100 → eff≈292）。
- A2 可行性尖刺：q=13（n=312）/ q=16（n=480，素数幂）——先验证 `kasai_affine_sweep.py`/metacyclic 生成器是否支持素数幂；这两条 n 带无人开采。
- 工具与纪律：`kasai_affine_sweep.py` + `lane_runner.py`、gf2_fast 加速（先确认 .pyd 可加载）、400-trial 粗筛 → 深读阶梯 → 1M 分块、对自家已合并在位码做偏移校准（上波最大返工源的解药）。
- 防御盯梢：MathysRennela 休眠分支（684-8-116-2、544-10-86、544-8-88）——一旦以 k>10 复活，立即优先该角落。
- 资源：机器 python 进程 ≤16、断点续跑（progress_*.jsonl）、10 分钟资源巡检 cron（进程消失即同命令重启，done-set 幂等）。

**Lane C（副攻，geo 赛道）**：
- 目标：破 1.7555（957-105-4，w4/d4 精确认证，6 周未动）。
- 工具：`local_sat.py`/`sat_rungs.py`（cadical195）+ L6 boundary_engine 经验；搜 n 700-1000 / w≤8 / d≤40 档的稠密孔洞布局；记录级申报需 `sat_certify.py` ladder 模式出 d_lower + 验证器接受的布局。
- 优先级低于 A，跑在巡检 cron 的算力余量上。

**提交纪律**：新发现沿用 stage-only + 门禁 + 多种子电池 + 授权后 promote（本方案即为持续授权模式，新码走同一条 Phase 3-5 流水线）。

## 验证清单

- promote dry-run 9/9 绿；prepush 9/9 exit 0；9 PR 全开且 verify+prose 绿、被上游 bot 合并；站点贡献者数据 codes 从 5 涨到 ≤14。
- 清理后：活动脚本无 Desktop/liang 残留路径；`git status` 干净（除有意 untracked 的 .pyd）；workspace-private 与活副本一致。
- 新战役：A/C 各有 campaign 目录 + campaign.json + 台账，gate-green 候选进 candidates/，每波 REPORT 收尾。

## 风险与对策

- CI 反驳（L6 仪表读数 +1..+9 偏高）：电池预飞 + 脚本化改名重推闭环。
- 新板占位（512-128-19 等 CPM 新码）：Phase 1 重门禁裁决，被支配即弃。
- `.pat` 失效：Phase 4 开头即测，阻塞时向用户要新 token。
- promote 证据约束拒收 L6 抖动读数：取低值申报（诚实读数纪律）。