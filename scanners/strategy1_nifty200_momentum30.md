# Strategy 1 — NIFTY 200 Momentum 30 (Rule-Based) Chart Scan Logic

Source: *Swing Trading Framework — Investors Way* (Strategy 1).

## Strategy Summary

| Item | Rule |
|------|------|
| Universe | NSE Nifty 200 only |
| Core signal | Volatility-adjusted 6M + 12M momentum, z-scored across universe |
| Portfolio (full) | Top 30 stocks, equal-weight, rebalance monthly (last trading day) |
| Portfolio (swing) | Top 5–10 stocks, rebalance every 2 weeks |
| Exit | Drop out of rank band at next rebalance; no per-trade stop required |
| Regime filter | Only deploy when Nifty 50 is above 50-DMA; optional cash exit if Nifty weekly close < 200-DMA |

## Scoring Formula (NSE / Report)

For each Nifty 200 stock on rebalance day:

1. **6M momentum ratio** = 6-month price return ÷ 6-month daily-return standard deviation  
2. **12M momentum ratio** = 12-month price return ÷ 12-month daily-return standard deviation  
3. **Z-score** each ratio across all Nifty 200 names  
4. **Combined score** = average(6M z-score, 12M z-score)  
5. **Rank** descending → hold top 30 (or top 5–10 for swing)

Trading-day windows (approx.):

- 6 months ≈ 126 sessions  
- 12 months ≈ 252 sessions  

## Chartink Workflow (3 Steps)

Chartink cannot rank by true cross-sectional z-score in a basic scan alone. Use this 3-step flow:

### Step 0 — Regime Check (manual, 30 seconds)

Before running any momentum scan:

- Nifty 50 daily chart: close **above 50-DMA** (required)  
- Nifty 50 weekly chart: close **above 200-DMA** (optional but reduces drawdown)  
- India VIX trending down or below 20 is preferred  

If Nifty is below 50-DMA → skip new momentum entries; hold cash or existing winners only.

### Step 1 — Scanner C Filter (eligibility)

Paste **Scanner C** from `chartink_queries/strategy1_momentum30.txt`.

This removes illiquid names, downtrends, and negative-momentum stocks.

### Step 2 — Sort by Combined Momentum Score

In Chartink screener results:

1. Add a **custom column** using **Combined Momentum Score** (see query file).  
2. Sort descending on that column.  
3. Take:
   - **Top 30** for full rule-based portfolio (monthly rebalance)  
   - **Top 5–10** for swing adaptation (bi-weekly rebalance)

### Step 3 — Chart Review (mandatory)

Do not buy scanner output blindly. Each name must pass:

1. Clean uptrend structure (higher highs / higher lows on daily)  
2. Not within 5 trading days of earnings / ex-dividend / major event  
3. ATR(14) as % of price between 1.5% and 5%  
4. 20-day avg daily turnover ≥ ₹5 crore (already in scanner)  

## Rebalance Calendar

| Variant | When to run scan | Action |
|---------|------------------|--------|
| Full (30 stocks) | Last trading day of each month | Replace names that fell out of top 30 |
| Swing (5–10 stocks) | Every 2 weeks (e.g. Sunday prep) | Replace names that fell out of top 5–10 |

## Scanner Queries

All copy-paste queries live in:

`scanners/chartink_queries/strategy1_momentum30.txt`

| Scanner | Purpose |
|---------|---------|
| **C — Momentum 30 Filter** | Nifty 200 eligibility + positive vol-adjusted momentum |
| **C-Sort — Combined Score** | Custom sort column for ranking |
| **C-Elite — Above Universe Avg** | Optional: keeps only above-average momentum vs Nifty 200 group |
| **R — Regime (Nifty 50)** | Confirms market in trend before deploying Strategy 1 |

## Exact Z-Score Ranking (Python)

For monthly rebalance matching NSE index methodology exactly, run:

```bash
pip install -r requirements.txt
python src/nifty200_momentum30_scan.py --top 30 --output results/momentum30.csv
```

Swing variant:

```bash
python src/nifty200_momentum30_scan.py --top 10 --output results/momentum10_swing.csv
```

## What “Right Stocks” Means for This Strategy

A stock is **right** for Strategy 1 when ALL of the following are true:

1. Member of Nifty 200  
2. Positive 6M and 12M price returns  
3. High volatility-adjusted momentum (top of z-score rank)  
4. Liquid (≥ ₹5 cr 20-day avg turnover)  
5. In a trending market regime (Nifty above 50-DMA)  
6. Passes manual chart quality check  

A stock is **wrong** (exit at rebalance) when:

- It drops out of the top 30 (or top 5–10 swing band)  
- Optional: Nifty weekly close breaks below 200-DMA → reduce/exit all longs  

## Notes

- Chartink `Std(close, N)` approximates daily-return volatility; for index-identical scores use the Python script.  
- Test scanner syntax on a known name (e.g. RELIANCE, HDFCBANK) before relying on alerts.  
- Chartink syntax evolves; adjust spacing/casing if a query fails to parse.
