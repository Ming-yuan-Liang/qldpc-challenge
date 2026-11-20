import os, sys, time
import numpy as np
ROOT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "research", "local2d"))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
import boundary_engine as be
import surrogate

pairs = [
    ("TILE4_MAIN", be.S_F_TILE4, be.S_G_TILE4_MAIN, 18),
    ("TILE4_PUB", be.S_F_TILE4, be.S_G_TILE4_PUBLISHED, None),
    ("W8", be.S_F_W8, be.S_G_W8, 12),
    ("08887", be.S_F_08887, be.S_G_08887, 12),
    ("B5-29", [[0,0],[1,3],[2,1],[4,4]], [[0,2],[1,4],[3,1],[4,0]], 29),
    ("B5-32", [[0,0],[1,3],[4,0],[4,4]], [[0,4],[2,1],[3,2],[4,0]], 32),
]
for tag, sf, sg, k20 in pairs:
    sf = [tuple(p) for p in sf]; sg = [tuple(p) for p in sg]
    mv = surrogate.mixed_volume(sf, sg)
    # k at 12x12 and 10x10
    ks = {}
    for L in (10, 12, 20):
        HX, HZ, info = be.build_planar(L, L, sf, sg)
        ks[L] = be.compute_k(HX, HZ)
    print(f"{tag}: MV={mv} k@10={ks[10]} k@12={ks[12]} k@20={ks[20]} board_k20={k20}")
