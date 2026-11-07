"""Kasai affine 2BGA codes over Aff(F_q) in its metacyclic realization.

Local, untracked helper (reconstructed 2026-11-06 by the l1-q19-resume lane
after the previous session's copy was lost; the construction primitives are
committed ``research/kit/group_algebra.py`` code, and the reconstruction is
pinned by the recorded css_fingerprints and RIS witnesses of campaign
parallel-q19-k14-1106 -- see ``research/campaigns/parallel-q19-k14-1106/``).

Aff(F_q) = F_q x| F_q^* = Z_q x| Z_{q-1} with action j: i -> r^j * i (mod q),
r the smallest primitive root mod q (2 for q=19, 3 for q=17). That is exactly
``group_algebra.metacyclic(q, q-1, r)``: elements (i, j) at index i*(q-1)+j,
identity at 0. ``build_2bga_affine(q, a, b)`` then builds the Lin-Pryadko
left-right 2BGA on that Cayley table with exponent sets a, b (element indices
in [0, q*(q-1))): n = 2*q*(q-1) (684 for q=19, 544 for q=17), check weight
|a| + |b|. CSS commutation is automatic (left and right multiplication
commute).
"""
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from group_algebra import build_2bga, metacyclic  # noqa: E402


def smallest_primitive_root(q):
    """Smallest primitive root modulo the prime q (2 for q=19, 3 for q=17)."""
    for r in range(2, q):
        if all(pow(r, k, q) != 1 for k in range(1, q - 1)):
            return r
    raise ValueError(f"no primitive root found for q={q}")


_TABLE_CACHE = {}


def affine_table(q):
    """Cayley table of Aff(F_q) in its metacyclic realization (memoized)."""
    if q not in _TABLE_CACHE:
        r = smallest_primitive_root(q)
        mul, labels = metacyclic(q, q - 1, r)
        assert labels[0] == (0, 0) and mul.shape == (q * (q - 1),) * 2
        _TABLE_CACHE[q] = mul
    return _TABLE_CACHE[q]


def build_2bga_affine(q, a, b):
    """HX, HZ of the affine 2BGA over Aff(F_q) with exponent sets a, b.

    ``a`` and ``b`` are lists of element indices into the metacyclic labeling
    (i, j) -> i*(q-1) + j. Returns int8 arrays of shape (q*(q-1), 2*q*(q-1)).
    """
    return build_2bga(affine_table(q), list(a), list(b))


if __name__ == "__main__":
    from css import verify_css, compute_k

    for q in (17, 19):
        mul = affine_table(q)
        HX, HZ = build_2bga_affine(q, [0, 1, 2], [0, q - 1, 2 * (q - 1)])
        print(f"q={q}: table {mul.shape}, n={HX.shape[1]}, "
              f"css={verify_css(HX, HZ)}, k={compute_k(HX, HZ)}")
