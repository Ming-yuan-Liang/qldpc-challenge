#!/bin/bash
# Wave-17: 684-14-128b deep ladder stage 1 (200k x3, fast pd12, 1 worker).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/684-14-128b.json 4 200000 fast 12" \
      "$DIR/684-14-128b.json 5 200000 fast 12" \
      "$DIR/684-14-128b.json 6 200000 fast 12")
: > $W/w17_0.txt
for job in "${JOBS[@]}"; do
  doc=$(echo "$job" | awk '{print $1}')
  r=$(echo "$job" | awk '{print $2}')
  rungf="${doc%.json}-rung$r.json"
  [ ! -f "$rungf" ] && echo "$job" >> $W/w17_0.txt
done
(
  while read -r args; do
    echo "[$(date +%H:%M:%S)] START $args" >> $W/log.txt
    $PY -I research/campaigns/_12h-portfolio-shared/ladder_rerun.py $args \
      >> $W/log.txt 2>&1 \
      || echo "FAIL $args" >> $W/log.txt
  done < $W/w17_0.txt
  echo "[$(date +%H:%M:%S)] wave17-worker0 done" >> $W/log.txt
) &
wait
echo "WAVE17 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
