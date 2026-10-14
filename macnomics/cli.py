#!/usr/bin/env python3
"""Macnomics: learn economics through McDonald's.

Every order is an economics lesson. Give a budget and a goal; Macnomics
computes the provably optimal bundle (knapsack, exact DP) and teaches you
the economics behind it.

Usage:
  macnomics --budget 40 --goal protein --store 1950562
  macnomics --budget 30 --goal kcal --store 1950562 --kcal-cap 800
  macnomics --budget 50 --goal protein --store 1950562 --coupons --refresh

Goals: protein (max protein), kcal (max calories), balanced (max protein under kcal cap).
Auth: set MCD_MCP_TOKEN env var (from https://open.mcd.cn console).
"""
from __future__ import annotations

import argparse
import sys

from .data import build_items, coupon_items
from .mcp_client import Session
from .optimize import knapsack, summarize
from .lessons import pick_lesson


def main() -> int:
    ap = argparse.ArgumentParser(prog="macnomics", description="Learn economics through McDonald's.")
    ap.add_argument("--budget", type=float, required=True, help="budget in yuan, e.g. 40")
    ap.add_argument("--goal", choices=["protein", "kcal", "balanced"], default="protein")
    ap.add_argument("--store", default="1950562", help="storeCode (default: 北京丽泽SOHO)")
    ap.add_argument("--kcal-cap", type=float, default=None, help="kcal ceiling (for balanced)")
    ap.add_argument("--coupons", action="store_true", help="include usable coupons as virtual items")
    ap.add_argument("--refresh", action="store_true", help="ignore cache, refetch live")
    args = ap.parse_args()

    items = build_items(args.store, refresh=args.refresh)
    sess = None
    if args.coupons:
        sess = Session()
        for c in coupon_items(sess, args.store):
            # 买一送一-style: coupon price, doubled nutrition of base item
            base = next((i for i in items if i["name"] == c.get("base")), None)
            if base and "买一送一" in c.get("title", ""):
                items.append({"code": c["code"], "name": c["name"], "price": c["price"],
                              "kcal": base["kcal"] * 2, "protein": base["protein"] * 2,
                              "fat": base["fat"] * 2, "carb": base["carb"] * 2,
                              "sodium": base["sodium"] * 2, "coupon": True})

    value_key = "protein" if args.goal in ("protein", "balanced") else "kcal"
    kcal_cap = args.kcal_cap if args.goal == "balanced" else None
    bundle = knapsack(items, args.budget, value_key, kcal_cap=kcal_cap)
    s = summarize(bundle)
    lesson = pick_lesson(bundle, s, args.goal)

    print(f"=== Macnomics · 预算¥{args.budget:.0f} · 目标:{args.goal} ===\n")
    print("最优组合（动态规划精确解）:")
    for it in bundle:
        q = f"x{it['qty']}" if it["qty"] > 1 else ""
        tag = " [券]" if it.get("coupon") else ""
        print(f"  · {it['name']}{q}{tag}  ¥{it['price'] * it['qty']:.2f}")
    print(f"\n合计 ¥{s['cost']:.2f}｜{s['kcal']:.0f}kcal｜蛋白{s['protein']:.0f}g")
    print(f"性价比 {s['kcal_per_yuan']:.1f}kcal/元 · {s['protein_per_yuan']:.2f}g蛋白/元")
    print(f"\n--- 今日一课：{lesson['title']} ---")
    print(f"原理：{lesson['principle']}")
    print(f"证据：{lesson['evidence']}")
    print(f"带走：{lesson['takeaway']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
