# MCP_INTEGRATION.md

## 使用的 MCP Server

- **服务**：麦当劳中国 MCP（McDonald's China MCP）
- **文档**：https://open.mcd.cn/mcp/doc
- **接入点**：`https://mcp.mcd.cn`（Streamable HTTP）
- **认证**：`Authorization: Bearer <MCP Token>`（Token 由用户在 open.mcd.cn 控制台自行申请，本项目通过环境变量 `MCD_MCP_TOKEN` 读取，不在代码或文档中存放任何凭证）
- **版本**：MCP 协议 `2024-11-05`；握手流程 `initialize` → `notifications/initialized` → `tools/list` / `tools/call`

## 实际调用的 Tool（5 个）

| Tool | 用途 | 在 Macnomics 中的角色 |
|---|---|---|
| `query-meals` | 查门店在售菜单（分类 + 产品码） | 优化问题的**决策变量来源**：116 个在售品 |
| `calculate-price` | 按门店/订单类型算价（含券） | **价格**的唯一可信来源；支持批量（一次 20 个） |
| `list-nutrition-foods` | 160 个餐品的营养成分（TOON 格式） | **热量/蛋白质**的唯一可信来源 |
| `query-store-coupons` | 查门店可用券 | 券建模为虚拟商品（买一送一 = 双倍营养、券后价） |
| `query-nearby-stores` | 按城市+关键词查门店 | `--store` 参数的门店发现（默认北京丽泽 SOHO 1950562） |

## 调用流程

```
query-nearby-stores（门店发现，可选）
        ↓
query-meals（拿 116 个产品码）
        ↓
calculate-price ×N 批量（拿每个码的真实售价）      ← 价格锚定分析的数据基础
        ↓
list-nutrition-foods（拿 160 项营养，按名对齐）
        ↓
query-store-coupons（可选 --coupons：券 → 虚拟商品）
        ↓
本地背包问题求解（动态规划，精确最优）
        ↓
输出最优组合 + 经济学一课
```

数据缓存 6 小时（`~/.cache/macnomics/`），遵守 600 req/min 限流。

## 业务价值

1. **把 MCP 从"查询工具"变成"决策引擎"**：不止查价格，而是把价格+营养+券喂进约束优化，输出可证明最优的点餐方案。
2. **用真实商业数据讲经济学**：价格锚定（套餐立省 76% 来自饮料锚）、边际成本（可乐 ¥1.5→¥9.5）、单位经济学（kcal/元）、效用套利——每个概念都有麦当劳的真实数字做证据。
3. **反向收割**：帮用户看穿定价套路，用券+免费品+单点组合拿回信息差利润；多出的份额转赠他人，完成"效用的最后一公里"。
