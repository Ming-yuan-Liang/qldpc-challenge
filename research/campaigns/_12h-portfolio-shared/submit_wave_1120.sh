#!/usr/bin/env bash
# Submit the nine-code wave: one branch per code off upstream/main, one
# commit per code (codes/<slug>.json + notes/<slug>.md only), prepush prose
# check, PAT push to the fork. Does NOT open PRs (open_prs_1120.py does).
# Usage: bash submit_wave_1120.sh <slug> [<slug> ...]
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 1

PY=".venv/Scripts/python.exe"
export QLDPC_PYTHON="$PWD/$PY"
export PR_AUTHOR=Ming-yuan-Liang
BASE=upstream/main

ok=0; fail=0
for slug in "$@"; do
  echo "=== $slug $(date +%H:%M:%S) ==="
  body="research/candidates/pr-body-${slug}.md"
  [ -f "$body" ] || { echo "missing $body"; fail=$((fail+1)); continue; }
  [ -f "codes/${slug}.json" ] || { echo "missing codes/${slug}.json"; fail=$((fail+1)); continue; }

  git checkout -q -f "$BASE" 2>/dev/null
  git branch -D "submit-${slug}" 2>/dev/null
  git checkout -q -b "submit-${slug}" "$BASE" || { echo "branch fail"; fail=$((fail+1)); continue; }
  git add "codes/${slug}.json" "notes/${slug}.md" || { echo "add fail"; fail=$((fail+1)); continue; }
  git commit -q -m "$(python -I -c "
import json,sys
rep=json.load(open('promote-real-1120.json',encoding='utf-8'))
print(next(r['title'] for r in rep if r['slug']=='$slug'))")" || { echo "commit fail"; fail=$((fail+1)); continue; }

  if QLDPC_PYTHON="$QLDPC_PYTHON" PR_AUTHOR="$PR_AUTHOR" BASE="$BASE" \
     bash verify/prepush_prose_check.sh "$body" > "prepush_${slug}.log" 2>&1; then
    echo "prepush OK"
  else
    echo "PREPUSH FAIL (see prepush_${slug}.log)"; fail=$((fail+1)); continue
  fi

  pushed=0
  for i in 1 2 3 4 5 6 7; do
    TOK=$(cat research/candidates/.pat)
    if GIT_TERMINAL_PROMPT=0 git -c credential.helper= \
       -c "credential.helper=!f() { printf \"username=x-access-token\npassword=%s\n\" \"\$TOK\"; }; f" \
       push fork "submit-${slug}" -u 2>>"push_${slug}.log"; then
      pushed=1; break
    fi
    sleep 8
  done
  [ "$pushed" = 1 ] && { echo "push OK"; ok=$((ok+1)); } || { echo "PUSH FAIL"; fail=$((fail+1)); }
done

git checkout -q -f main
echo "SUBMIT-WAVE DONE: ok=$ok fail=$fail"
