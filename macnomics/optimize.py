"""Constrained optimization: the knapsack at the heart of Macnomics.

Given a budget (and optional kcal cap), pick the bundle that maximizes the
goal. Classic 0/1 knapsack with small integer prices (cents) -- exact solution
via dynamic programming, no heuristics.
"""
from __future__ import annotations


def knapsack(items: list[dict], budget: float, value_key: str,
             kcal_cap: float | None = None, max_qty: int = 2) -> list[dict]:
    """Maximize sum(value_key) s.t. sum(price) <= budget (and kcal <= cap).

    Each item may be taken up to max_qty times. Prices converted to cents.
    Returns the chosen list of item dicts (with 'qty').
    """
    B = int(round(budget * 100))
    # expand to unit copies
    units = []
    for it in items:
        if it["price"] <= 0:
            continue
        for _ in range(max_qty):
            units.append(it)
    n = len(units)
    # dp[b] = (value, kcal, picks-bitmask as tuple of indices)
    # n is a few hundred, B a few thousand -> fine.
    dp_val = [-1.0] * (B + 1)
    dp_kcal = [0.0] * (B + 1)
    dp_pick: list[tuple] = [() for _ in range(B + 1)]
    dp_val[0] = 0.0
    for i, u in enumerate(units):
        c = int(round(u["price"] * 100))
        v = float(u[value_key])
        k = float(u.get("kcal", 0))
        for b in range(B, c - 1, -1):
            if dp_val[b - c] < 0:
                continue
            nk = dp_kcal[b - c] + k
            if kcal_cap is not None and nk > kcal_cap:
                continue
            nv = dp_val[b - c] + v
            if nv > dp_val[b]:
                dp_val[b] = nv
                dp_kcal[b] = nk
                dp_pick[b] = dp_pick[b - c] + (i,)
    best_b = max(range(B + 1), key=lambda b: dp_val[b])
    chosen: dict[int, dict] = {}
    for i in dp_pick[best_b]:
        u = units[i]
        key = id(u)
        if key not in chosen:
            chosen[key] = dict(u, qty=0)
        chosen[key]["qty"] += 1
    return list(chosen.values())


def summarize(bundle: list[dict]) -> dict:
    cost = sum(it["price"] * it["qty"] for it in bundle)
    kcal = sum(it["kcal"] * it["qty"] for it in bundle)
    protein = sum(it["protein"] * it["qty"] for it in bundle)
    return {"cost": cost, "kcal": kcal, "protein": protein,
            "kcal_per_yuan": kcal / cost if cost else 0,
            "protein_per_yuan": protein / cost if cost else 0}
