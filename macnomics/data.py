"""Data layer: menu + live prices + nutrition, joined into one item list.

Everything is fetched live from the McDonald's MCP server; results are cached
under ~/.cache/macnomics/ for 6 hours to stay polite (600 req/min limit).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .mcp_client import Session

CACHE_DIR = Path(os.environ.get("MACNOMICS_CACHE", Path.home() / ".cache" / "macnomics"))
CACHE_TTL = 6 * 3600


def _cache_path(store: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"items_{store}.json"


def _load_cache(store: str):
    p = _cache_path(store)
    if p.exists() and time.time() - p.stat().st_mtime < CACHE_TTL:
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def build_items(store_code: str, order_type: int = 1, be_type: int = 1,
                refresh: bool = False) -> list[dict]:
    """Return [{code, name, price, kcal, protein, fat, carb, sodium}] (price in yuan)."""
    if not refresh:
        cached = _load_cache(store_code)
        if cached:
            return cached
    sess = Session()

    # 1. menu codes
    menu = sess.call("query-meals", {"storeCode": store_code,
                                     "orderType": order_type, "beType": be_type})
    data = menu.get("structuredContent", {}).get("data", {}) or {}
    codes = list(dict.fromkeys(
        m["code"] for c in data.get("categories", []) for m in c.get("meals", [])))

    # 2. prices, batched (calculate-price accepts a list)
    prices: dict[str, tuple[str, float]] = {}
    for i in range(0, len(codes), 20):
        batch = codes[i:i + 20]
        r = sess.call("calculate-price", {
            "storeCode": store_code, "orderType": order_type, "beType": be_type,
            "items": [{"productCode": c, "quantity": 1} for c in batch]})
        for p in (r.get("structuredContent", {}).get("data", {}) or {}).get("productList", []):
            prices[p["productCode"]] = (p["productName"], p["subtotal"] / 100)

    # 3. nutrition (TOON string)
    nut = sess.call("list-nutrition-foods", {})
    toon = nut.get("structuredContent", {}).get("data", "") or ""
    nutrition = []
    for line in toon.strip().split("\n")[1:]:
        parts = [x.strip() for x in line.strip().split(",")]
        if len(parts) >= 9 and parts[0]:
            try:
                nutrition.append({"name": parts[0], "kcal": float(parts[3] or 0),
                                  "protein": float(parts[4] or 0), "fat": float(parts[5] or 0),
                                  "carb": float(parts[6] or 0), "sodium": float(parts[7] or 0)})
            except ValueError:
                pass

    # 4. join on name
    items = []
    for code, (name, price) in prices.items():
        if price <= 0:
            continue
        m = next((n for n in nutrition if n["name"] == name), None)
        if not m:
            m = next((n for n in nutrition if n["name"] and (n["name"] in name or name in n["name"])), None)
        if m and m["kcal"] > 0:
            items.append({"code": code, "name": name, "price": price, **{k: m[k] for k in
                          ("kcal", "protein", "fat", "carb", "sodium")}})
    _cache_path(store_code).write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return items


def coupon_items(sess: Session, store_code: str, order_type: int = 1,
                 be_type: int = 1) -> list[dict]:
    """Model usable coupons as virtual items (e.g. 买一送一 = 2x nutrition, ~1x price)."""
    r = sess.call("query-store-coupons", {"storeCode": store_code,
                                          "orderType": order_type, "beType": be_type})
    data = r.get("structuredContent", {}).get("data", []) or []
    out = []
    for c in data:
        title = c.get("title", "")
        prods = c.get("products", []) or []
        if not prods:
            continue
        pc = prods[0]["productCode"]
        calc = sess.call("calculate-price", {
            "storeCode": store_code, "orderType": order_type, "beType": be_type,
            "items": [{"productCode": pc, "quantity": 1,
                       "couponId": c.get("couponId"), "couponCode": c.get("couponCode")}]})
        pl = (calc.get("structuredContent", {}).get("data", {}) or {}).get("productList", [])
        if not pl:
            continue
        # "买一送一"-style: double the nutrition of the base product at coupon price
        base_name = prods[0].get("productName", "")
        out.append({"code": pc, "name": f"{title}(券)", "price": pl[0]["subtotal"] / 100,
                    "coupon": True, "base": base_name, "title": title})
    return out
