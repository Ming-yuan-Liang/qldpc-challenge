"""L4 board snapshot + dominance checker (lane beat-surface-k50-w8-unrestricted).

Replicates verify/validate_candidate.py's novelty rule read-only:
a candidate is DOMINATED by board entry B iff B is CSS, same code_type,
B.weight_class order <= candidate's (i.e. B's max check weight is at most as
loose), B.locality order <= candidate's (all locality classes compete with an
unrestricted candidate), and B.n <= n, B.k >= k, B.d >= d, B.w <= w with at
least one strict.

The candidate advances (strict lane criterion) iff not dominated AND it
dominates at least one board entry on the four axes.
"""
import glob
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
CODES = os.path.join(_ROOT, "codes")

# weight_class from max check weight, nested: <=4, <=6, <=8, else 9plus
_WEIGHT_ORDER = {"weight-4": 0, "weight-6": 1, "weight-8": 2, "weight-9plus": 3}
_LOCAL_ORDER = {"local-2d-single": 0, "local-2d-bilayer": 1, "unrestricted": 2}


def weight_class(w):
    return "weight-4" if w <= 4 else "weight-6" if w <= 6 else \
        "weight-8" if w <= 8 else "weight-9plus"


def load_board(cache_path=None):
    """Snapshot of every CSS board entry as (n, k, d, w, name)."""
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return [tuple(r) for r in json.load(f)]
    rows = []
    for p in glob.glob(os.path.join(CODES, "*.json")):
        try:
            doc = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if doc.get("code_type", "CSS") != "CSS":
            continue
        ch = doc.get("checks") or {}
        xs, zs = ch.get("X") or [], ch.get("Z") or []
        if not xs and not zs:
            continue
        try:
            rows.append((int(doc["n"]), int(doc["k"]),
                         int(doc["distance"]["d"]),
                         max(len(s) for s in list(xs) + list(zs)),
                         os.path.basename(p)))
        except (KeyError, TypeError, ValueError):
            continue
    if cache_path:
        d = os.path.dirname(cache_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    return rows


def dominates(a, b):
    """Does candidate tuple a=(n,k,d,w) dominate board tuple b=(n,k,d,w,name)?"""
    an, ak, ad, aw = a
    bn, bk, bd, bw = b[0], b[1], b[2], b[3]
    if an <= bn and ak >= bk and ad >= bd and aw <= bw:
        return an < bn or ak > bk or ad > bd or aw < bw
    return False


def dominated_by(a, b):
    """Is candidate a dominated by board entry b?"""
    an, ak, ad, aw = a
    bn, bk, bd, bw = b[0], b[1], b[2], b[3]
    if bn <= an and bk >= ak and bd >= ad and bw <= aw:
        return bn < an or bk > ak or bd > ad or bw < aw
    return False


class Board:
    """Dominance oracle over the CSS board for unrestricted candidates."""

    def __init__(self, cache_path=None):
        self.entries = load_board(cache_path)

    def verdict(self, n, k, d, w):
        """Return (dominators, advances) for candidate (n, k, d, w).

        dominators: list of entry names that dominate the candidate
        (empty => the gate would call it board_advancing).
        advances: entries the candidate strictly dominates on >=1 axis.
        """
        cand = (n, k, d, w)
        wco = _WEIGHT_ORDER[weight_class(w)]
        dom, adv = [], []
        for e in self.entries:
            en, ek, ed, ew, name = e
            if ew > w:                      # entry weight class looser than mine
                continue
            if dominated_by(cand, e):
                dom.append(name)
            if dominates(cand, e):
                adv.append(name)
        return dom, adv


if __name__ == "__main__":
    import sys
    b = Board()
    print(f"board CSS entries: {len(b.entries)}")
    for arg in sys.argv[1:]:
        n, k, d, w = (int(x) for x in arg.split(","))
        dom, adv = b.verdict(n, k, d, w)
        print(f"({n},{k},{d},w{w}): dominated_by={len(dom)} {dom[:3]} "
              f"advances={len(adv)} e.g. {adv[:3]}")
