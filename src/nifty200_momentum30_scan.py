"""
NIFTY 200 Momentum 30 scanner — NSE rule-based methodology.

Computes volatility-adjusted 6M/12M momentum ratios, z-scores them across the
Nifty 200 universe, and ranks stocks for monthly (top 30) or swing (top 5-10)
rebalance.

Educational use only. Not investment advice.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Nifty 200 constituent symbols (NSE, .NS suffix for yfinance).
# Update periodically from NSE; subset shown — script falls back to fetching index holdings.
NIFTY200_FALLBACK = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN",
    "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "BAJFINANCE", "ASIANPAINT", "MARUTI",
    "HCLTECH", "SUNPHARMA", "TITAN", "ULTRACEMCO", "WIPRO", "NTPC", "POWERGRID",
    "M&M", "TATAMOTORS", "ADANIENT", "ADANIPORTS", "COALINDIA", "ONGC", "JSWSTEEL",
    "TATASTEEL", "TECHM", "NESTLEIND", "BAJAJFINSV", "GRASIM", "HINDALCO", "CIPLA",
    "DRREDDY", "EICHERMOT", "BPCL", "DIVISLAB", "APOLLOHOSP", "BRITANNIA", "HEROMOTOCO",
    "INDUSINDBK", "SBILIFE", "TATACONSUM", "HDFCLIFE", "BAJAJ-AUTO", "PIDILITIND",
    "GODREJCP", "DABUR", "HAVELLS", "SIEMENS", "DLF", "VEDL", "GAIL", "IOC", "BANKBARODA",
    "PNB", "CANBK", "UNIONBANK", "IDFCFIRSTB", "FEDERALBNK", "AUBANK", "BANDHANBNK",
    "CHOLAFIN", "MUTHOOTFIN", "SHRIRAMFIN", "LICI", "IRFC", "RECLTD", "PFC", "NHPC",
    "SJVN", "TORNTPOWER", "CUMMINSIND", "ABB", "BEL", "HAL", "BHEL", "POLYCAB",
    "VOLTAS", "CROMPTON", "AMBUJACEM", "ACC", "SHREECEM", "RAMCOCEM", "JKCEMENT",
    "INDIGO", "IRCTC", "CONCOR", "ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "DMART",
    "TRENT", "PAGEIND", "MARICO", "COLPAL", "UBL", "VBL", "TATAPOWER", "ADANIGREEN",
    "ADANIPOWER", "JINDALSTEL", "SAIL", "NMDC", "MOIL", "NATIONALUM", "HINDZINC",
    "LUPIN", "BIOCON", "AUROPHARMA", "TORNTPHARM", "ALKEM", "MANKIND", "GLENMARK",
    "MAXHEALTH", "FORTIS", "LALPATHLAB", "METROPOLIS", "PERSISTENT", "COFORGE",
    "LTIM", "MPHASIS", "OFSS", "NAUKRI", "INDHOTEL", "JUBLFOOD", "DEVYANI", "WESTLIFE",
    "MOTHERSON", "BOSCHLTD", "MRF", "BALKRISIND", "EXIDEIND", "TVSMOTOR", "ASHOKLEY",
    "ESCORTS", "BHARATFORG", "ASTRAL", "SUPREMEIND", "KEI", "CGPOWER", "THERMAX",
    "AIAENG", "SCHAEFFLER", "TIMKEN", "SKFINDIA", "GRINDWELL", "CARBORUNIV",
]

PERIODS_6M = 126
PERIODS_12M = 252
MIN_HISTORY = PERIODS_12M + 5


@dataclass
class StockScore:
    symbol: str
    ret_6m: float
    ret_12m: float
    vol_6m: float
    vol_12m: float
    mr_6m: float
    mr_12m: float
    z_6m: float
    z_12m: float
    combined_z: float
    nms: float
    rank: int
    avg_turnover_cr: float | None


def load_universe(symbols_file: Path | None) -> list[str]:
    if symbols_file and symbols_file.exists():
        lines = symbols_file.read_text().strip().splitlines()
        return [s.strip().upper() for s in lines if s.strip() and not s.startswith("#")]
    return NIFTY200_FALLBACK


def fetch_prices(symbols: list[str], lookback_days: int = 400) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise SystemExit("Install dependencies: pip install -r requirements.txt") from exc

    tickers = [f"{s}.NS" for s in symbols]
    data = yf.download(
        tickers,
        period=f"{lookback_days}d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    return data


def daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().dropna()


def momentum_ratio(close: pd.Series, return_period: int, vol_period: int) -> tuple[float, float, float]:
    if len(close) < vol_period + 1:
        return np.nan, np.nan, np.nan

    ret = (close.iloc[-1] / close.iloc[-return_period - 1]) - 1
    rets = daily_returns(close.tail(vol_period + 1))
    vol = rets.std()
    if vol == 0 or np.isnan(vol):
        return ret, vol, np.nan
    return ret, vol, ret / vol


def zscore(series: pd.Series) -> pd.Series:
    mean = series.mean()
    std = series.std()
    if std == 0 or np.isnan(std):
        return pd.Series(0.0, index=series.index)
    return (series - mean) / std


def normalized_momentum_score(combined_z: float) -> float:
    """NSE transformation for positive/negative weighted average z-score."""
    if combined_z >= 0:
        return 1 + combined_z
    return 1 / (1 - combined_z)


def score_universe(
    price_data: pd.DataFrame,
    symbols: list[str],
    liquidity_min_cr: float = 5.0,
) -> list[StockScore]:
    rows: list[dict] = []

    multi = isinstance(price_data.columns, pd.MultiIndex)

    for sym in symbols:
        ticker = f"{sym}.NS"
        try:
            if multi:
                if ticker not in price_data.columns.get_level_values(0):
                    continue
                close = price_data[ticker]["Close"].dropna()
                volume = price_data[ticker]["Volume"].dropna()
            else:
                close = price_data["Close"].dropna()
                volume = price_data["Volume"].dropna()
        except (KeyError, TypeError):
            continue

        if len(close) < MIN_HISTORY:
            continue

        ret_6m, vol_6m, mr_6m = momentum_ratio(close, PERIODS_6M, PERIODS_6M)
        ret_12m, vol_12m, mr_12m = momentum_ratio(close, PERIODS_12M, PERIODS_12M)

        if any(np.isnan(x) for x in (mr_6m, mr_12m)):
            continue

        # Liquidity: 20-day avg daily turnover in ₹ crore
        turnover = (close.tail(20).values * volume.tail(20).values).mean() / 1e7
        if turnover < liquidity_min_cr:
            continue

        # Trend filter (report: works best above 50/200 DMA)
        sma50 = close.tail(50).mean()
        sma200 = close.tail(200).mean()
        if close.iloc[-1] <= sma50 or close.iloc[-1] <= sma200:
            continue

        rows.append({
            "symbol": sym,
            "ret_6m": ret_6m,
            "ret_12m": ret_12m,
            "vol_6m": vol_6m,
            "vol_12m": vol_12m,
            "mr_6m": mr_6m,
            "mr_12m": mr_12m,
            "avg_turnover_cr": turnover,
        })

    if not rows:
        return []

    df = pd.DataFrame(rows)
    df["z_6m"] = zscore(df["mr_6m"])
    df["z_12m"] = zscore(df["mr_12m"])
    df["combined_z"] = (df["z_6m"] + df["z_12m"]) / 2
    df["nms"] = df["combined_z"].apply(normalized_momentum_score)
    df = df.sort_values("combined_z", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    return [
        StockScore(
            symbol=r.symbol,
            ret_6m=r.ret_6m,
            ret_12m=r.ret_12m,
            vol_6m=r.vol_6m,
            vol_12m=r.vol_12m,
            mr_6m=r.mr_6m,
            mr_12m=r.mr_12m,
            z_6m=r.z_6m,
            z_12m=r.z_12m,
            combined_z=r.combined_z,
            nms=r.nms,
            rank=int(r.rank),
            avg_turnover_cr=r.avg_turnover_cr,
        )
        for r in df.itertuples()
    ]


def write_csv(scores: list[StockScore], path: Path, top: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = [s for s in scores if s.rank <= top]

    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank", "symbol", "combined_z", "nms", "z_6m", "z_12m",
            "ret_6m_pct", "ret_12m_pct", "mr_6m", "mr_12m", "avg_turnover_cr",
        ])
        for s in selected:
            writer.writerow([
                s.rank, s.symbol, f"{s.combined_z:.4f}", f"{s.nms:.4f}",
                f"{s.z_6m:.4f}", f"{s.z_12m:.4f}",
                f"{s.ret_6m * 100:.2f}", f"{s.ret_12m * 100:.2f}",
                f"{s.mr_6m:.4f}", f"{s.mr_12m:.4f}",
                f"{s.avg_turnover_cr:.2f}" if s.avg_turnover_cr else "",
            ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Nifty 200 Momentum 30 scanner")
    parser.add_argument("--top", type=int, default=30, help="Number of top stocks (30 full, 5-10 swing)")
    parser.add_argument("--output", type=Path, default=Path("results/momentum30.csv"))
    parser.add_argument("--symbols", type=Path, default=None, help="Optional Nifty 200 symbol list file")
    parser.add_argument("--liquidity-min-cr", type=float, default=5.0)
    args = parser.parse_args()

    symbols = load_universe(args.symbols)
    print(f"Scanning {len(symbols)} symbols...")
    prices = fetch_prices(symbols)
    scores = score_universe(prices, symbols, args.liquidity_min_cr)

    if not scores:
        print("No stocks passed filters. Check data connectivity or symbol list.")
        return

    write_csv(scores, args.output, args.top)

    print(f"\nNIFTY 200 Momentum 30 — Top {args.top} as of {datetime.now().strftime('%Y-%m-%d')}")
    print("-" * 72)
    for s in scores[: args.top]:
        print(
            f"{s.rank:>3}  {s.symbol:<12}  z={s.combined_z:>6.2f}  "
            f"6M={s.ret_6m * 100:>6.1f}%  12M={s.ret_12m * 100:>6.1f}%  "
            f"turnover=₹{s.avg_turnover_cr:.1f}cr"
        )
    print(f"\nSaved: {args.output}")


if __name__ == "__main__":
    main()
