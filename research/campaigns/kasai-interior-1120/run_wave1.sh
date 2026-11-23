#!/bin/bash
# Wave-1 ladder (resume-safe): 3 fresh 20k rungs per doc, 4 workers.
# Skips rungs whose output file already exists.
DOCS=(684-14-107 544-20-76 684-16-124 684-14-128 544-20-94 544-18-91 544-16-95 544-14-98 684-26-124 684-18-124 684-16-127)
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
mkdir -p research/campaigns/kasai-interior-1120/wave1
for w in 0 1 2 3; do : > research/campaigns/kasai-interior-1120/wave1/w$w.txt; done
i=0
for doc in "${DOCS[@]}"; do
  for r in 1 2 3; do
    if [ ! -f "$DIR/$doc-rung$r.json" ]; then
      echo "$DIR/$doc.json $r 20000" >> research/campaigns/kasai-interior-1120/wave1/w$((i % 4)).txt
      i=$((i + 1))
    fi
  done
done
for w in 0 1 2 3; do
  (
    while read -r args; do
      echo "[$(date +%H:%M:%S)] START $args" >> research/campaigns/kasai-interior-1120/wave1/log.txt
      $PY -I research/campaigns/_12h-portfolio-shared/ladder_rerun.py $args \
        >> research/campaigns/kasai-interior-1120/wave1/log.txt 2>&1 \
        || echo "FAIL $args" >> research/campaigns/kasai-interior-1120/wave1/log.txt
    done < research/campaigns/kasai-interior-1120/wave1/w$w.txt
    echo "[$(date +%H:%M:%S)] worker$w done" >> research/campaigns/kasai-interior-1120/wave1/log.txt
  ) &
done
wait
echo "WAVE1 ALL DONE $(date +%H:%M:%S)" >> research/campaigns/kasai-interior-1120/wave1/log.txt
