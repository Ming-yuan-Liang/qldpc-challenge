"""Run the L5 harvest batteries (6 codes x 2 fresh seeds) sequentially.

Writes one line per battery to battery_harvest.log, flushed immediately.
"""
import subprocess
import sys
import os

ROOT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge"
LOG = os.path.join(ROOT, "research", "campaigns", "beat-surface-k100-w8-unrestricted",
                   "battery_harvest.log")

codes = ["510-102-19", "588-98-22", "686-98-22", "686-98-23", "686-98-24", "714-102-25"]
seeds = [(20270601, 20270602), (20270603, 20270604), (20270605, 20270606),
         (20270607, 20270608), (20270609, 20270610), (20270611, 20270612)]

with open(LOG, "a", encoding="utf-8") as log:
    for code, (s1, s2) in zip(codes, seeds):
        for s in (s1, s2):
            p = os.path.join(ROOT, "research", "candidates", "l5-beat-surface", f"{code}.json")
            try:
                r = subprocess.run([sys.executable, os.path.join(ROOT, "verify", "gate_changed.py"),
                                    p, "--seed", str(s)],
                                   capture_output=True, text=True, timeout=600, cwd=ROOT)
                tail = (r.stdout + r.stderr).strip().splitlines()
                line = tail[-1] if tail else f"(no output, exit {r.returncode})"
                log.write(f"{code} seed {s}: exit={r.returncode} | {line}\n")
            except subprocess.TimeoutExpired:
                log.write(f"{code} seed {s}: TIMEOUT (600s)\n")
            log.flush()
    log.write("ALL_BATTERIES_DONE\n")
    log.flush()
print("done")
