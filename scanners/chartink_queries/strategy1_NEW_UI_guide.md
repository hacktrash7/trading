# Chartink Strategy 1 — NEW UI Instructions (2026)

Chartink changed their scanner. **You cannot paste the old AND query into the main box anymore.**

Tested live on https://chartink.com/screener/process — these are the fixes.

---

## Why everything showed error

| Mistake | Fix |
|---------|-----|
| Pasting into **Magic Filters** box | That box only accepts plain English, not code |
| Using `{nifty 200}` | Does NOT work — use segment dropdown OR `{46553}` |
| Pasting full AND string without copy icon | Paste button only works for **filters copied from another Chartink scan** |
| Leaving segment as **cash** | Must change to **nifty 200** |

---

## METHOD 1 — Build filters manually (100% works on new UI)

### Step 1: Open scanner
https://chartink.com/screener

### Step 2: Change universe
Click the blue text **`cash segment`** → select **`nifty 200`**

It should now say: `Stock passes all of the below filters in nifty 200 segment:`

### Step 3: Add filters one by one
Click the purple **`+`** button. Add each row below (all set to **Passes all / AND**):

| # | Left | Operator | Right |
|---|------|----------|-------|
| 1 | Latest Close | > | 50 |
| 2 | Latest Volume * Latest Close | > | 5000000 |
| 3 | Latest Close | > | Latest SMA( Close, 50 ) |
| 4 | Latest Close | > | Latest SMA( Close, 200 ) |
| 5 | Latest Close | > | 6 months ago Close |
| 6 | Latest Close | > | 1 year ago Close |
| 7 | Latest Close / 6 months ago Close / Latest Std( Close, 126 ) | > | 0 |
| 8 | Latest Close / 1 year ago Close / Latest Std( Close, 252 ) | > | 0 |

### Step 4: Run
Click **Run Scan** → you should see ~60-70 stocks.

### Step 5: Rank for top 30
Add a **column** (not filter):
```
( Latest Close / 6 months ago Close / Latest Std( Close, 126 ) + Latest Close / 1 year ago Close / Latest Std( Close, 252 ) ) / 2
```
Sort that column **highest first** → pick top 30.

---

## METHOD 2 — Copy an existing scan and edit

1. Open: https://chartink.com/screener/0-600-nifty-200
2. Click **Save Scan** → save a copy to your account
3. Change segment to nifty 200 if needed
4. Replace/add filters from the table above
5. Run Scan

---

## METHOD 3 — Verified paste format (advanced)

If you use the **copy filter icon** workflow or backend query, this is the **live-tested** format:

```
( {46553} ( latest close > 50 and latest volume * latest close > 5000000 and latest close > latest sma( close, 50 ) and latest close > latest sma( close, 200 ) and latest close > 6 months ago close and latest close > 1 year ago close and latest close / 6 months ago close / latest std( close, 126 ) > 0 and latest close / 1 year ago close / latest std( close, 252 ) > 0 ) )'
```

Notes:
- `{46553}` = Nifty 200 watchlist ID (not `{nifty 200}`)
- Use lowercase `and` not `AND`
- Wrap as `( {ID} ( conditions ) )`

**Do not paste this into Magic Filters.** Use Method 1 or copy from an existing scan.

---

## Regime check (Nifty 50)

```
( {33492} ( latest close > latest sma( close, 50 ) and latest close > latest sma( close, 200 ) ) )
```

`{33492}` = Nifty 50. Only run Strategy 1 when this passes (~19 stocks when tested).

---

## Magic Filters (optional shortcut)

In the top box, try plain English then click **Generate**:

```
nifty 200 stocks above 50 dma and 200 dma with price higher than 6 months ago and 1 year ago
```

Then review generated filters and click **Run Scan**. You may still need to add the Std momentum filters manually.
