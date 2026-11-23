#!/bin/bash
# A1 batch-3 sweeps: fresh seeds, sequential, 6000 draws each.
PY=.venv/Scripts/python.exe
LOG=research/campaigns/kasai-interior-1120/sweep_batch3.log
echo "[$(date +%H:%M:%S)] batch3 start" >> $LOG
$PY -I research/campaigns/kasai-interior-1120/interior_sweep.py \
  --q 19 --weight 8 --num 6000 --seed 42006 --workers 2 >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] q19 s42006 done" >> $LOG
$PY -I research/campaigns/kasai-interior-1120/interior_sweep.py \
  --q 19 --weight 7 --num 4000 --seed 42007 --workers 2 >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] q19 s42007 (w7 diversity) done -> BATCH3 ALL DONE" >> $LOG
