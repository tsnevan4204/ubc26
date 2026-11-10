"""Clean versions of the four headline figures, styled to match the report.

Run from wormhole_analysis/: python3 make_clean_figures.py
Output: figures/clean/*.png
"""
import json
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import pandas as pd

D = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "figures" / "clean"
OUT.mkdir(parents=True, exist_ok=True)

GREEN, GRAY, INK, MUTED = "#1fae7a", "#cdd5d1", "#1c2622", "#6b7772"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "text.color": INK,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.edgecolor": GRAY, "xtick.major.size": 0, "ytick.major.size": 0,
    "text.parse_math": False, "savefig.dpi": 220, "savefig.bbox": "tight",
})


from matplotlib.transforms import offset_copy


def header(fig, n, title):
    top = fig.subplotpars.top
    t = fig.transFigure
    fig.text(0.0, top, title, fontsize=11.5, weight="bold", transform=offset_copy(t, fig=fig, y=22, units="points"))
    fig.text(0.0, top, f"FIGURE {n}", color=GREEN, fontsize=8, family="DejaVu Sans Mono", weight="bold",
             transform=offset_copy(t, fig=fig, y=40, units="points"))


def source(fig, text, y=-0.04):
    fig.text(0.0, y, text, fontsize=7.5, color=MUTED)


def hbars(ax, labels, vals, colors, fmt):
    ax.barh(labels, vals, color=colors, height=0.6)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.015, i, fmt(v), va="center", fontsize=9)
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.invert_yaxis()


# ---- Figure 1: monthly volume and W price
m = pd.read_csv(D / "xchain_tops_monthly.csv", parse_dates=["date"]).set_index("date").loc["2025-01-01":"2026-10-01"]
k = pd.DataFrame(json.load(open(D / "kl_WUSDT.json"))).iloc[:, [0, 4]]
k.columns = ["t", "c"]
k = k.assign(date=pd.to_datetime(k.t, unit="ms"), c=k.c.astype(float)).set_index("date").c.loc["2025-01-01":"2026-10-31"]

fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 4.2), sharex=True, gridspec_kw=dict(height_ratios=[1.6, 1], hspace=0.25))
fig.subplots_adjust(left=0.13)
a1.bar(m.index, m.usd, width=20, color=[GREEN if d >= pd.Timestamp("2026-07-01") else GRAY for d in m.index])
a1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v/1e9:.1f}B"))
a1.set_ylabel("Monthly volume")
a1.grid(axis="y", color="#edf1ef"); a1.set_axisbelow(True)
a2.plot(k.index, k.values, color=INK, lw=1.4)
a2.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:.2f}"))
a2.set_ylabel("W price")
a2.grid(axis="y", color="#edf1ef")
a2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
a2.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
header(fig, 1, "Wormhole monthly volume and W price, 2025 to 2026")
source(fig, "Volume has risen since July 2026 (green) while W stayed near its low. "
            "Source: Wormholescan, Binance. Nov 10, 2026.", y=0.0)
fig.savefig(OUT / "fig1_volume_vs_price.png", facecolor="white"); plt.close(fig)

# ---- Figure 2: 30-day volume by measurement scope
app = pd.read_csv(D / "app_daily.csv", parse_dates=["date"])
by = app[(app.date >= "2026-10-10") & (app.date <= "2026-11-09")].groupby("app").usd.sum()
total = float(json.load(open(D / "scorecards.json"))["30d_volume"])
rows = [("GMP only (Allium x LayerZero dashboard)", 21.89e6), ("Portal token bridge", by["PORTAL_TOKEN_BRIDGE"]),
        ("Native Token Transfers", by["NATIVE_TOKEN_TRANSFER"]), ("NEAR Omni Bridge", by["OMNI_BRIDGE"]),
        ("All Wormhole transfers", total)]
fig, ax = plt.subplots(figsize=(7, 2.6))
fig.subplots_adjust(left=0.43)
hbars(ax, [r[0] for r in rows], [r[1] for r in rows], [GRAY] * 4 + [GREEN], lambda v: f"${v/1e6:,.0f}M")
header(fig, 2, "Wormhole 30-day volume by measurement scope")
source(fig, "Oct 10 to Nov 9, 2026. Source: Wormholescan; digital-asset-interoperability.com (undated snapshot).")
fig.savefig(OUT / "fig2_scope.png", facecolor="white"); plt.close(fig)

# ---- Figure 3: market cap / annual fees
cg = {c["id"]: c for c in json.load(open(D / "cg_markets.json"))}
fees = {k_: json.load(open(D / f"fees_{f}.json"))["total1y"] for k_, f in [("W", "portal"), ("ZRO", "layerzero"), ("AXL", "axelar")]}
mult = {"Wormhole (W)": cg["wormhole"]["market_cap"] / fees["W"],
        "LayerZero (ZRO)": cg["layerzero"]["market_cap"] / fees["ZRO"],
        "Axelar (AXL)": cg["axelar"]["market_cap"] / fees["AXL"]}
fig, ax = plt.subplots(figsize=(7, 1.9))
fig.subplots_adjust(left=0.2)
hbars(ax, list(mult), list(mult.values()), [GREEN, GRAY, GRAY], lambda v: f"{v:.0f}x")
header(fig, 3, "Market cap per dollar of annual protocol fees")
source(fig, "Lower is cheaper. Circulating market cap / trailing 365-day fees. Source: CoinGecko, DeFiLlama. Nov 10, 2026.", y=-0.08)
fig.savefig(OUT / "fig3_mc_to_fees.png", facecolor="white"); plt.close(fig)

# ---- Figure 4: what moves over Wormhole, and from where
s = pd.read_csv(D / "top_symbols_30d.csv")
cls = {"SOL": "SOL and ETH", "WETH": "SOL and ETH", "USDC": "Stablecoins", "USDT": "Stablecoins",
       "WHYPE": "HYPE", "hype": "HYPE"}
g = s.assign(c=s.symbol.map(cls).fillna("Other")).groupby("c").volume.sum().reindex(["SOL and ETH", "Stablecoins", "HYPE", "Other"])
xd = pd.read_csv(D / "xchain_daily_by_chain.csv", parse_dates=["date"])
CH = {1: "Solana", 15: "NEAR", 2: "Ethereum", 47: "HyperEVM", 44: "Unichain", 23: "Arbitrum"}
c30 = xd[xd.date >= "2026-10-10"].groupby("emitter_chain").usd.sum().sort_values(ascending=False).head(6)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 2.5), gridspec_kw=dict(wspace=0.55))
fig.subplots_adjust(left=0.13)
hbars(a1, list(g.index), list(g.values), [GRAY, GRAY, GREEN, GRAY], lambda v: f"{v/g.sum():.0%}")
a1.set_title("By asset (top 7 symbols)", loc="left", fontsize=9.5, color=MUTED, pad=4)
names = [CH.get(i, str(i)) for i in c30.index]
hbars(a2, names, list(c30.values), [GREEN if n in ("HyperEVM", "Unichain") else GRAY for n in names], lambda v: f"${v/1e6:,.0f}M")
a2.set_title("By source chain", loc="left", fontsize=9.5, color=MUTED, pad=4)
header(fig, 4, "What moved over Wormhole in the last 30 days")
source(fig, "Hyperliquid-related flow in green. Oct 10 to Nov 9, 2026. Source: Wormholescan.")
fig.savefig(OUT / "fig4_flow_mix.png", facecolor="white"); plt.close(fig)
print("done")
