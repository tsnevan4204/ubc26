"""Build evidence figures for the Wormhole (W) long thesis.

Data: Wormholescan public API, DeFiLlama API, Binance public market data,
CoinGecko markets endpoint. Pulled 2026-11-10 (UTC). Raw files in ./data.
Run: python3 make_figures.py  (from wormhole_analysis/)
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import pandas as pd

D = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

GREEN, DARK, GRAY, LIGHT, RED, INK = "#1fae7a", "#0b1f17", "#c9d1cd", "#eef3f0", "#e8643c", "#1c2622"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#9aa5a0",
    "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
    "axes.titlesize": 12, "axes.titlelocation": "left", "figure.dpi": 100,
    "savefig.dpi": 220, "savefig.bbox": "tight", "axes.grid": False, "text.color": INK,
    "axes.labelcolor": INK, "text.parse_math": False, "xtick.color": INK, "ytick.color": INK,
})
SRC = "Source: {}. Pulled Nov 10, 2026 (UTC)."
musd = mt.FuncFormatter(lambda v, _: f"${v/1e6:,.0f}M")
busd = mt.FuncFormatter(lambda v, _: f"${v/1e9:,.1f}B")


def foot(fig, text):
    fig.text(0.01, -0.09, text, fontsize=7.5, color="#5d6a64", ha="left")


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def klines(sym):
    k = pd.DataFrame(json.load(open(D / f"kl_{sym}.json"))).iloc[:, [0, 4]]
    k.columns = ["t", "close"]
    k["date"] = pd.to_datetime(k.t, unit="ms")
    return k.set_index("date").close.astype(float)


score = json.load(open(D / "scorecards.json"))
cg = {c["id"]: c for c in json.load(open(D / "cg_markets.json"))}
monthly = pd.read_csv(D / "xchain_tops_monthly.csv", parse_dates=["date"]).set_index("date")
app_m = pd.read_csv(D / "app_monthly.csv", parse_dates=["date"])
app_d = pd.read_csv(D / "app_daily.csv", parse_dates=["date"])
w = klines("WUSDT")

# ---------------------------------------------------------------- F1
# Volume vs price divergence since W listing
m = monthly.loc["2024-04-01":"2026-10-01"].copy()
wp = w.resample("MS").mean().reindex(m.index)
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(m.index, m.usd, width=22, color=[GREEN if d >= pd.Timestamp("2026-07-01") else GRAY for d in m.index])
ax.yaxis.set_major_formatter(busd)
ax.set_ylabel("Monthly cross-chain volume")
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax2 = ax.twinx()
ax2.plot(wp.index, wp.values, color=DARK, lw=2)
ax2.set_ylabel("W price (monthly avg, $)")
ax2.spines["right"].set_visible(True)
ax2.set_ylim(0, wp.max() * 1.1)
jul, octo = m.loc["2026-07-01", "usd"], m.loc["2026-10-01", "usd"]
ax.annotate(f"July 2026: W all-time low,\nvolume trough ${jul/1e6:.0f}M", xy=(pd.Timestamp("2026-07-01"), jul),
            xytext=(pd.Timestamp("2025-08-01"), m.usd.max() * 0.85), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color="#5d6a64"))
ax.set_title(f"Volume has recovered {m.loc['2026-08-01':'2026-10-01','usd'].mean()/m.loc['2026-05-01':'2026-07-01','usd'].mean():.1f}x off the July low; the token has not")
foot(fig, SRC.format("Wormholescan x-chain-activity (monthly, all emitter chains); Binance WUSDT daily closes"))
save(fig, "F01_volume_vs_price")

# ---------------------------------------------------------------- F2
# Scope reconciliation: what "Wormhole volume" means
last = app_d[(app_d.date >= "2026-10-10") & (app_d.date <= "2026-11-09")]
by = last.groupby("app").usd.sum()
rows = [
    ("Allium x LayerZero dashboard\n(GMP cohort, undated snapshot)", 21.89e6, RED),
    ("Wormhole GMP app", by["GMP"], GRAY),
    ("Portal token bridge", by["PORTAL_TOKEN_BRIDGE"], GRAY),
    ("Native Token Transfers (NTT)", by["NATIVE_TOKEN_TRANSFER"], GRAY),
    ("NEAR Omni Bridge", by["OMNI_BRIDGE"], GRAY),
    ("All Wormhole messages (scorecard)", float(score["30d_volume"]), GREEN),
]
fig, ax = plt.subplots(figsize=(8, 3.6))
labels, vals, cols = zip(*rows)
ax.barh(labels[::-1], vals[::-1], color=cols[::-1])
for i, v in enumerate(vals[::-1]):
    ax.text(v + 1e7, i, f"${v/1e6:,.0f}M", va="center", fontsize=9)
ax.xaxis.set_major_formatter(musd)
ax.set_xlim(0, max(vals) * 1.15)
ax.set_title(f"The '0.17% share' stat measures GMP only: total 30-day volume is {float(score['30d_volume'])/21.89e6:.0f}x larger")
foot(fig, SRC.format("Wormholescan application-activity, Oct 10 to Nov 9 2026; scorecards 30d; digital-asset-interoperability.com snapshot"))
save(fig, "F02_scope_reconciliation")

# ---------------------------------------------------------------- F3
# App mix over time (new engines of volume)
keep = {"PORTAL_TOKEN_BRIDGE": "Portal token bridge", "NATIVE_TOKEN_TRANSFER": "NTT",
        "OMNI_BRIDGE": "NEAR Omni Bridge", "CCTP_WORMHOLE_INTEGRATION": "CCTP (USDC)",
        "MAYAN_SWIFT": "Mayan Swift", "GMP": "GMP", "CONNECT": "Connect"}
p = app_m[app_m.app.isin(keep)].pivot_table(index="date", columns="app", values="usd", aggfunc="sum").fillna(0)
p = p.loc["2024-01-01":"2026-10-01"].rename(columns=keep)
order = ["Portal token bridge", "NTT", "NEAR Omni Bridge", "CCTP (USDC)", "Mayan Swift", "GMP", "Connect"]
pal = ["#9aa5a0", GREEN, DARK, "#6fc9a4", "#c9d1cd", RED, "#e3e8e5"]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.stackplot(p.index, [p[c] for c in order], labels=order, colors=pal, alpha=0.95)
ax.yaxis.set_major_formatter(busd)
ax.legend(loc="upper left", fontsize=8, ncol=2, frameon=False)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("New volume engines: NEAR Omni Bridge (from Aug 2026) and NTT")
foot(fig, SRC.format("Wormholescan application-activity (monthly). Labeled apps only; excludes unattributed messages"))
save(fig, "F03_app_mix")

# ---------------------------------------------------------------- F4
# What moves: asset composition (top symbols, 30d)
s = pd.read_csv(D / "top_symbols_30d.csv")
cls = {"SOL": "Blue chip", "WETH": "Blue chip", "USDC": "Stablecoin", "USDT": "Stablecoin",
       "WHYPE": "Hyperliquid (HYPE)", "hype": "Hyperliquid (HYPE)", "zec": "Other"}
s["cls"] = s.symbol.map(cls).fillna("Other")
g = s.groupby("cls").volume.sum().sort_values(ascending=False)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.5, 3.4), gridspec_kw=dict(width_ratios=[1, 1.3]))
a1.pie(g, colors=[GREEN, DARK, "#6fc9a4", GRAY][:len(g)], startangle=90, wedgeprops=dict(width=0.42))
a1.legend([f"{k} {v/g.sum():.0%}" for k, v in g.items()], loc="center left", bbox_to_anchor=(-0.45, 0.5), frameon=False, fontsize=8.5)
s2 = s.sort_values("volume")
a2.barh(s2.symbol, s2.volume, color=[GREEN if c != "Other" else GRAY for c in s2.cls])
a2.xaxis.set_major_formatter(musd)
for i, (v, t) in enumerate(zip(s2.volume, s2.txs)):
    a2.text(v + 2e6, i, f"${v/t:,.0f} avg", va="center", fontsize=8)
a2.set_xlim(0, s2.volume.max() * 1.35)
fig.suptitle(f"Not memecoin churn: {g.drop('Other', errors='ignore').sum()/g.sum():.0%} of top-7-asset volume is SOL, ETH, stablecoins and HYPE",
             x=0.01, ha="left", fontweight="bold", fontsize=12)
foot(fig, SRC.format("Wormholescan top-symbols-by-volume, 30d (top 7 symbols = $%.0fM)" % (s.volume.sum() / 1e6)))
save(fig, "F04_asset_mix")

# ---------------------------------------------------------------- F5
# Chain-level traction, last 30 days
CH = {1: "Solana", 2: "Ethereum", 4: "BNB Chain", 5: "Polygon", 6: "Avalanche", 14: "Celo", 15: "NEAR",
      21: "Sui", 23: "Arbitrum", 24: "Optimism", 30: "Base", 44: "Unichain", 47: "HyperEVM", 50: "Mezo", 55: "Chain 55"}
xd = pd.read_csv(D / "xchain_daily_by_chain.csv", parse_dates=["date"])
c30 = xd[xd.date >= "2026-10-10"].groupby("emitter_chain").usd.sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 3.6))
names = [CH.get(i, f"Chain {i}") for i in c30.index]
hl = {"HyperEVM", "Unichain"}
ax.barh(names[::-1], c30.values[::-1], color=[GREEN if n in hl else GRAY for n in names[::-1]])
for i, v in enumerate(c30.values[::-1]):
    ax.text(v + 3e6, i, f"${v/1e6:,.0f}M", va="center", fontsize=9)
ax.xaxis.set_major_formatter(musd)
ax.set_xlim(0, c30.max() * 1.15)
ax.set_title("Hyperliquid routes are already a top-5 source chain (HyperEVM + Unichain)")
foot(fig, SRC.format("Wormholescan x-chain-activity/tops, daily by emitter chain, Oct 10 to Nov 9 2026. Chain 55 unlabeled"))
save(fig, "F05_source_chains")

# ---------------------------------------------------------------- F6
# NTT: listed market cap vs real flow (concentration)
n = pd.read_csv(D / "ntt_tokens.csv")
n = n.groupby("symbol", as_index=False).agg(volume_30d=("volume_30d", "sum"), market_cap=("market_cap", "max"))
top = n.sort_values("volume_30d", ascending=False)
tot = top.volume_30d.sum()
t8 = top.head(8)
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.barh(t8.symbol[::-1], t8.volume_30d[::-1], color=[GREEN if s in ("WHYPE", "hype") else GRAY for s in t8.symbol[::-1]])
for i, v in enumerate(t8.volume_30d[::-1]):
    ax.text(v + 1e6, i, f"{v/tot:.0%}", va="center", fontsize=9)
ax.xaxis.set_major_formatter(musd)
ax.set_xlim(0, t8.volume_30d.max() * 1.15)
active = (n.volume_30d > 1e6).sum()
ax.set_title(f"NTT flow is concentrated: {len(n)} tokens listed, {active} moved >$1M in 30 days")
foot(fig, SRC.format(f"Wormholescan native-token-transfer/token-list; 30d NTT volume ${tot/1e6:.0f}M. "
                     "Listed market cap of NTT tokens is dominated by USDT/USDC, which move little via NTT"))
save(fig, "F06_ntt_concentration")

# ---------------------------------------------------------------- F7
# Corrected TVL comparison
tv = pd.read_csv(D / "tvl_history.csv", parse_dates=["date"]).set_index("date")
lastv = tv.ffill().iloc[-1]
lab = {"layerzero-v2": "LayerZero V2", "ccip": "Chainlink CCIP", "portal": "Wormhole (Portal)", "axelar": "Axelar"}
lv = lastv.rename(lab).sort_values()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.4), gridspec_kw=dict(width_ratios=[1, 1.4]))
a1.barh(lv.index, lv.values, color=[GREEN if "Wormhole" in i else GRAY for i in lv.index])
for i, v in enumerate(lv.values):
    a1.text(v + 2e8, i, f"${v/1e9:.2f}B", va="center", fontsize=8.5)
a1.xaxis.set_major_formatter(busd); a1.set_xlim(0, lv.max() * 1.35)
a1.set_title("TVL today")
h = tv.loc["2024-01-01":].resample("W").last()
for c, col in [("portal", GREEN), ("ccip", DARK), ("axelar", GRAY)]:
    a2.plot(h.index, h[c], color=col, lw=2, label=lab[c])
a2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); a2.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
a2.yaxis.set_major_formatter(busd); a2.legend(frameon=False, fontsize=8); a2.set_title("TVL history")
fig.suptitle("Wormhole holds $1.3B, not $3.0B; LayerZero V2 is far larger under DeFiLlama's method",
             x=0.01, ha="left", fontweight="bold", fontsize=12, y=1.04)
foot(fig, SRC.format("DeFiLlama /protocol (portal, layerzero-v2, ccip, axelar). LayerZero V2 TVL series begins mid-2026"))
save(fig, "F07_tvl_corrected")

# ---------------------------------------------------------------- F8
# Fee-normalised and TVL-normalised valuation
fees1y = {}
rev1y = {}
for k, f in [("W", "portal"), ("ZRO", "layerzero"), ("AXL", "axelar")]:
    fees1y[k] = json.load(open(D / f"fees_{f}.json"))["total1y"]
    rev1y[k] = json.load(open(D / f"rev_{f}.json"))["total1y"]
mc = {"W": cg["wormhole"]["market_cap"], "ZRO": cg["layerzero"]["market_cap"], "AXL": cg["axelar"]["market_cap"]}
tvl = {"W": lastv["portal"], "ZRO": lastv["layerzero-v2"], "AXL": lastv["axelar"]}
val = pd.DataFrame({"Market cap": mc, "1y fees": fees1y, "1y revenue": rev1y, "TVL": tvl})
val["MC / 1y fees"] = val["Market cap"] / val["1y fees"]
val["MC / TVL"] = val["Market cap"] / val["TVL"]
val.to_csv(OUT / "valuation_multiples.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.2))
for ax, col, fmt in [(a1, "MC / 1y fees", "{:.0f}x"), (a2, "MC / TVL", "{:.3f}x")]:
    v = val[col].sort_values()
    ax.barh(v.index, v.values, color=[GREEN if i == "W" else GRAY for i in v.index])
    for i, x in enumerate(v.values):
        ax.text(x * 1.02, i, fmt.format(x), va="center", fontsize=9)
    ax.set_xlim(0, v.max() * 1.25); ax.set_title(col + (" (lower = cheaper)"))
fig.suptitle("On fees W is cheaper than ZRO and AXL; on TVL it sits between them",
             x=0.01, ha="left", fontweight="bold", fontsize=12, y=1.04)
foot(fig, SRC.format("CoinGecko markets (circulating MC); DeFiLlama fees (trailing 365d) and TVL. None of these fees accrue to W today"))
save(fig, "F08_valuation_multiples")

# ---------------------------------------------------------------- F9
# Value-accrual gap: break-even take rate vs observed
vol1y = float(score["1y_volume"])
price = cg["wormhole"]["current_price"]
unlock_tokens = 50.41e6 * 26
unlock_usd = unlock_tokens * price
obs_bps = fees1y["W"] / vol1y * 1e4
need_bps = unlock_usd / vol1y * 1e4
fig, ax = plt.subplots(figsize=(8, 2.8))
bars = [("Observed fee rate (all fees,\n0% to W today)", obs_bps, GRAY),
        ("Rate needed for the Reserve to buy\nevery unlocked W at today's price", need_bps, GREEN)]
ax.barh([b[0] for b in bars][::-1], [b[1] for b in bars][::-1], color=[b[2] for b in bars][::-1])
for i, b in enumerate(bars[::-1]):
    ax.text(b[1] + 0.1, i, f"{b[1]:.2f} bps", va="center", fontsize=10, fontweight="bold")
ax.set_xlim(0, need_bps * 1.3); ax.set_xlabel("basis points of annual volume")
ax.set_title(f"To absorb ${unlock_usd/1e6:.1f}M/yr of unlocks, Wormhole must monetise {need_bps/obs_bps:.0f}x more than it does")
foot(fig, SRC.format(f"Wormholescan 1y volume ${vol1y/1e9:.1f}B; DeFiLlama Portal 1y fees ${fees1y['W']/1e3:.0f}k, revenue $0; "
                     f"unlocks 50.41M W biweekly (Tokenomist) x ${price:.4f}"))
save(fig, "F09_value_accrual_gap")

# ---------------------------------------------------------------- F10
# Supply overhang
circ = cg["wormhole"]["circulating_supply"]
months = pd.date_range("2026-11-01", "2028-10-01", freq="MS")
sup = [min(circ + 50.41e6 * (26 / 12) * i, 10e9) for i in range(len(months))]
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.fill_between(months, sup, color=LIGHT); ax.plot(months, sup, color=DARK, lw=2)
ax.axhline(10e9, color=GRAY, ls="--", lw=1); ax.text(months[0], 10.05e9, "Max supply 10B", fontsize=8)
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1e9:.1f}B"))
ax.set_ylim(6e9, 10.5e9)
y1 = sup[12]
ax.annotate(f"Nov 2027: {y1/1e9:.2f}B (+{y1/circ-1:.0%})", xy=(months[12], y1), xytext=(months[3], 9.3e9),
            arrowprops=dict(arrowstyle="-", color="#5d6a64"), fontsize=9)
ax.set_title("Circulating W if the 50.41M biweekly schedule continues")
foot(fig, SRC.format("CoinGecko circulating supply; Tokenomist biweekly unlock size. Linear projection, not a published schedule"))
save(fig, "F10_supply_projection")

# ---------------------------------------------------------------- F11
# Relative performance vs peers
px = pd.DataFrame({s: klines(s + "USDT") for s in ["W", "ZRO", "AXL", "BTC"]}).loc["2025-01-01":]
px = px / px.iloc[0] * 100
fig, ax = plt.subplots(figsize=(8, 3.4))
for s, c, lw in [("BTC", "#9aa5a0", 1.5), ("AXL", GRAY, 1.5), ("ZRO", DARK, 1.5), ("W", GREEN, 2.5)]:
    ax.plot(px.index, px[s], color=c, lw=lw, label=s)
    off = {"AXL": 6, "W": -4}.get(s, 0)
    ax.text(px.index[-1], px[s].iloc[-1] + off, f" {s} {px[s].iloc[-1]-100:+.0f}%", color=c, fontsize=8.5, va="center")
ax.axhline(100, color="#9aa5a0", lw=0.8, ls=":")
ax.set_ylabel("Indexed, Jan 1 2025 = 100")
ax.set_title("W fell with Axelar (-95%); ZRO held up better, so the gap is W-specific, not just sector beta")
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
foot(fig, SRC.format("Binance daily closes (WUSDT, ZROUSDT, AXLUSDT, BTCUSDT)"))
save(fig, "F11_relative_performance")

# ---------------------------------------------------------------- F12
# Average transfer size (quality of flow)
q = monthly.loc["2024-04-01":"2026-10-01"].copy()
q["avg"] = q.usd / q.n
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.bar(q.index, q["n"], width=22, color=GRAY, label="Transfers")
ax.set_ylabel("Transfers per month")
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1e3:,.0f}k"))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax2 = ax.twinx(); ax2.spines["right"].set_visible(True)
ax2.plot(q.index, q["avg"], color=GREEN, lw=2.2, label="Avg $ per transfer")
ax2.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax2.set_ylabel("Average transfer ($)")
ax.set_title("Since Aug 2026 transfer counts jumped 5x as average size fell: retail-sized flow arrived")
foot(fig, SRC.format("Wormholescan x-chain-activity/tops monthly volume and count"))
save(fig, "F12_transfer_size")

# ---------------------------------------------------------------- F13
# Valuation method sensitivity (their own method, updated inputs)
per_b_base = (1.05 + 3.62) / 2 * 1e6
supply_12m = 8.04e9
life_now = float(score["total_volume"])
cases = [("Report input: $70B lifetime", 70e9), (f"Wormholescan today: ${life_now/1e9:.1f}B", life_now),
         (f"+1 more year at trailing pace: ${(life_now+vol1y)/1e9:.1f}B", life_now + vol1y)]
fig, ax = plt.subplots(figsize=(8, 2.8))
vals = [per_b_base * v / 1e9 / supply_12m for _, v in cases]
ax.barh([c[0] for c in cases][::-1], vals[::-1], color=[GREEN, GRAY, GRAY])
for i, v in enumerate(vals[::-1]):
    ax.text(v + 0.0004, i, f"${v:.4f}  ({v/0.0109-1:+.0%})", va="center", fontsize=9)
ax.axvline(0.0109, color=RED, lw=1, ls="--"); ax.text(0.0109, 2.45, " today $0.0109", color=RED, fontsize=8)
ax.set_xlim(0, max(vals) * 1.3)
ax.set_title("Base-case target under the report's own method, with current lifetime volume")
foot(fig, "Method from report: ($2.335M of MC per $1B lifetime volume) x lifetime volume / 8.04B W. Volume: Wormholescan scorecards.")
save(fig, "F13_target_sensitivity")

# ---------------------------------------------------------------- F14
# Institutional RWA flow via Securitize app (honest check)
sec = app_m[app_m.app == "SECURITIZE"].set_index("date").usd.loc["2025-01-01":"2026-10-01"]
fig, ax = plt.subplots(figsize=(8, 2.8))
ax.bar(sec.index, sec.values, width=22, color=GREEN)
ax.yaxis.set_major_formatter(musd)
ax.set_title("Securitize-labelled flow is lumpy: $57M in Jul 2025, little since")
foot(fig, SRC.format("Wormholescan application-activity, app SECURITIZE. BUIDL/ACRED moves routed via other apps (e.g. NTT) are not in this series"))
save(fig, "F14_securitize_flow")

print(val.round(3).to_string())
print("obs bps", obs_bps, "need bps", need_bps, "unlock usd", unlock_usd)
