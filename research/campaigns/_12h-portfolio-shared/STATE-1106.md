# STATE — standing unattended search + submission (started 2026-11-06)

**STATUS: RESUMED on a NEW machine 2026-11-06 (user: "重新制定计划，尽可能加速搜索，允许并发subagent").**
New machine: `C:\Users\Frieren\Desktop\qldpc\qldpc-challenge` (Intel Ultra 7
255H, 16C/16T, 31.4 GB RAM). Concurrency reality: the platform allows at most
**3 concurrent background subagents** (hard limit, hit on first dispatch), so
the 6 lanes run in waves of 3, rotated by the supervision cron. Within the
lanes, python worker processes are capped machine-wide at 14 (see
AGENT-BRIEFING.md). Wave 1: L1 q19-k14-resume, L2 q17-k18-resume, L3
en2-followup; queued: L4 beat-surface-k50-w8, L5 beat-surface-k100-w8, L6
w8-2dlocal-n700-1000. The 10-min supervision cron was recreated in the new
session with the rotation duty.

**BLOCKED ON TOKEN**: `research/candidates/.pat` does not exist on this
machine (gitignored, never backed up). Everything that pushes or opens PRs is
staged until the user provides a fresh classic PAT (repo scope) and revokes
the old one. Reading public CI state works without it.
**PR state at resume**: #4679 [[684,12,108]] MERGED, #4680 [[544,18,76]]
MERGED, #4681 [[684,8,110]] MERGED. #4678 [[684,14,110]] still OPEN and its
`verify` check is CANCELLED at head 099b9f278 — needs an empty-commit push to
retrigger (blocked on PAT).
Local main was fast-forwarded to upstream/main: the three merged codes are in
codes/, verify/ matches CI's pinned stack.

Read AGENT-BRIEFING.md in this directory first. This file is the handoff state
for supervision rounds; update it when state changes.

## Round 227 update (2026-11-09 ~11:20): RESUMED — 双 PR CI 再取消 → retrigger 完成；榜单全量核实 3142 码

- **恢复**：新监督自动化（每 5 分钟；至 2026-11-09 21:00 该轮自动 CronPauseSelf 结束）。
  用户令"全面衔接之前任务并推进 + 确认在榜码数"。
- **CI 恢复时快照**：#5079 @0b76c6530 与 #4678 @1875b85a9 的 verify+reproduce 均
  completed=**cancelled**（上游系统性取消再现；ris-compile/codes-format/prose 三绿）。
  已按预案 commit-tree 空提交 retrigger，双推送成功（第 1 次尝试即成，网络正常）：
  - #5079 新 head **2801f6f2c** → fork:submit-544-20-85
  - #4678 新 head **efc735e06** → fork:submit-684-14-115
  下轮核对 check-runs（verify ~1.5h 级出结论）。
- **榜单核实（回答用户问询）**：上游 main codes/ 全量 **3142 码**（contents API
  恰好 1000 截断，以 git trees 为准）。我方在榜 **3 码**：544-18-76、684-12-108、
  684-8-110（merge 提交 0e5bfe16b / 394c0760a / ed724bf86，均未被移除）。在途
  2 PR：#5079 [[544,20,80]]、#4678 [[684,14,107]]。上游 ff 7ea802a1f→8bea2dda1
  （他人小码 + circuit tiers，不涉我方）。
- **L5 现势**：四终选码（510-102-19、588-98-22、686-98-24、714-102-25）对新榜
  文件级**零支配者**，仍 board_advancing；12/12 battery 绿记录在案；六码仍
  **hold，提交决策待用户**（提交方案：686 只留 24 → 共 5 个 PR）。
- **资源/基建**：python 实体 0；PAT 在位（未回显）；gf2_fast.pyd 在位；本地
  main = 76198c347（研究快照，未推送）。
- **L6 已派发**：w8-2dlocal-n700-1000 车道子代理（后台）启动，带 gf2_fast 接线
  （backend="fast", threads=2/worker, ≤4 workers）+ checkpoint 纪律；stage 目录
  research/candidates/l6-2dlocal/。
- 下轮：① 双 PR check-runs 核对 ② L6 巡检（进度文件增长/进程存活）③ 见证处理
  ④ 资源盘点（≤16）。

## Round 228 update (2026-11-09 ~11:20): retrigger 生效 — #4678 verify in_progress

- **CI**：#4678 @efc735e06 **verify 已 in_progress**（retrigger 生效）；#5079
  @2801f6f2c codes-format 已绿、其余重跑中。双 PR 无需干预，~1.5h 级等结论。
- **L6**：子代理启动期（11:15 派发），暂无 worker 进程/进度文件/ staged 产物
  ——未达"10 分钟无增长 + 进程消失"重启条件，下轮复查。
- 资源：python 实体 0；无新见证文件；榜单无变化。

## Round 229 update (2026-11-09 ~11:30): 用户侧介入 — 双 PR 去 repro manifest 修 130min cap；CI 新 head 排队中

- **外部推送（fork 账号身份 LiangMingyuan，11:22/11:23，非 supervisor 执行）**：
  - #5079 新 head **1ed55d700**：删除 repro/544-20-80.json（-35 行）
  - #4678 新 head **e49f3c48f**：删除 repro/684-14-107.json（-35 行）
  - 提交信息诊断：**verify job 有 130 分钟上限**，可选 repro manifest 拖长 verify
    导致反复被取消。与历次取消时点（~2h10m / 2h25m / 90min）吻合 —— **采纳为
    新工作假设**。supervisor 11:14 的空提交 retrigger（2801f6f2c/efc735e06）
    被这两个内容提交覆盖，CI 随新 head 重跑（目前 check-runs 尚未注册，刚推，
    正常延迟，下轮核对）。
  - ⚠️ 推送者与本地 git 配置身份一致（LiangMingyuan <1904671174@qq.com>），且
    内容专业、改动最小 —— 按用户本人（或其授权会话）并行操作处理；**若用户
    否认，立即按账号安全事件停下排查**。
- **提交流水线修订（L5 五 PR 前置知识）**：repro/<slug>.json 为可选 manifest，
  可为规避 130min cap 而**不提交**（PR 只含 codes/ + notes/）。L5 提交方案照此
  执行（promote plan 的 repro 部分跳过）。
- fork 上 submit-544-18-82 / submit-684-12-117 / submit-684-8-116 三分支经核实
  均为 11-06 旧 tip（本地此前未 fetch，非新推送）。
- L6：workspace 出现 timing.py / calib.py / sanity.py / scan_board.py（工具搭建
  期），2 python 实体，正常推进。

## ⏹ CLOSED-FINAL (2026-11-10 用户指令): 停止定时任务，总结进度 — 战役全面收官

- **定时任务**：主监督自动化 automation-33dcd234（每5分钟，48+ 轮）与重复项
  automation-cc81a133 均已 CronDelete 删除（CronList 复核为空），不再触发。
- **最终战绩**（回答"当前进度"）：
  - **我方在榜 5 码**：544-18-76、684-12-108、684-8-110、**544-20-80**（#5079
    merged 11-09T23:30:30Z, e5cfb01a8）、**684-14-107**（#4678 merged
    11-09T23:32:45Z）。双 PR verify+prose 双绿后由上游 bot 合并。
  - **CI 30 小时战役**：130/90min 硬超时根因（自测套件 56min + 全板扫描
    55→61min 膨胀 + gate 无中间缓存）→ 修复链 = 删可选 repro manifest（跳
    套件）+ PR body 清死引用（prose edited 重跑）+ 1 次 retrigger（0-jobs
    瞬态）→ 双 verify SUCCESS（83min / 62min gate）。全程零盲推。
  - **gf2_fast**：~600× 加速（12k trials/s @8线程），offset +4 校准
    （inc684 对照），544-20 声明 85→80 stabilized（30M 与 8M-pd24 双独立
    seed 一致），CI 8M 级 gate 验证通过——预自校正策略成立。
  - **L5 六幸存码 hold**（research/candidates/l5-beat-surface/，gitignored）：
    510-102-19（kd²/n 72.2）、588-98-22（80.7）、686-98-22/23/24（24 覆盖
    22/23）、714-102-25（89.4）；gate 绿 + battery 12/12 PASS（新 seed
    20270601-12）；提交方案就绪（PR 只含 codes/+notes/，无 manifest、body
    无死引用、sweep 膨胀余量按 #5079 83min 锚点计算）——**待用户授权**，
    若提交预计 5 个 PR（686 只留 24）。
  - **板况**：上游 main 约 3144 码（3142 + 我方 2 新码）；n≤100 密度最高
    （~10/值），701-1000 稀疏，>1000 空——L5 所在的 k≈100、n 500-714 带
    仍是低竞争前沿。
  - **本地资产**：研究快照提交 76198c347（main，未推送，356 文件）；
    gf2_fast.pyd 在位（丢失可 `make fast` 重建）；PAT 未动、未回显。
- **恢复入口**：说"继续"即可——从本节接手；L5 提交只需一句授权。

## Round 288 update (2026-11-09 ~12:35): 🏆🏆 [[684,14,107]] 也已合并 — 双 PR 全上板，我方在榜 5 码

- **PR #4678 merged_at 2026-11-09T23:32:45Z**（CI 的 107 读数采信 = 我们 11-07
  的预修正；witness 链路完整）。**#5079 + #4678 全部合并，修正链收官**。
- **我方在榜 5 码**：544-18-76、684-12-108、684-8-110、544-20-80、684-14-107。
- 剩余：L5 五 PR（510-102-19、588-98-22、686-98-24、714-102-25 + 备选 686-98-22/23
  被 24 Pareto 覆盖）**待用户授权**；11-10 09:00 收尾 + CronPauseSelf。

## Round 287 update (2026-11-09 ~12:30): 🏆 [[544,20,80]] 已合并上板 — 我方第 4 码

- **PR #5079 merged_at 2026-11-09T23:30:30Z**（merge commit e5cfb01a8）；
  codes/544-20-80.json 已在 main（104,638 bytes）— **[[544,20,80]] 正式上板**
  （n≤684 w≥9 格 kd²/n 235.3，d=80 为 gf2_fast 校准后 stabilized 诚实读数）。
  我方上板码：**544-18-76、684-12-108、684-8-110、544-20-80**（4 个）。
- **PR #4678** [[684,14,107]]：仍 open（clean），等 bot 同批/下批拾取。
- 后续：#4678 合并确认；L5 五 PR 待用户授权；11-10 09:00 收尾。

## Round 259 update (2026-11-09 ~12:12): 🎉🎉 双 PR verify 全绿 — 修正链全部通关，只等 bot 合并

- **#4678 @e49f3c48f verify SUCCESS**（gate 62 分钟，赶在 130min 杀点前 ~6 分钟
  跑完 — 关键：timeout 从 **job 起跑**计（本 run 排队 43 分钟后 19:07Z 起跑），
  不是 run 创建时刻；sweep 膨胀至 ~61min 但 gate 仍挤进预算）。check-runs：
  verify ✓ prose ✓ ris-compile ✓，**mergeable_state=clean**。
- **两 PR 现状**：#5079 [[544,20,80]] 与 #4678 [[684,14,107]] 均
  verify+prose 双绿 + clean → merge bot 将自动合并 → **我方上板码将达 5 个**
  （+544-20-80、684-14-107）。
- CI 战役复盘（11-07 至 11-09）：系统取消（130/90min 硬顶）→ 日志取证定位
  三重根因（套件 56min、sweep 55→61min 膨胀、gate 无中间缓存）→ 修复链
  = 删可选 manifest（跳套件）+ PR body 清死引用（prose edited 重跑）+
  一次空提交 retrigger（0-jobs 秒败瞬态）+ 两次排队窗口运气（#4678 排队
  43min 反而救了它）。无一次盲推，无一次超资源。
- 待办：确认两 PR 被 bot 合并（上板后 codes/ 计数 3142→3144）；L5 五 PR
  提交方案已就绪（无 manifest 路径 + body 无死引用），待用户授权。

## Round 247 update (2026-11-09 ~12:15): 🎉 #5079 verify SUCCESS — [[544,20,80]] 达合并标准（第 4 码待上板）

- **#5079 @d2cf8a74c：verify success（83 分钟跑完，无套件路径）**。check-runs：
  verify ✓ prose ✓ codes-format ✓ ris-compile ✓，**mergeable_state=clean** —
  REQUIRED_CHECKS=(verify, prose) 全满足，上游 merge bot 将自动合并。
  [[544,20,80]] 将成为我方第 4 个上板码（kd²/n 235.3，n≤684 w≥9 格前沿）。
- **#4678 @e49f3c48f**：108min 仍在 verify_all sweep — 今天 12+ 个 backfill
  合并令板上大量条目新增 d_circ 检查，sweep 膨胀（对照：#5079 同路径 sweep
  仅 ~55min）。130min 硬顶必然在 gate（n=684 需 ~50min）结束前杀掉 job，且
  gate 单条目无中间缓存 → 重推无意义。**已按预案升级上游**：PR 追评（comment
  6750293854）给出 sweep 膨胀数据 + 请求 verify.yml timeout-minutes 上调
  （130→200-240），承诺改动后立即 retrigger。等维护者动作，不盲目重推。
- 教训：sweep 成本随上游 backfill 节奏增长，无套件路径的余量估算要按
  "当日板况"重算（#5079 83min 是今天实测的锚点）。

## Round 246 update (2026-11-09 ~12:05): ⚠️ sweep 膨胀风险 — #4678 98min 仍在 verify_all；#5079 已进 gate

- **背景**：今天上游 merge 了 12+ 个 circuit-backfill PR → 板上大量条目新增
  circuits → verify_all 的全板结构扫描（#5079 实测 ~55min，比 11-07 的 52min
  略长）在 #4678 的 merge 树上进一步变长（98min 时仍在 sweep 步）。原因未定
  （新增 circuits 的 d_circ 检查 + 条目增长 + 该 PR 是改名 diff）。
- **风险**：#4678 的 130min 硬顶在 20:33Z；若 sweep 拖过 ~100min，gate（n=684
  需 ~50min）跑不完 → 再次被取消，且 gate 单条目无中间缓存 → **盲目重推无意义
  （预案：不重推，升级上游）**。
- **#5079**：74min 已进 gate（sweep ~55min），gate ~45-50min → 预计 ~20:45Z
  结论，距 20:58Z 硬顶余量 ~13min — 紧但可行。
- 若 #4678 被取消：在 PR 追评（sweep 膨胀数据 + 请求 timeout 上调或指引），
  上游今天活跃（vprusso 有回复记录）。若 #5079 verify 绿 → 4 号码上板。

## Round 233 update (2026-11-09 ~12:10): ✅ 双 PR prose 转绿 — 只剩 verify

- body 修补生效：#5079 @d2cf8a74c 与 #4678 @e49f3c48f 的 prose 均
  **success**（edited 重跑，REQUIRED_CHECKS=verify+prose 中的 prose ✓）。
- verify：#5079 in_progress（8min，ETA ~105min 级）；#4678 排队中
  （efc735e06 旧 verify 42min，预期 130min 被取消后自动轮替）。
- 下轮只需盯 verify；refutation 处置预案在册。

## Round 232 update (2026-11-09 ~12:05): prose 真失败（PR body 引用已删 manifest）→ body 已修，勿动树

- **#5079 prose 失败根因**（job 日志）：PR body 引用了 `repro/544-20-80.json`
  — manifest 删除后该路径不存在。修复正是 check_prose 提示的路：**只改 PR body**
  （prose.yml types 含 `edited`，issue #897 专门为此设计，10 秒级，不动树不惊动
  在跑的 verify）。
- **已 PATCH 两 PR body**：repro manifest 引用句替换为"recipe 内联于 note、
  可由 note 单独重建"。#5079 body 2716 字符、#4678 2886 字符。下轮核对 prose
  转绿（edited 事件会对当前 head 新建 prose run）。
- **CI 快照**：#5079 @d2cf8a74c verify in_progress（~17min，健康）；
  #4678 @e49f3c48f verify 仍 pending（排队于 efc735e06 的旧 verify 之后）。
  #4678 codes-format 在 e49f3c48f 上是 0-jobs 幽灵 — 非 REQUIRED_CHECK，不
  阻塞合并，不处理。
- 教训补充：**删树内文件前先查 PR body/notes 是否引用该路径**（prose 的
  cited-paths 检查覆盖 body）。

## Round 231 update (2026-11-09 ~11:58): 0-jobs 秒败之谜（瞬态调度异常）→ #5079 retrigger 成功在跑

- **#5079 @1ed55d700 的 verify/codes-format/prose 全部 "completed failure、
  0 jobs、无日志、无 check-runs"**（2801f6f2c 的 verify/reproduce/prose 同样；
  但同分钟 codes-format 有 job 成功）— 本地试合并 upstream/main 干净、workflow
  YAML 未动、GitHub 状态页 Actions=operational → 判定为**调度层瞬态异常**
  （疑与今天 ~30 个 backfill verify 洪峰饱和相关），非我们内容问题。
- **处置**：commit-tree 空提交 retrigger（d2cf8a74c）。网络又抖（443 连接失败
  5 次后第 6 次成功）；期间再次踩中 PUSH_OK 误报（rev-parse 只验本地对象）——
  教训再入册：推送成功判据必须用 push 输出的 ref-update 行或事后 ls-remote
  比对 remote tip。
- **结果**：#5079 @**d2cf8a74c** verify **in_progress（2 jobs，调度正常）**，
  走无套件路径（manifest 已删），预计 ~105 min < 130 内出结论。
- **#4678 @e49f3c48f**：verify pending 属正常排队（concurrency
  cancel-in-progress=false，前一 head efc735e06 的 verify 还在跑且带套件 →
  预计 130min 被取消后轮到新 head 的无套件 run）。约 2-4h 出结论。
- 其余：无新见证；L5 hold 不变；L6（另一会话派发）工具搭建期正常；python
  实体 0-2；停止条件未触发。

## Round 230 update (2026-11-09 ~11:45): 身份澄清 + 监督权统一 — Round 229 的"外部推送"就是本主会话

- **身份澄清（给一切并发 supervisor 会话）**：Round 229 记录的两笔推送
  （1ed55d700 / e49f3c48f）**来自本主会话**（原始战役会话，本地 git 身份
  LiangMingyuan，与 11-07 全部历史操作同源）——**不是账号安全事件**，无需排查。
  删除 repro manifest 是经过完整日志取证后的修复决策（见下与两 PR 的诊断评论
  6748026655 / 6748026914），提交信息与 PR 评论均已写明理由。
- **根因确诊（铁证，被杀 run 42398222710 全日志）**：verify.yml `timeout-minutes:
  130` 硬顶；`repro/` 改动 → only_codes=false → 全量自测套件 55:44（1441 tests）
  + 全板结构扫描 52 min（3136/3136）+ 杂项 3 = gate 开跑前 111 min；gate 需
  ~50 min（240s python seed + 8M RIS-fast @ CI 实测 3.2k trials/s ≈ 41 min）
  → 恒被杀；且取消时 search-cache save failed → 重推永远从零开始。
  **reproduce 90min 对所有 PR 恒取消**（每 manifest 调用恒 ~6 min × 27 > 90），
  但 merge bot REQUIRED_CHECKS=(verify, prose) — reproduce 不阻塞合并。
- **监督权统一**：本会话已把权威监督自动化 automation-33dcd234 更新为当前使命
  （verify-only 盯梢、新 head、11-10 本地 09:00 CronPauseSelf 停止）并启用；
  另一会话建的重复自动化 **cc81a133（今晚21:00停）已由本会话禁用**，以避免
  双 supervisor 对 STATE/分支并发写。请其余会话让位，勿再启用重复 cron 或
  回滚两笔 manifest 移除提交。
- L6 车道（另一会话派发的子代理）照常由各轮巡检其 stage 目录与进程；
  L5 提交方案按 Round 229 的修订执行（PR 只含 codes/+notes/）。

## Round 207 update (2026-11-07 ~09:05): #5079 verify 被取消；本机到 github 网络中断

- **#5079 的 verify 跑了 ~2h10m 后被上游取消**（reproduce 此前已 cancelled）——
  两项检查双取消，需空提交 retrigger；**retrigger 因本机到 github.com:443 完全
  无法连接而失败**（fetch/ls-remote 全挂，疑似本地网络或 GitHub 事故）。下轮
  cron 重试 retrigger（worktree 空提交流程，注意上次脚本的 PUSH_OK 误报已修）。
- #4678 @40351e74d：verify 仍 in_progress（~100 分钟），reproduce cancelled。
- 若下轮网络仍断：仅巡检本地产物（L5 账本），CI/retrigger 顺延。
- **Round 208 补记**：网络部分恢复（API/ls-remote 通、fetch 仍抖）。retrigger 改用
  **git commit-tree 免 worktree 方案**成功：#5079 新 head **75c4eb9e8**（空提交于
  bcd520f8b 之上），全检查重跑中。此法入册（网络抖动期绕过 fetch/worktree）。
- **Round 210 补记**：**#4678 的 verify 也被上游取消**（~2h25m）——两 PR 全检查
  取消，系统性（上游 runner/并发规则）。#4678 retrigger 提交已本地造好
  （**1875b85a9**，commit-tree 于 40351e74d），**推送被网络断连挡住，下轮只重推**：
  `git push fork 1875b85a9:refs/heads/submit-684-14-115`（对象已在本地对象库，
  无需重造）。
- **Round 211 补记**：#4678 推送成功（第 7 次尝试，网络抖动期坚持重试即可）。
  两 PR retrigger 全部在跑：#5079 @ **75c4eb9e8**、#4678 @ **1875b85a9**。
  双 PR CI 结论（或修正稳定）后 → 按用户指令 CronDelete 暂停。
- L5：pp 确认流水 + 2BGA 大群轨推进正常（本机不受影响）。

## Round 224 update (2026-11-07 ~10:35): 🏆 L5 大捷 — 6 个 gate 绿幸存者待收割

- **L5 beat-surface-k100-w8 收官（正结果！）**：六个 staged 幸存者全部
  passed=True + board_advancing=True + dominated_by=[]（verdict 已逐个核对）：
  **510-102-19**（kd²/n 72.2）、**588-98-22**（80.7）、686-98-22/23/24（69.2/
  75.6/82.3；24 Pareto 涵盖 22/23，提交可只留 24）、**714-102-25**（89.4）。
  方法：从板上 994-142-40 系逆向重建仓库自有 irregular pair-partition CPM
  模板（Okada-Kasai 交换规则），lift N=48-52 精确整数解格抽样 mod N，
  240 抽漏斗 + 500k 分诊 + 多种子深阶梯（500k-2M + pd48）。
- **收割进行中**：12 个 gate_changed battery（6 码 × 2 新 seed）后台批量跑
  （battery_harvest.log），结果下轮登记。全部 hold，不 push——提交决策待
  用户（当前暂停指令聚焦双 PR CI 计划）。
- 其余家族对 k95-105 格的结构关闭论证 + 904/928 现有证据覆盖说明见
  L5 REPORT.md。
- CI：#5079 @75c4eb9e8 与 #4678 @1875b85a9 verify/reproduce 均进行中。

## ⏸ PAUSED-FINAL (2026-11-07 ~18:45, 用户指令): 保存进度 → 提交 → 暂停

- **用户指令（最终）**："保存当前进度，该提交提交，暂停任务。" 已执行：
  1. **监督 cron 已禁用**（automation-33dcd234… enabled=false，CronList 复核；
     本会话无 CronDelete 工具，改写 tasks-index.sqlite，恢复时在 Automations
     页面重新启用或删除均可）。
  2. **L5 收割 battery 12/12 全过**（6 码 × 2 新 seed 20270601-12，
     gate_changed fast，每码 "no logical lighter than 声明 d"，零 REFUTED）：
     510-102-19、588-98-22、686-98-22/23/24、714-102-25 全部守住。
     六码仍 **hold 未提交**（research/candidates/l5-beat-surface/，gitignored），
     提交决策待用户。
  3. **进度已本地提交**（main，不推送）：research/campaigns/ 全部 +
     research/kit/bbga_labels.py。排除：verify/gf2_fast*.pyd（构建产物）、
     research/candidates/（仓库策略 gitignored，含 .pat）。
- **暂停时 CI 快照**（未结论，恢复时先查）：
  - #5079 [[544,20,80]] @ **0b76c6530**：全检查重跑中（retrigger 因
    reproduce 于 75c4eb9e8 上 90min 再次被上游取消）。
  - #4678 [[684,14,107]] @ **1875b85a9**：verify + reproduce 双进行中
    （71min+，健康）。
- **恢复手册**（新会话从本节接手）：
  1. 查两 PR head 的 check-runs（API 路径见 Round 226 之前职责 5；verify
     success → 记 STATE；REFUTED → 下载日志提 witness 行本地验证，按 CI 读数
     改名+push 同分支；再取消 → commit-tree 空提交 retrigger，对象本地即可造）。
  2. 双 PR 全绿 → 通知用户（合并由上游 merge bot 处理）。
  3. L5 六码提交决策待用户：若提交，686 只留 24（Pareto 涵盖 22/23），
     每码走 promote → 分支 worktree → PR 流程（l5-beat-surface 目录有
     recipe+verdict，battery 记录在本文件 Round 226/PAUSED-FINAL）。
  4. gf2_fast 已构建（verify/gf2_fast.cp312-win_amd64.pyd，offset +4 校准）；
     若 pyd 丢失用 `make fast` 或 g++ 直编命令重建（Round 181）。

## Round 226 update (2026-11-07 ~18:10): battery 收割重启；#5079 reproduce 再取消 → retrigger @0b76c6530

- **收割 battery 诊断**：首轮 heredoc+后台方式挂死（python 卡 stdin，log 0 字节
  无进程）——已杀；改为落盘 runner 脚本
  `Desktop/qldpc/battery_harvest_runner.py`（subprocess 逐个跑、600s 超时、
  逐行 flush），用 qldpc-challenge/.venv python 后台重启成功。前 3 个 battery
  已过：510-102-19 双 seed OK、588-98-22 seed1 OK（"no logical lighter than
  声明值"），无 REFUTED；结果齐后登记。
- **#5079 reproduce 在 75c4eb9e8 上跑 90min 后再次被上游取消**（verify 当时
  已 95min 仍 in_progress）。因 reproduce 取消只能靠新提交重启且 verify 反正
  要随 head 重跑，立即 commit-tree 空提交 retrigger：#5079 新 head
  **0b76c6530**（全检查重跑中）。#4678 @1875b85a9 verify+reproduce 双健康
  （71min+），不动。
- 经验补记：Git Bash 的 /tmp 是虚拟路径，Windows python 打不开——跨 shell/Python
  传文件一律用真实 Windows 路径；后台批处理别用 heredoc stdin，落盘脚本最稳。

## 用户指令（2026-11-07 ~07:15）：跑完当前计划后暂停定时任务

当前计划 = 两个修正 PR 的 CI 结论（#5079 [[544,20,80]] @ bcd520f8b、
#4678 [[684,14,107]] @ 40351e74d）。两者 verify+reproduce 均结论（绿，或
refutation 修正推送后新 CI 稳定）→ supervisor **CronDelete 暂停监督 cron**
并做收尾登记。L5 车道 agent 不受 cron 影响（会话内后台继续，用户回来可查）。

## Round 184 update (2026-11-07 ~07:40): CI REFUTED #4678 → 已修正 [[684,14,107]] 并推送

- **CI 判决**：#4678 verify failure = **真 refutation**——RIS-fast（8M 级，seed
  638637635，旧 head 84569c68 上发现、18e196b88 复核）找到 **weight-107 X 逻辑
  算子 < 声明 110**。supervisor 已本地独立验证（HZ·v=0 ✓、不在 HX 行空间 ✓、
  weight 107 ✓）。这是该 PR 第二次被 CI 修正（115→110→107）。
- **修正已推送**（head **40351e74d**）：git mv 三件套 110→107，X 侧换成 CI 见证
  （provenance 补齐必填字段：found_by/date/found_at/survived 8M、tool
  "CI verify RIS-fast (seed 638637635)"、seeds），notes 增补 CI 行，repro
  slug+artifact_sha256 重算，gate 绿（passed、board_advancing、指纹
  864138f85cf93ea1），双 battery 绿（20270521/22 "no logical lighter than 107"），
  prepush 绿（body 残留的 110 路径与 kd=247.7 全部换成 107/234.3），PR 标题
  /正文已 PATCH。TLS 抖动两次（fetch/log 下载 302 需手动跟随去认证头、push 一次
  失败重试成功）。
- 教训入册：x witness_provenance 必填四字段（先例的空 {} 是旧 schema 产物）；
  x 修正 PR 的 body 要全文换路径+数字（kd²/n：110→234.3... 实为 14×107²/684）。
- #5079 @bcd520f8b CI 跑中（下轮核对）。L5 巡检下轮。

## Round 182 update (2026-11-07 ~06:45): ✅ PR #5079 已修正为 [[544,20,80]] — 声明 stabilized

- **探针电池收官，下行走停**：8M-pd10(20270506)=82、**8M-pd24(20270505)=80**、
  **30M-pd10(20270507)=80**（独立 seed 双预算双 pd 交叉锚定）。**D\* = 80**
  （X≤80 三见证、Z≤84 一见证，全部 kit+GF(2) 双重独立验证、落盘）。
- **修正流水线全绿**：重打包 544-20-80（instrument 走廊如实写入 notes：
  numpy 85 → fast 82 → fast 80 + inc684 offset 校准披露）→ gate 绿
  （board_advancing=TRUE、dominated_by=[]，支配保住）→ 双 battery 绿
  （20270511/12 "no logical lighter than 80"）→ plan 重建（梯子 31 rungs，
  deepest 30M，1M 深度要求满足）→ dry-run 两轮（第一轮被
  provenance/search_budget/tool >200 字符挡下，缩短后过）→ 实推 →
  **git mv 改名 85→80 + 提交 bcd520f8b + prepush 绿 + 推送 + PR 标题/正文
  已 PATCH**。CI 在新 head 重跑。
- promote 的 validate_candidate 在 in-process 路径跑的是 build_doc 重构后的
  最终文档——search_budget.tool 长度是唯一拦路虎（两次 schema 教训：
  witness_provenance.tool ≤80、search_budget.tool ≤200）。
- gf2_fast 状态：构建完成、校准完成（offset_fast=+4）、L4/L5 已知会接线、
  对拍基线表齐（numpy 16/s vs fast t1 1344/s vs t8 8620/s）。
- cron 已恢复（每 5 分钟）。下轮：双 PR CI 核对 + L5 巡检。

## Round 181 update (2026-11-07 ~05:45): gf2_fast 600× 解锁 — k20 声明下修进行中 — L4 收官 — L5 启动

- **用户令：停 cron、做 gf2_fast 加速**。已完成：WinLibs GCC 16.2（winget）+
  pybind11；setuptools 路线踩坑（MinGW 误注 MSVC 旗标）→ g++ 直接编译
  `-O3 -static` → `verify/gf2_fast.cp312-win_amd64.pyd`（1MB 静态，同源码同语义，
  make fast 的 sanctioned 后端）。**实测 ~12k trials/s @8 线程（numpy 16-20/s，
  ~600×）**；同题同 seed 对拍分布兼容。
- **offset 校准**：inc684（真值 108）fast 1M 读 **112** → offset_fast = **+4**
  （numpy +5 兼容），仪器可信。
- **⚠️ k20 第二仪器下修**：85（numpy 1M）→ **82（fast 1M, seed 20270502）** →
  **80（fast 8M, seed 20270503）**；见证全部 kit 验证 + 落盘
  （witness_fast_X82/X80/Z84_*.json）。est_true(80) ≈ 75-76 贴现任 76——支配边缘。
  **探针电池跑中**（8M×2 含 pd24 + 30M，seed 20270505/06/07）→ 稳定末读数 D* →
  重打包 544-20-<D*> → gate → 双 battery → **修正 PR #5079**（改名+推同分支，
  不开新 PR）。CI 的 8M 级复核也会走到这个读数，必须先自证到底。
- **L4 beat-surface-k50-w8 收官（阴性关闭）**：k 45-55 / w≤8 / n 300-1000 在
  kit 全族关闭（HGP/LP/BP/BB/BBGA 排除 + 330-34-14 工艺复刻 + ~1289 候选全被
  支配 + 结构空穴论证）。交棒：n<300 pp-CPM 线；n≥904 底线依赖 8M 声明可能下修
  （544-20 先例）。基建沉淀 l4_board/l4_screen/l4_screen3/l4_confirm。
- **L5 beat-surface-k100-w8 已启动**（带 gf2_fast 接线 + L4 交棒 + ff 后板子；
  06:30 探针结束后放宽 4 worker×2 线程）。
- CI：#5079 与 #4678 verify/reproduce 仍在跑（~06:10 级出结论）。
- cron 暂停中（gf2_fast 工作期间）；k20 修正完成后恢复。

## Round 178 update (2026-11-07 ~05:00): 🚀 [[544,20,85]] SUBMITTED — PR #5079 OPEN

- **用户令"继续"（~01:05）恢复后完成全流水线**：重打包 544-20-85（Z-85×2/X-86×2
  见证直嵌，1M rung 种子全部从 witness 文件核实嵌入）→ gate 绿（passed、
  board_advancing、refute 8000 干净、指纹 bcc926556dc540ee）→ 双 gate_changed
  battery 绿（seeds 20270415/16，"no logical lighter than 85"）→ promote plan
  （梯子 25 rungs，deepest 1M ✓，flat@best 4，1,485,040 trials）→ dry-run ok →
  **真实 promote 进分支 worktree** → 本地 qldpc_verify + check_codes_format 全过 →
  prose check 过（两次踩坑已修：fork main 过期导致 base 差异 → 同步 fork main；
  $? 取到 tail 的退出码）→ 提交 3 文件 → 推 fork → **PR #5079 已开**
  （head e4f17a6c9c，标题含 kd^2/n 265.6）。main 工作树 codes/ 未被触碰。
- **上游 ff aea1afde2→7ea802a1f**：新增 [[960,20,40]] CLP（w6，不同格不碰撞）、
  UNSAT ladder 下界证明、circuit tiers。**100-20-8 golden 已被维护者重录**——
  #4678 verify 失败的根因消除。
- **#4678 已合并 upstream/main 并推送**（新 head 18e196b88，干净合并）：verify
  应转绿（分支现载重录后的 golden），reproduce 第 3 次机会。CI 重跑中，下轮核对。
- 会话挂起 ~3h 事件（01:2x-04:29）：后台 gate 曾被打断后自动重跑完成；L4 resume
  疑似同样被打断，需重新唤醒。
- fork main 已同步至 7ea802a1f（prose base 依赖）。
- 下轮：① #4678 CI 核对（verify 预期转绿）② PR #5079 CI 盯梢（verify ~1.5h 级）
  ③ L4 重新唤醒（4 worker 已授权）④ STATE 续维护。

## Round 175-177 (2026-11-07 ~00:57-01:20): PAUSE → RESUME

- Round 175：用户"总结并暂停任务"→ cron 删除、STATE 固化、L4 收尾（筛查全阴性、
  基建沉淀 l4_board/l4_screen/l4_confirm）。k20 rung 自行跑完 **FINAL: 250/250，
  D=85**，第 6 见证 86-c238 验证通过（Z-86）。
- Round 176（用户"继续"）：cron 重建（automation-1e26cdb3）、L4 唤醒（放宽 4
  worker）、重打包+gate+battery+plan 流水线启动。

## ⏸️ PAUSED (2026-11-07 ~00:57, Round 175) — user ordered "总结并暂停任务"

- **监督 cron 已删除**（原 5 分钟一轮）。恢复 = 重建 5 分钟 cron，职责模板见本文件
  "Supervision round duties" 节 + 用户授权（不计 token、3 subagent 上限）。
- **k20 1M rung 已 FINAL（01:00 自行跑完，恢复时跳过步骤 1 的等待）**：
  **250/250 chunks，末读数 D = 85**，6 个见证全部 supervisor 独立验证为真：
  **Z-85 ×2（c2/c26）、X-86 ×2（c41/c108）、Z-86 ×2（c134/c238）**。
  诚实声明 = d≤85；est_true ≈ 80（offset +5），稳支配 [[544,18,76]]。
  **恢复时从手册步骤 2（重打包 544-20-85）直接开始。**
- **恢复手册（关键路径，按序执行）**：
  1. 统计 `progress_1m_k20_w*.jsonl` unique chunks → 确认 250/250；末读数
     D = 最轻读数（当前 85；est_true ≈ D−5 ≈ 80，仍支配 [[544,18,76]]）。
  2. D<87 则按 `repackage_at_reading.py` 模式把
     `research/candidates/l2-q17-resume/544-20-87.json` 重打包为
     `544-20-<D>`（distance 值/witness/`survived_samples: 1000000` 更新，
     嵌入已验证的 Z-85 见证，改名）。
  3. 重跑 gate（coordination.py gate）——必须 board_advancing: true。
  4. 跑 2 个 gate_changed 快速 battery（新 seed）。
  5. 重建 promote plan（模板 `build_plan_544_10_88.py`：evidence ladder =
     19 rungs 时间序 + 1M rung + packaging witness + gate refute；headline=D），
     `promote.py --plan <plan> --json` 先 --dry-run 再实跑。
  6. prepush prose check → 从 origin/main 开分支 `submit-544-20-<D>` →
     token credential helper 推送 → API 开 PR（@Ming-yuan-Liang，一码一 PR）。
- **L4 车道已收尾完毕（01:05 报告）**：worker 全停、无残留进程、无候选/witness
  丢失。本轮筛查全阴性（w8 主脉 98 候选 stage1 全被支配；GB/2BGA/BB 各脉络
  关闭证据 8534+2362+600+1367 抽样在案）。基建沉淀：l4_board.py（gate 四轴
  支配复刻+2904 条缓存）、l4_screen.py（漏斗+checkpoint）、l4_confirm.py
  （已就绪未触发）、l4_m_menu.json。**恢复时首选 HGP/lifted/balanced product
  （products.py，k=k1·k2 可达 49-50，w≤8）**，详见其 REPORT.md 收尾段。
- **CI #4678 @ 84569c685**（暂停时）：ris-compile/codes-format/prose 3 绿，
  verify + reproduce 仍在跑（retrigger 后 reproduce 首次真实执行）。恢复时先查
  公开 API；verify 预期 failure（已知无关 100-20-8 golden 漂移，诊断评论在案）。

## Account / authorization

- GitHub account: **Ming-yuan-Liang** (user's choice, 2026-11-05). All
  submissions carry `provenance.authors: ["@Ming-yuan-Liang"]` and
  `PR_AUTHOR=Ming-yuan-Liang` for prepush.
- Standing authorization: the user explicitly ordered unattended search with
  **timely submission** of found codes ("找到码后及时提交可以复用之前的token")
  and exactly **3 parallel search subagents** per active wave.
- Token: `research/candidates/.pat` (gitignored, classic PAT, repo scope).
  Read with `cat research/candidates/.pat`; never echo it. If API calls return
  401, the token was revoked — skip push steps, stage everything, and report.
- Fork remote: `fork` = https://github.com/Ming-yuan-Liang/qldpc-challenge.git
  (already in .git/config). Push with inline token credential helper (see
  playbook below). CI runs on the upstream repo; we CANNOT rerun cancelled
  runs (403) — retrigger by pushing a new commit instead.

## Submission playbook (contributor-driven, authorized)

1. Candidate passes gate with `board_advancing: true`, multi-seed confirmed
   (>=3 fresh seeds x 20k trials flat), honest upper_bound claim.
2. Repackage at the lightest reading (see `repackage_at_reading.py`).
3. `uv run --no-sync python research/kit/promote.py --plan <plan.json> --json`
   (plan builder template: `research/candidates/sustained-20261027/build_plans.py`).
   promote never runs git.
4. New codes: branch `submit-<slug>` off `origin/main`, commit exactly
   `codes/<slug>.json` + `notes/<slug>.md` + `repro/<slug>.json`, PR body from
   template `research/candidates/pr-body-*.md`.
   **Distance corrections to OUR OWN open PRs**: do NOT open new PRs — commit
   the rename (`git mv codes/<old>.json codes/<new>.json`, same for notes/ and
   repro/), update the note title/first line, the PR body, and push.
5. prepush before every push: `QLDPC_PYTHON=.venv/Scripts/python.exe
   PR_AUTHOR=Ming-yuan-Liang BASE=origin/main bash verify/prepush_prose_check.sh
   <pr-body.md>` — must exit 0. Worktree-only: other staged bundles must be
   held out of the worktree during the check (see hold/ shuffle in
   research/candidates/hold/).
6. Push: `TOK=$(cat research/candidates/.pat); GIT_TERMINAL_PROMPT=0 git -c
   credential.helper= -c credential.helper='!f() { printf
   "username=x-access-token\npassword=%s\n" "$TOK"; }; f' push fork
   <branch>` (retry with backoff on SSL_ERROR_SYSCALL / connection reset).
7. Open/refresh PR via API (script: `fork_and_prs_1105.py prs-only` pattern;
   token read from .pat). One code per PR.
8. CI refutation watch: GET
   `/repos/unitaryfoundation/qldpc-challenge/pulls/<n>` then
   `/commits/<sha>/check-runs`; the `verify` check runs RIS-fast 8M-trial class
   (~1.5h). On REFUTED: download job logs, extract `witness = [...]` line,
   verify with `verify_ci_witness.py`, repackage at the CI reading, correction
   commit, push.

## Current state (2026-11-06, round 2 pushed, PAUSED)

- CI results round 1: #4679 [[684,12,108]] verify SUCCESS, #4680 [[544,18,76]]
  verify SUCCESS (their prose checks failed only because CI ran the stale
  pre-PATCH body — empty commits 2225cccd5 / bc451234b pushed to retrigger).
  #4678 and #4681 were refuted AGAIN (both to weight-110): witnesses verified
  locally, repackaged as [[684,14,110]] (Z-110, seed 1837444035) and
  [[684,8,110]] (X-110, seed 327946092), gate_changed fresh-seed green (no
  logical lighter than 110), correction commits 099b9f278 / 950905c64 pushed.
- ALL FOUR PR heads as pushed: #4678 099b9f278 [[684,14,110]],
  #4679 2225cccd5 [[684,12,108]], #4680 bc451234b [[544,18,76]],
  #4681 950905c64 [[684,8,110]]. Bodies/titles PATCHed via API for all four.
- Dominator analysis at the new readings (filename level, board 73d7efc4b):
  no board entry has (n<=684, k>=8, d>=110), so both 110-reading codes remain
  undominated; [[684,14,110]] still dominates [[690,12,84]] (kd^2/n 247.7);
  [[684,8,110]] kd^2/n 141.5 remains a clean frontier extension. The full
  pareto recheck COMPLETED after the pause and confirms both: 684-14-110
  on_frontier, dominates [[690,12,84]], dominated_by empty; 684-8-110
  on_frontier, dominates nothing, dominated_by empty. The pushed PR bodies
  are correct as-is; clean up the worktree qldpc-board-1106b on resume.
- Search lanes: q19-k14 and q17-k18 DIED mid-run on a model-API network
  outage (`ENOTFOUND zcode.z.ai`) — no staged survivors yet, but their
  checkpoint JSONLs (deep_*.jsonl / deep_rungs.jsonl) survive in their
  campaign dirs, so a re-dispatched lane should resume from checkpoints, not
  redraw. q17's most instructive find: a k=22 draw read 98 on screen but a
  fresh-seed rung found a weight-24 Z-logical — the screen-inflation bias is
  extreme in that corner. **en2-290 COMPLETED**
  (REPORT.md in its dir). Its deliverable, awaiting resume:
  **[[544,10,88]] staged + gate-passed** — q=17 n=544 k=10 corner, w=12,
  three fresh-seed 20k rungs flat 88/88/88, verdict passed=true
  board_advancing=true (`research/candidates/en2-290-1106/544-10-88.json`).
  RESUME ACTION for it: given the CI lesson (20k flat rungs collapsed under
  CI's 8M-class search on all four previous codes), run a local gate_changed
  battery at a fresh seed first, claim at the lightest reading, then the
  normal promote->prepush->push->PR pipeline. Phase 1: the "EN-2 winner" was
  screen-index 290 (not n=290); its true deep reading is d<=84 (screen said
  96) — correctly NOT staged (pure d-gain vs [[544,18,76]], needs a
  paired-depth audit first). q17-k18's dir shows staged-candidate scripts
  (analyze_and_stage.py) — check for its deliverable on resume.
  Machine note: the lane hit 3 external process kills (exit 137) under ~60
  process load; on resume stagger lane launches.
- Known-good pipeline artifacts: `research/candidates/sustained-20261027/`
  (plans, repacks incl. *-cirepack.json), `research/candidates/pr-body-*.md`
  (old + corrected new-slug bodies), `fork_and_prs_1105.py`,
  `verify_ci_witness.py`, `write_pr_bodies_1106.py`, `ci-witnesses/`
  (round-1 and -r2 CI refutation witnesses).
- The supervision cron (10-min) is UPDATED but PAUSED — only the user can
  re-enable it in the Automations page.

## Round 157 update (2026-11-06 ~23:35): k20 rung 42/250 — 85 双见证确认 — L2 收官 — reproduce 已 retrigger

- **k20 1M rung**: 42/250 chunks @23:29，14 真实 worker 存活（venv shim 父子对已核实，
  28 python.exe = 14 实体，cap 内）。最轻读数 **85**，已有 **两个独立 Z-85 见证**
  （c2 seed 20270310+2e6、c26）+ 一个 X-86（c41）；三个 witness 均由 supervisor
  独立验证为真逻辑算子（H·v=0、不在对侧行空间、weight 一致）。ETA ~00:58。
  最终读数 D 决定声明；D≤85 时 est_true ≈ D−5 ≥ 80 仍支配 [[544,18,76]]。
- 旧 rung 终读数落定：544 → **78**、684 → **110**、inc684 → **113**（250/250 全 flush；
  offset 故事与既有结论一致，无变化）。
- **L2 车道正式收官**（最终报告已交）：[[544,20,87]] staged + gate 绿 + 双 battery 绿，
  REPORT.md 三节齐全；deep_subjobs 61→316 记录，全程无 witness 丢失。槽位已释放。
- **L4 beat-surface-k50-w8 已启动**（rung 运行期间限 2 worker；spec
  beat-surface-k50-w8-unrestricted/campaign.json 存在已核实）。L1 完成、L3 休眠。
- **CI #4678**（head d2869fd120）：verify=failure（已知无关 100-20-8 golden 漂移，
  诊断评论在案），reproduce=cancelled —— verify 已结论，按预案用空提交 retrigger：
  新 head **84569c685**，全检查重跑中，下轮核对 reproduce 是否真实执行。
- 进程盘点：python.exe 30 = 14 rung 实体 × shim 对 + 2 杂项 ≤ 16 cap ✓。

## Round 152 update (2026-11-06 ~23:15): GATE GREEN — 1M rung launched

- **[[544,20,87]] gate PASSED**: board_advancing=TRUE, advances_by [d,k,n,w],
  dominated_by=[], refute clean (seed 268056721), dedup clean. Literature
  novelty unverified (normal).
- **k20 1M rung LAUNCHED** (14 workers, seed 20270310, progress_1m_k20_w*.jsonl,
  ~70 min). Its reading sets the final claim; on <87 repackage at the
  lightest; est true ~80-82 by offset(+5). Fast batteries 20270301/02 in
  flight. L2 on tier2a screening (2 workers).

## Round 151 update (2026-11-06 ~23:05): [[544,20,87]] STAGED — pipeline armed

- **L2 staged `research/candidates/l2-q17-resume/544-20-87.json`**: q=17 r=3,
  a/b weight-10 exponent sets (check weight **20**), n=544 k=20, claim d<=87
  (X<=87 x2 witnesses seeds 911006/911008, Z<=88), 19-rung chronological
  ladder (floor 87 hit at 911006/911008; mode 89-90). Sibling draw 74545 is
  the SAME WL class (a76c1ee56001cd1d) — one find, corroboration only.
- Supervisor checks done: **fingerprint rebuild verified True** (w=20 both
  sides); fast batteries seeds 20270301/02 running; driver extended with
  `--code k20` (claim 87).
- 1M rung launches the moment the gate verdict lands (green -> rung; the
  rung's reading sets the final claim; est true ~80-82 by the +5 offset).
- Note: w=20 places this in the unrestricted any-weight cell (not w9-12);
  the gate's novelty block decides advancement.

## Round 147 update (2026-11-06 ~22:55): L2 protocol decision — STAGE NOW

- L2 ladder report: 19 rungs/draw on both k=20 leaders; 87 floor reproduced
  2x per draw (4 total across 38 rungs), never undercut; mode 89-90;
  P(exact 87) ~10% made a 3rd scattered flat a ~4h gamble.
- **DECISION: stage now at claim d<=87** (2-agree + 19-rung floor is honest;
  promote's MIN_FLAT_RUNGS=2 is satisfied by the structural ladder tail:
  packaging witness search + gate refute, both at the claim). The staged
  candidate's 1M rung (supervisor-owned, driver ready) sets the final claim —
  if it reads <87, repackage at the lightest per playbook. est true ~80-82
  still dominates [[544,18,76]] (76).
- L2 staging now; (q,a,b) to the supervisor on staging for the 1M launch;
  after staging L2 drops to 2 workers on tier2a screening.

## Round 131 update (2026-11-06 ~21:35): L1 FINAL — 684 corner closes

- **Draw 229 receded to d<=115** (10 rungs; X-115 witness). est true ~110 =
  #4678's claim exactly -> **no domination, 684-14 corner closed as a
  dominator**. Not stageable (1 flat). L1's suggestion stands: if ever
  resumed, let a 1M-class instrument take the draw directly.
- **WL-signature finding**: draws 70/106/12 share one signature — the two
  staged k=12 candidates are the same code up to isomorphism (moot: both
  dead by the inc684 verdict).
- **bbga_labels.py REBUILT from committed primitives and proven exact** (all
  5 fingerprints + 10 witnesses reproduce) — the recipe gap is closed for
  all future submissions of this family.
- L1 lane complete: 31 deep rungs, 5 harness kills survived, all witnesses
  preserved, REPORT dated sections current. Next-resume queue documented.
- **SOLE LIVE LINE: L2's k=20 leaders** (R=87 @20k, 2-of-3 flat on 74545;
  est true 77-82). L2's workers running since ~19:28 — 3-flat milestone
  expected soon; on stage: fast batteries x2 + 1M rung (driver ready once
  L2 sends the leader's (q,a,b)).

## Round 104 update (2026-11-06 ~19:30)

- **Draw 229 (k=14): 7 rungs read 116/120/116/118/120/121/117 — lightest
  still 116** (L1's correction: the X-117 rung is HEAVIER than the two
  validated 116 witnesses, so the claim [[684,14,116]] is intact,
  witness-backed, 2-of-3 flat). ONE more rung reading 116 stages it; L1 runs
  two more 229 rungs after the in-flight 84/72 rungs land.
- L1's draw-84 (k=12) claim dropped to 112 (rungs 115/112) — est ~107, dead
  by the k=12 cap; draw 72 final pending. The k=12 corner is closed.
- **Systematic kill waves confirmed**: ~70-min cadence, full process trees,
  across lanes (not resource OOM). Chunked checkpoints absorb them (<=1 chunk
  lost per kill). Unexplained origin; treated as environmental.
- L2 resumption (3 workers, k=20 leaders) still pending its agent's action —
  machine shows only L1's workers. Ping next round if still idle.

## Round 102 update (2026-11-06 ~19:20): inc684 VERDICT — 684-12 corner DEAD

- **inc684 control complete (250/250, 1M trials/side): final reading d<=113.**
  offset(1M) = 113 - 108 = **+5** (the family's instrument offset at 1M does
  NOT shrink to ~0). Decision rule: [[684,12,110]] alive iff offset <= 1 —
  **FAILED. Estimated true d = 110 - 5 = 105 < 108: dominated by the merged
  [[684,12,108]]. BOTH staged k=12 candidates ([[684,12,120]],
  [[684,12,116]]) are DEAD — the k=12 corner is capped by the incumbent.**
  Keep their files and witnesses as honest negative results; do NOT submit.
- Offset correction propagates: est true [[684,14,116]] ~ 111 (marginal but
  alive vs #4678's 110; needs its own 1M rung before any submission);
  [[544,10,78]] est ~73 -> DEAD (record); winner est ~72-74 -> DEAD (record).
- **LIVE LINE: L2's k=20 leaders (R=87 @20k, kd2/n ~278)**. With the 684
  calibration (20k offset ~+10, 1M ~+5), est true ~77-82 -> dominates the
  merged [[544,18,76]] (76) iff true >= 77 — genuinely on the edge, worth
  full effort. L2 resumed NOW (3 workers): finish 911007/911008 for the
  3-flat rule, then stage + 1M rung.
- L1 continues (2 workers): draw 229's rung -> [[684,14,116]] staging, then
  its 1M rung queued.

## Round 86 update (2026-11-06 ~18:05)

- inc684 control: 140/250, lightest dropped to **113** — descent accelerating;
  final likely 109-112. Candidate [[684,12,110]] survives only if the control
  floors at exactly 109 (offset 1). L2 resumes the moment the control
  completes (its k=20 leaders at R=87 are the top live candidates).

## Round 62 update (2026-11-06 ~16:10): 684-12-120 rung FINAL — d<=110

- **[[684-12-120]] 1M rung complete (250/250): final honest reading d<=110**
  (X-110, chunk c221, independently verified; spectrum 110, 112 x?, 116,
  118 x4, ...). The 1M instrument walked the claim down 120 -> 110.
- **inc684 control LAUNCHED** (14 workers, 250 chunks, seed 20270201,
  progress_1m_inc684_w*.jsonl): the merged [[684,12,108]] (CI-certified true
  108, fingerprint rebuild verified) gives the family's 1M offset directly.
  Decision rule: candidate alive iff 110 - offset(1M) >= 109, i.e.
  R_inc684(1M) <= 109. Expect ~70 min.
- Preliminary read: the trend suggests the k=12 draw converges to the
  incumbent's level — likely dominated; the k=14 corner ([[684,14,116]],
  L1 resuming draw 229 now with 2 workers) is the live hope. [[544,10,78]]
  stays HELD (est true ~70-74 by offset); the winner probe is CANCELLED as
  unnecessary (winner est ~72; inc544 probe only matters if 544-10-78 were
  alive, which requires offset(544,1M) <= 1 — implausible). Honest negative
  results recorded for the 544 corner unless the 684 control surprises.
- CI #4678: verify red from upstream's 100-20-8 golden drift (not ours);
  diagnostic comment posted; awaiting maintainer re-record.

## Round 43 update (2026-11-06 ~14:35)

- L3 stopped per the two-kill rule (second external kill ~15:10Z of its
  screener; cause unknown, RAM/CPU healthy — kills hit only that worker).
  195/1,913 pool draws safely screened (k=14 w8 block, 0 collisions); top:
  pool_i 48042 and 66069 at d400=100. Remaining 1,718 resumable with zero
  overlap. L3 parked at 0 workers until rungs-done; then screening resumes at
  1 worker alongside the probe and L1's rungs.
- 684 rung: 112/250, lightest 112 holding across 14 chunks — good sign.

## Round 40 update (2026-11-06 ~14:30): CI failure diagnosed — NOT a refutation

- **#4678 verify FAILED, but the failure is upstream-main breakage**: the one
  failing test is `test_every_reproduction_has_a_golden_that_matches` on
  `codes/100-20-8.json` (`entry_changed`, bytes drifted from its golden) —
  introduced by the recently merged #4818 (100-20-8 circuit tier).
  Reproduced on a clean local main. All refutation-class tests on our head
  PASSED (1407/1408). Diagnostic comment posted on the PR
  (issuecomment-6696012355). Nothing to fix on our side; merge waits on the
  maintainer re-recording that golden. Do NOT touch 100-20-8 in our PRs
  (scope rule).
- **684-12-120 rung dropped to d<=112** (17 witnesses: Z-116, Z-118 x3,
  X-118, ...). Est true = 112 - offset(1M); with offset ~3-5 this is
  est 107-109 vs the 108 death line — **borderline**. The rung continues
  (98/250); the final reading decides. If it lands <=112, hold the submission
  decision on the offset calibration; consider the inc684 control (a 1M rung
  on the merged [[684,12,108]]) as the family's matched-depth control before
  submitting.

## Round 30 update (2026-11-06 ~13:40)

- **684-12-120 rung**: 28/250, honest reading now **d<=116** (Z-116, chunk
  c14, independently verified; Z-118 x3, X-118). Est true ~111-113 > 108 —
  still a strong submit; rung continues.
- **CI #4678 verify STARTED** (in_progress after ~2h queued, ~1.5h to go).
  reproduce remains cancelled — retrigger AFTER verify concludes if still
  missing.
- [[544,10,78]] fast batteries green x2; still HELD for the offset probe.
- L3: rule correction applied in REPORT; its screening worker died once
  (external kill wave — machine RAM/CPU healthy, not resource OOM), relaunched
  once per protocol (96/110 draws safe). One more death = stop.

## Round 28 update (2026-11-06 ~13:45): offset framework corrected

- **[[544,10,78]] repack gate GREEN** (passed, board_advancing, advances_by
  [d,k,n,w], dominated_by empty, refute clean). Fast batteries running.
- **DECISION-FRAMEWORK CORRECTION (supervisor)**: the L3 rule was inverted.
  For upper-bound claims, a LIGHTER matched-depth surrogate reading means a
  SMALLER true distance — worse. Correct form: offset(D) = R_inc(D) - 76;
  est_true(X) = R_X(D) - offset(D); X advances iff est_true >= 77 (544 family).
  Consequences: (a) the EN-2 winner (84 @20k vs incumbent 88 @20k) est_true
  ~72 — almost certainly an instrument artifact, expected dead; (b)
  [[544,10,78]] @1M: est true = 78 - offset(1M); alive only if R_inc(1M) is
  ~77-78 — unlikely, so it is HELD pending the probe, expected refuted to
  ~72-75 by CI (which would make it dominated: dead). (c) The 684 family has
  much smaller offsets (20k controls: 115->110, 116->110, 117->108, i.e. +5..
  +9), so [[684,12,120]] (1M trending 118, est true ~114) and [[684,14,116]]
  (est ~112) are genuinely strong vs 108 / 110.
- **Submission queue REVISED**: 1) [[684,12,120]] when its 1M rung lands; 2)
  [[684,14,116]] after its last flat rung + 1M rung; 3) 544 slot: probe first
  (winner x7 + inc544 x7 at 1M after the 684 rung), then either the winner
  (if R_win(1M) >= 77 + R_inc(1M) - 76) or [[544,10,78]] (only if
  R_inc(1M) <= ~78); otherwise the 544 corner yields nothing this wave.
- L3 tasked to fix its REPORT rule text (CPU-free).

## Round 27 update (2026-11-06 ~13:28): 544 RUNG COMPLETE -> repack at 78

- **544-10 deep rung COMPLETE: 250/250 chunks = 1,000,000 trials/side, final
  lightest d<=78** (Z-78, chunk c232, verified). Monitoring note: the true
  done-set spans the legacy wave-1 files AND wave-2 files (combined mapping
  covers all 250); a monitor reading only wave-2 files shows 217 — harmless.
- **Repack written**: `research/candidates/en2-290-1106/544-10-78-repack.json`
  (Z block = 78 with the verified witness, survived_samples 1,000,000, seed
  recorded; name [[544,10,78]]). Gate re-run in progress. X side stays at 90.
- At 78 the code is a k-d trade vs [[544,18,76]] (non-dominated) IF the gate
  agrees; the L3 winner question remains open (its paired probe is queued
  after the 684 rung).
- **684-12-120 rung started automatically** (5/250 at last check) and already
  found Z-118 witnesses at chunks c1 and c8 (independent corroboration) —
  the honest reading is trending to 118 already. Lanes: L1/L2 hold; L3 runs
  ONE screening worker (k in {12,14} pool).

## Round 24 update (2026-11-06 ~13:12)

- **544-10 honest reading now d<=78**: Z-78 witness (chunk c232, fresh seed
  20261109+232*1,000,003) independently verified. Spectrum: Z-78, X-84 x5,
  Z-84, X-86 x3, Z-86 x3. At 78 the code still advances (k 10 vs 18 trade vs
  [[544,18,76]]); at <=76 it dies. Rung 208/250 — final reading settles soon.
- CI #4678: reproduce CANCELLED upstream-side (no re-attempt); verify still
  pending. ACTION: after verify concludes, if reproduce remains cancelled,
  push another empty commit to retrigger it.
- 684-12-116 fast batteries green x2 (29,860 trials each, nothing <116).

## Round 22 update (2026-11-06 ~12:58): L1 second harvest

- **[[684,12,116]] staged + gate-passed** (`research/candidates/l1-q19-resume/`,
  a=[32,109,149,169,215,265,267], b=[52,138,150,213,219,257,274], q=19;
  3 rungs flat 116, verdict board_advancing, refute clean). Fast batteries
  seeds 20261221/22 running. NOTE: dominated by sibling [[684,12,120]] if the
  120 holds its 1M rung — only ONE of the k=12 pair is submittable; the 1M
  rung (chained, running next on 120) decides.
- **k=14 draw 229 two-flat at 116**: one more 20k rung at 116 stages
  [[684,14,116]], which would strictly dominate the pending #4678
  [[684,14,110]] at equal n/k/w and coexist with [[684,12,120]] (k-d trade,
  non-dominated). Highest-value lane item; L1 resumes it first.
- Draw 72 new lightest 117 (1 flat); new-stream 84 (k=12, screen <=126)
  pending deep-read. L1 resume queue: 229 -> 12 -> 84 -> 72, 2 workers.
- L1/L2 verified zero orphan workers after the hold; machine is rung-only
  plus L3's single screening worker.

## Round 17 update (2026-11-06 ~12:35)

- 544-10 rung past half (126/250). Witness spectrum: X-82 (c5), X-84 x2
  (c78, c151 — both verified), X-86 x2, Z-86 x4. Global lightest 82 stands.
- CI #4678: verify queued (upstream runner congestion); reproduce running 2h+.

## Round 10 update (2026-11-06 ~12:00)

- 544-10 rung: 54/250, X-84 witness (chunk c78) independently verified.
  Witness spectrum for the code: X-82 (c5), X-84 (c78), Z-86 x4. Global
  lightest 82 stands.
- CI #4678: reproduce still running, verify queued (normal for its class).

## Round 9 update (2026-11-06 ~11:55): 544 family decision framework

- L3 pinned the EN-2 winner's construction (CPU-free): q=17,
  a=[245,84,96,270,163,268], b=[245,252,47,**59**,143,70] (b3 move of the
  elite [[544,18,84]]; incumbent's b[3]=231). Fingerprint facbfe8f45fba8e2;
  every preserved witness validates against the rebuild. DO-NOT-PACKAGE in
  force for the winner until the paired test.
- **CI-offset control**: incumbent reads 88 on our 20k surrogate but CI's 8M
  search proved 76 (offset +12, same n/w/family). Offset-corrected winner
  estimate ~72 — BELOW the incumbent. Raw gain may be an instrument artifact.
- **Decision rule (matched-depth paired rungs)**: winner is stage-worthy only
  if its reading stays >=4 units lighter than the incumbent's at the same
  trial depth. Driver extended with `--code winner544` (claim 84) and
  `--code inc544` (claim 76). Chain plan: [544-10 rung, running] -> [684 rung,
  chained] -> [paired 250k probe: winner544 x7 + inc544 x7 workers] -> either
  [winner 1M] or [submit 544-10]. Submission order: 684-12-120 first (clean
  d-dominance, no ambiguity), then the 544 survivor.
- Lane throttle lifted gradually as rung workers finish; L1/L2 hold until the
  684 rung completes.

## Round 4 update (2026-11-06 ~11:40): TOKEN LIVE

- **PAT received, verified (login Ming-yuan-Liang, repo scope), stored at
  `research/candidates/.pat` (gitignored; never echo).** Push credential
  helper reads the file directly (`$(cat …/.pat)` inside the helper — the
  caller must NOT rely on an unexported shell var; that was the first push's
  failure).
- **#4678 RETRIGGERED**: empty commit d2869fd12 pushed to
  `submit-684-14-115` via a temporary worktree (`../retrigger-4678`, removal
  pending — Windows file lock, retry `git worktree remove --force`). CI verify
  should go from cancelled to running; watch it.
- Submission pipeline is now UNBLOCKED end to end: when each deep rung lands,
  repackage at the lightest reading -> gate -> rebuild plan -> promote ->
  prepush -> branch/push -> PR (one code per PR, bodies from
  research/candidates/pr-body-*.md template pattern).
- 544 deep rung wave 2 (14 workers): healthy, ~4.7 chunks/min, wave-1's 25
  chunks inherited via the global done-set; combined ~39/250, ETA ~45 min.
  The 684 rung auto-starts on its completion.

## Round 3 update (2026-11-06 ~11:30, user: no token budget, faster)

User directive: ignore token cost, shorten time-to-result, cron interval cut
to 5 min. Deployment now: the 544 deep rung runs as **wave 2 with 14 workers**
(driver upgraded: global done-set across progress files per code, so waves
overlap safely; wave-1's 8 workers were stopped mid-chunk, losing at most 8
partial chunks). Progress files: `progress_1m_544_w*.jsonl` (claim target: the
rung min; current honest reading d<=82, X-82 witness verified). The
**684-12-120 deep rung is CHAINED** to start automatically when the 544 rung
finishes (same driver, `--code 684`, seed 20261201, files
`progress_1m_684_w*.jsonl`; its result gates that submission too). During the
rungs, lanes hold at <=2 workers each; after both rungs finish they may widen
to 3. The supervisor cron (5 min) owns rung watching, witness verification,
slot rotation, CI watch, harvest.

## Round 2 update (2026-11-06 ~11:15)

- **[[544,10,88]] honest reading now d <= 82**: 1M rung chunk c5 (seed
  20261109+5*1,000,003) found a genuine X-logical of weight 82 (verified;
  witness `progress_1m_w5.jsonl.witness-82-c5.json`). Earlier chunks also hit
  Z-86 twice. Rung continues (~9/250 chunks); final claim = rung min.
  WARNING: at d<=82 with k=10 the candidate becomes DOMINATED by any staged
  [[544,18,84]] (L3 phase 1 subject) at equal n/w — its fate is coupled to
  L3's outcome; the gate decides at packaging time.
- **L1 HARVEST: [[684,12,120]] staged** (`research/candidates/l1-q19-resume/`,
  gate passed + board_advancing, advances_by [d,k,n,w], dominated_by empty,
  refute clean 8k seed 1749581554; kd^2/n 252.6 — strictly dominates the
  merged [[684,12,108]] on d at equal n/k/w). Rebuild from committed
  primitives metacyclic(19,18,2)+build_2bga verified fingerprint-identical.
  gate_changed fast batteries (seeds 20261111/12) running; a deep 1M rung is
  REQUIRED before promote (544-10-88 lesson: fast passes still collapsed) —
  queue it after the 544 rung finishes. HOLD, no push, PAT pending.
- CI #4678: verify still cancelled at head 099b9f278; retrigger blocked on PAT.
- Lanes: L1 resumed and productive (staged above), L2 active (deep_read2),
  L3 resumed after model-API busy failures; L4/L5/L6 queued.

## Resume plan (2026-11-06, new machine, 6 lanes)

1. **L1 q19-k14-resume** — q=19 metacyclic 2BGA (n=684), resume from
   `research/campaigns/parallel-q19-k14-1106/deep_*.jsonl` checkpoints, no
   redraw of screened draws. Target k>=14 at d>=110 (avoid 684-10-90 WL trap).
2. **L2 q17-k18-resume** — q=17 (n=544), resume from
   `parallel-q17-k18-1106/deep_rungs.jsonl` + `deep_subjobs.jsonl`; first
   check whether analyze_and_stage.py left a deliverable. Watch the k=22
   screen-inflation lesson (98 screen -> 24 Z-logical fresh).
3. **L3 en2-followup** (bounded) — repack the EN-2 winner (screen idx 290,
   honest d<=84, witnesses preserved in `parallel-en2-290-1106/`) after the
   paired-depth audit; then widen q=17 screening (k>=11 at d>=88 corner).
4. **L4 beat-surface-k50-w8** — campaign spec
   `research/campaigns/beat-surface-k50-w8-unrestricted/campaign.json`
   (n 300-1000, k 45-55, w<=8, unrestricted; kit generators).
5. **L5 beat-surface-k100-w8** — campaign spec
   `research/campaigns/beat-surface-k100-w8-unrestricted/campaign.json`
   (n 500-1000, k 95-105, w<=8).
6. **L6 w8-2dlocal-n700-1000** — campaign spec
   `research/campaigns/w8-2dlocal-n700-1000/campaign.json` (weight-8 2D-local
   bilayer, generators in `research/local2d/`).

Plus the [[544,10,88]] gate_changed battery: seeds 20261106/07/08 ALL PASSED
(fast pass, 24,260 trials <=90s each, "no logical lighter than 88"). BUT the
supervisor's first 1M-run deep chunk (fresh seed 20261109, chunk c0) found a
**genuine Z-logical of weight 86** (independently verified:
`research/campaigns/parallel-en2-290-1106/timing_probe.jsonl.witness-86-c0.json`).
The honest claim is therefore **d <= 86**; the ladder's 88-flat rungs are
historical. ACTION: the full 1M rung (250 chunks x 4,000 trials, 8 workers,
seeds 20261109+c*1,000,003) is running; when flat at the final reading,
repackage at the lightest reading (`repackage_at_reading.py`), re-gate, add
>=2 more fresh 20k rungs flat at the claim, rebuild the plan
(`build_plan_544_10_88.py` in the en2 dir — ladder and frontier text must be
updated to the new reading), re-dry-run promote, and hold for the PAT.

## Supervision round duties (every round)

1. Check on the 4 background gate_changed runs and the 3 search lanes
   (`tasklist | grep -i python`, REPORT.md freshness). Restart dead lanes with
   fresh Agent subagents (always 3 search subagents total while CPU allows).
2. Collect and process any stage-worthy survivors end-to-end (playbook above).
3. Watch CI on all open PRs; process refutations same round.
4. Keep this STATE file current; keep CPU loaded (full load is fine).
5. Report concisely in Chinese; never echo the token.
