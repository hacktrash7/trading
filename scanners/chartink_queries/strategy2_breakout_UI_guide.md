# Breakout Scan — Chartink UI Build Guide

For stocks that **broke out 1–2 days ago** OR are **within 3% of 52-week high**, while filtering **false breakouts**.

---

## Step 1 — Universe

1. Open https://chartink.com/screener
2. Click **`cash segment`** → select **`nifty 500`** (best for breakouts) or **`nifty 200`**

---

## Step 2 — Base filters (add with `+`, all AND)

| # | Left | Op | Right |
|---|------|----|-------|
| 1 | Latest Close | > | 50 |
| 2 | Latest Volume × Latest Close | > | 5000000 |
| 3 | Latest Close | > | SMA(Close, 50) |
| 4 | Latest Close | > | SMA(Close, 200) |
| 5 | SMA(Close, 50) | > | SMA(Close, 200) |

---

## Step 3 — Breakout timing (add a GROUP with **Passes Any** = OR)

Create a **sub-group** set to **Passes Any**, then add 3 sub-filters:

### A) Broke out yesterday
| Left | Op | Right |
|------|----|-------|
| 1 day ago High | > | 1 week ago Max(52, High) |
| 2 days ago High | <= | 2 weeks ago Max(52, High) |

### B) Broke out 2 days ago
| Left | Op | Right |
|------|----|-------|
| 2 days ago High | > | 2 weeks ago Max(52, High) |
| 3 days ago High | <= | 3 weeks ago Max(52, High) |

### C) Near breakout (within 3%, not broken yet)
| Left | Op | Right |
|------|----|-------|
| Latest Close | > | Max(52, High) × 0.97 |
| Latest Close | < | Max(52, High) |

---

## Step 4 — Anti false-breakout filters (all AND)

| # | Left | Op | Right | Why |
|---|------|----|-------|-----|
| 6 | Latest Close | > | 1 day ago Low | No sharp reversal |
| 7 | Latest Close | >= | 1 day ago Close × 0.98 | Holding gains |
| 8 | Latest Low | > | Max(52, High) × 0.95 | Not back in base |
| 9 | Latest Close | > | SMA(Close, 20) | Short trend intact |

---

## Step 5 — Optional strict volume (Scan B)

Add **one** of these (Passes Any):

| Left | Op | Right |
|------|----|-------|
| 1 day ago Volume | > | 1 day ago SMA(Volume, 50) × 1.5 |
| 2 days ago Volume | > | 2 days ago SMA(Volume, 50) × 1.5 |
| Latest Volume | > | SMA(Volume, 50) × 1.5 |

---

## Step 6 — Run Scan

- **Standard (Step 1–4):** ~40–50 names on Nifty 500
- **Strict (+ Step 5):** ~10–15 names, fewer fakes

---

## After scan — manual filter (5 min per stock)

Only trade names where:
- Breakout level is a **clean horizontal** resistance (touched 2+ times)
- Base was **tight** 3–8 weeks (not wide/loose)
- Volume **spiked** on breakout day visually
- No earnings within **5 days**
- Stop below breakout candle low or last swing low

**Skip** if price gapped down >3% after breakout or volume died for 2+ days.
