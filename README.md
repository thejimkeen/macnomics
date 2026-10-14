# Macnomics：用麦当劳学经济学

> McDonald's + Economics. 每次点餐，都是一堂经济学。

1024 程序员大多没系统学过经济学——但每个人都点过麦当劳。Macnomics 把麦当劳变成一间经济学教室：**你给预算和目标，它用动态规划算出精确最优组合，并告诉你这一单背后的经济学原理**：价格锚定、边际成本、约束优化、边际效用递减、机会成本、效用套利……

别人做"帮你点餐"，Macnomics 做"**教你为什么这么点**"。

## 目标用户

- 想吃得明白的麦门信徒：同样的钱，怎么吃蛋白更多、快乐更大
- 对经济学好奇但没时间啃书的程序员：每一单都是 3 分钟一课
- 想看穿商家定价套路的人：套餐的"立省 XX 元"是怎么算出来的

## 安装

零第三方依赖，只需要 Python 3.10+。

```bash
git clone https://github.com/thejimkeen/macnomics.git
cd macnomics
```

去 [open.mcd.cn](https://open.mcd.cn) 登录 → 控制台 → 激活，拿到你的 MCP Token：

```bash
export MCD_MCP_TOKEN=你的Token
```

## 使用

```bash
# 预算40元，蛋白质最大化（增肌）
python3 -m macnomics.cli --budget 40 --goal protein

# 预算30元，热量最大化（干饭）
python3 -m macnomics.cli --budget 30 --goal kcal

# 预算50元，蛋白质最大化但热量不超过800（减脂）
python3 -m macnomics.cli --budget 50 --goal balanced --kcal-cap 800

# 指定门店（默认北京丽泽SOHO店 1950562）
python3 -m macnomics.cli --budget 40 --goal protein --store 1950526

# 把可用优惠券也纳入优化
python3 -m macnomics.cli --budget 40 --goal protein --coupons

# 强制刷新缓存（菜单/价格缓存6小时）
python3 -m macnomics.cli --budget 40 --goal protein --refresh
```

示例输出：

```
=== Macnomics · 预算¥40 · 目标:protein ===

最优组合（动态规划精确解）:
  · 那么大鸡排（椒盐风味）x2  ¥28.00
  · 热牛奶中杯  ¥9.50

合计 ¥37.50｜946kcal｜蛋白58g
性价比 25.2kcal/元 · 1.55g蛋白/元

--- 今日一课：价格锚定：套餐的"立省"是算出来的 ---
原理：人们判断贵不贵，不看绝对价格，看参照物……
```

## 它教会你的第一课（剧透）

巨无霸三件套 ¥37.5，单点总和 ¥50（巨无霸26.5+中薯14+可乐9.5），"立省12.5"。但拿掉可乐的 ¥9.5 锚，只省 ¥3——**76% 的"优惠感"来自成本最低的饮料**（一杯可乐成本约 ¥1.5，毛利率 84%）。这就是价格锚定。

而真正的"反向收割"是：巨无霸单点 + 中薯买一送一（券后 ¥13.5 两份）+ 免费冰水 = ¥40 拿下 1091kcal / 35g 蛋白。买一送一多出的那份薯条，送给取餐的小哥或路边的阿姨——一句"谢谢"，一天的好心情。这是效用套利，也是 Macnomics 的最后一课。

## 项目结构

```
macnomics/
  mcp_client.py   # MCP Streamable-HTTP 客户端（零依赖）
  data.py         # 菜单/实时价格/营养库抓取与对齐
  optimize.py     # 背包问题精确求解（动态规划）
  lessons.py      # 经济学课程库 + 选课规则
  cli.py          # 命令行入口
```

## 课程大纲

1. 价格锚定 2. 边际成本 3. 单位经济学（kcal/元） 4. 约束优化 5. 边际效用递减 6. 机会成本 7. 效用套利

## 声明

- 本项目仅用于学习与技术交流，Token 请使用你自己的，不要分享。
- 菜单、价格、营养数据来自麦当劳官方 MCP 接口实时获取，各门店可能不同。
- `CONTEST_DECLARATION.md` 为大赛官方声明文件，内容未做任何修改。
