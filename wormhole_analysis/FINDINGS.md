# Wormhole (W) — data analysis directions and evidence figures

Data pulled **Nov 10, 2026 (UTC)** from public APIs, because the Allium MCP server rejects
Academic-plan accounts ("API keys are not available on the academic plan"). Sources:
Wormholescan API, DeFiLlama API, Binance public market data, CoinGecko markets.
Raw responses are in `data/`, and `make_figures.py` regenerates every figure.
The **Allium Explorer SQL** at the end lets you replicate the key cuts on Allium itself, which is the
competition's sponsor data source.

> Research workspace, not report text. The team must verify the numbers and write the submission
> itself (the competition disqualifies AI-generated reports).

## Key numbers (snapshot)

| Metric | Value | Source |
|---|---|---|
| Lifetime volume | **$77.7B** (report says $70B) | Wormholescan scorecards |
| Trailing 1y volume | $17.1B | Wormholescan |
| 30d volume / 90d volume | $1.20B / $4.36B | Wormholescan |
| Lifetime messages | 1.21B | Wormholescan |
| Wormhole TVL | **$1.35B** (report says $3.0B) | Wormholescan; DeFiLlama Portal $1.34B |
| LayerZero V2 / CCIP / Axelar TVL | $16.4B / $1.84B / $0.13B | DeFiLlama |
| Portal fees, 1y / revenue | $330k / $0 | DeFiLlama |
| LayerZero fees, 1y / revenue | $2.33M / $3.39M | DeFiLlama |
| W price, MC, FDV, circulating | $0.0108, $72.7M, $107.9M, 6.74B | CoinGecko |
| ZRO MC / AXL MC | $591M / $45.1M | CoinGecko |

## The 15 analysis directions

Status: **Done** = figure built from public data. **Allium** = needs Allium Explorer (SQL below).

| # | Direction | Status | Result (one line) |
|---|---|---|---|
| 1 | Volume vs price divergence | Done, F01 | Monthly volume up 1.8x off the July 2026 low (Aug to Oct avg vs May to Jul avg) while W sat near its ATL. **Bullish core chart.** |
| 2 | Scope reconciliation (why dashboards say 0.17%) | Done, F02 | The Allium/LayerZero "0.17% share" is GMP-only ($22M). Wormhole's GMP app did $39M in 30d; all Wormhole volume was $1.20B (55x). **Rebuts the main bear stat.** |
| 3 | What drives volume (app mix) | Done, F03 | Portal bridge is shrinking; NEAR Omni Bridge (from Aug 2026, $413M in 30d) and NTT are the new engines. |
| 4 | Asset quality (memecoin claim) | Done, F04 | 97% of top-7 asset volume is SOL, ETH, USDC, USDT and HYPE. Rebuts "memecoin churn". Note: top-7 symbols only ($535M of $1.2B). |
| 5 | Chain-level traction / catalysts | Done, F05 | HyperEVM ($43M) + Unichain ($29M) in 30d: Hyperliquid/HYPE NTT routes are a real top-5 source. Supports the Elysium/HYPE catalyst. |
| 6 | NTT concentration and the "$170B on NTT" claim | Done, F06 | 201 NTT tokens, only 8 moved >$1M in 30d; WHYPE = 61% of NTT flow. The $170B figure is mostly USDT/USDC listings that move little via NTT. **Soften that claim.** |
| 7 | TVL comparison | Done, F07 | Wormhole $1.35B, not $3.0B; LayerZero V2 is $16.4B on DeFiLlama. **Figure 3 in the report should be replaced.** |
| 8 | Fee- and TVL-normalised valuation | Done, F08 | MC/1y fees: W 221x vs ZRO 253x vs AXL 815x (W is cheapest). MC/TVL: ZRO 0.036x, W 0.054x, AXL 0.34x. A better comp than lifetime volume, but no fees reach W today. |
| 9 | Value-accrual gap (break-even take rate) | Done, F09 | Observed fees are 0.19 bps of volume. Buying every unlocked W ($14.1M/yr) needs 8.3 bps, 43x current monetisation. **Most important bear figure: put it in Risks.** |
| 10 | Supply overhang | Done, F10 | 6.74B to 8.05B circulating by Nov 2027 (+19%) on the 50.41M biweekly schedule. Matches the report's 8.04B. |
| 11 | Relative performance vs peers | Done, F11 | Since Jan 2025: W -96%, AXL -95%, ZRO -72%, BTC -21%. W tracks Axelar, not LayerZero. |
| 12 | Flow quality: transfer size and count | Done, F12 | Since Aug 2026, transfers rose ~5x to ~300k/month while the average fell to ~$2.5k: retail-sized flow (Solana to NEAR). More usage, smaller tickets. |
| 13 | Price-target sensitivity (your own method) | Done, F13 | Using $77.7B instead of $70B gives a base case of $0.0226 (+107%); one more year at the trailing pace gives $0.0275 (+153%). Your target is conservative on its own logic. |
| 14 | Institutional RWA flow (Securitize) | Done, F14 | The Securitize-labelled app moved $57M in Jul 2025, $16M in Q4 2025 and ~0 in 2026. **Don't lean on BUIDL as usage volume**; frame it as distribution/partnership. |
| 15 | W Reserve, holder concentration, unlock-to-exchange flows | **Allium** | No public Reserve address. The public Solana RPC refuses largest-holder queries. Use Allium SQL (B, C below). |

## Suggested edits to the report (evidence-driven)

1. **Replace Figure 3 (TVL).** "$3.0B, largest of any bridge" doesn't match DeFiLlama or Wormholescan
   ($1.35B). Use F02 (scope reconciliation) or F01 (volume vs price divergence) instead: both are stronger and true.
2. **Update lifetime volume to $77.7B** (Wormholescan, Nov 10). That raises your base case (F13).
3. **Add F09 to Risks.** It quantifies "no revenue reaches the token" and makes the thesis-break condition concrete:
   watch for Reserve disclosures implying more than ~8 bps of capture.
4. **Add F08 as a second valuation lens.** On fees W screens cheapest of the three. That's a cleaner comp than
   lifetime volume, which includes 2022 Terra-era flow.
5. **Soften** "$170B of tokens on NTT" (F06) and "usage is institutional" (F14). The data shows the flow is
   SOL/USDC/ETH retail traffic plus NEAR Omni Bridge and Hyperliquid, which is still a good story.
6. The market-share sources in the report conflict (33% vs 20% vs 0.17%). F02 explains why: each
   measures a different product scope.

## Allium Explorer SQL to replicate (run in app.allium.so)

Confirm table and column names in Explorer's schema browser first; the names below follow Allium's
documented `crosschain.bridges` and `solana.assets` conventions but are **unverified**. Keep the
literal date filters so the queries stay within the 100-credit budget.

```sql
-- A. Wormhole vs peers, weekly bridge volume (replicates F02 scope on Allium)
SELECT date_trunc('week', block_timestamp) AS wk, project,
       SUM(usd_amount) AS usd, COUNT(*) AS transfers
FROM crosschain.bridges.transfers
WHERE block_timestamp >= '2026-08-01' AND block_timestamp < '2026-11-10'
  AND project IN ('wormhole', 'layerzero', 'chainlink_ccip', 'axelar')
GROUP BY 1, 2 ORDER BY 1, 2;

-- B. W token holder concentration on Solana (direction 15)
SELECT address, balance
FROM solana.assets.balances_latest
WHERE mint = '85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ'
ORDER BY balance DESC LIMIT 50;

-- C. W flows into exchange-labelled wallets around unlock dates (direction 15)
SELECT date_trunc('day', block_timestamp) AS d, SUM(amount) AS w_to_exchanges
FROM solana.assets.transfers t
JOIN common.identity.entities e ON e.address = t.to_address AND e.category = 'cex'
WHERE t.mint = '85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ'
  AND block_timestamp >= '2026-08-01' AND block_timestamp < '2026-11-10'
GROUP BY 1 ORDER BY 1;
```

## Caveats

- Wormholescan app labels overlap (GMP = MTT, CCTP = STABLE). Figures use non-overlapping apps, and the
  scorecard total includes unlabelled messages.
- DeFiLlama only begins LayerZero V2 TVL in mid-2026; its methodology counts OFT-locked supply.
- Fees are DeFiLlama's Portal accounting. Off-chain institutional contracts aren't visible.
- All values are a point-in-time snapshot; rerun `make_figures.py` after refreshing `data/` before submission.
