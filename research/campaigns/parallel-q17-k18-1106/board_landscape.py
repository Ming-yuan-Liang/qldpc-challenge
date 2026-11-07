"""Dominance thresholds for a [[544, k in 16..22, w in 16..20]] CSS candidate:
any CSS board entry with n<=544, k'>=k, d'>=d, w'<=w (one strict) dominates.
Read-only helper for lane q17-k18.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for _p in (os.path.join(_ROOT, "verify"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import validate_candidate  # noqa: E402

board = validate_candidate._board_entries()
css = []
for b in board:
    if b.get("code_type", "CSS") != "CSS":
        continue
    w = b.get("w")
    if w is None:
        continue
    css.append((int(b["n"]), int(b["k"]), int(b["d"]), int(w),
                b.get("weight_class", "?"), b["name"]))
css.sort()
print(f"board entries: {len(board)}, CSS with w known: {len(css)}")

print("\nCSS entries n<=544, k>=16, d>=60 (the threat pool):")
for n, k, d, w, wc, name in css:
    if n <= 544 and k >= 16 and d >= 60:
        print(f"  [[{n:4d},{k:3d},{d:3d}]] w={w:2d} {wc:13s} {name[:56]}")

print("\nminimum d a [[544,K,W]] needs to be potentially board-advancing:")
for K in range(16, 23):
    for W in (20, 18, 16):
        doms = [(d, w, n, name) for n, kk, d, w, wc, name in css
                if n <= 544 and kk >= K and w <= W]
        if doms:
            dmax = max(doms)
            print(f"  k={K} w<={W}: need d > {dmax[0]} "
                  f"(top dominator [[{dmax[2]},?,{dmax[0]}]] w={dmax[1]} {dmax[3][:44]})")
        else:
            print(f"  k={K} w<={W}: no dominator pool (any d advances)")
