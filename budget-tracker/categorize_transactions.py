#!/usr/bin/env python3
"""
Categorize ICICI/UPI bank transactions and summarize spending by category.

Usage (macOS — use python3, NOT python):
  python3 budget-tracker/categorize_transactions.py your_statement.csv
  ./budget-tracker/run_categorizer.sh your_statement.csv

From the repo root (trading-cursor-monthly-budget-tracker-bd1b):
  cd budget-tracker && python3 categorize_transactions.py ../your_statement.csv

CSV should have columns for description and amount (header names are flexible).
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

# Mirrors budget tracker categories
RULES = [
    (r"zerodha|indian cle|iccl", "Investments (Zerodha)"),
    (r"cc billpay|billpay|credit card", "Credit card payment"),
    (r"somasundar|rajat agar|b t govind|govind", "Family transfers"),
    (r"sparsh|hospital|medi|pharma", "Healthcare"),
    (r"centre for|course|training|udemy|coursera", "Education / training"),
    (r"dmart|avenue sup|bigbasket|innovative|grocer", "Groceries"),
    (r"munchzeste|chulha|truffles|tacobell|burger kin|tr enterpr|profile sa|restaurant", "Restaurant dining"),
    (r"polar bear|dessert|ice cream", "Desserts (Polar Bear etc.)"),
    (r"prakash|yeddula|swamy|najeeb|uttam saga|syed shabe|food corne|malnad|ali baba|muhammad|kanhu|manoj|abhishek|twisted|thatha tea|nexus|fgm|food", "Street food / canteen"),
    (r"cowrks", "Office cafe (Cowrks)"),
    (r"cursor|github|copilot|software|adobe", "Software subscriptions"),
    (r"youtube|netflix|spotify|prime video|hotstar", "Other subscriptions"),
    (r"bangalore metro|englishbmrc|bmrc", "Transport (Metro)"),
    (r"titan|luxury|watch|jewel", "Luxury / big purchases"),
    (r"amazon pay gift|gift card|giftc", "Gift cards"),
    (r"amazon|flipkart|myntra|shopping", "Shopping (Amazon etc.)"),
    (r"salary|johnson controls|neft.*salary", "Income"),
    (r"int\.pd|interest", "Income"),
]

TARGETS = {
    "Investments (Zerodha)": 55000,
    "Family transfers": 18060,
    "Credit card payment": 8000,
    "Groceries": 2000,
    "Restaurant dining": 3000,
    "Street food / canteen": 2500,
    "Desserts (Polar Bear etc.)": 300,
    "Office snacks / tea": 300,
    "Office cafe (Cowrks)": 200,
    "Transport (Metro)": 200,
    "Software subscriptions": 1500,
    "Other subscriptions": 200,
    "Healthcare": 2500,
    "Education / training": 2000,
    "Shopping (Amazon etc.)": 1000,
    "Gift cards": 0,
    "Luxury / big purchases": 2500,
    "Misc / buffer": 2000,
}


def categorize(description: str) -> str:
    text = description.lower()
    for pattern, category in RULES:
        if re.search(pattern, text):
            return category
    return "Misc / buffer"


def parse_amount(raw: str):
    cleaned = re.sub(r"[₹,\s]", "", str(raw))
    try:
        return float(cleaned)
    except ValueError:
        return None


def find_columns(row):
    keys = {k.lower().strip(): k for k in row}
    desc_key = next((keys[k] for k in keys if "remark" in k or "description" in k or "narration" in k or "particular" in k), None)
    amt_key = next((keys[k] for k in keys if "withdrawal" in k or "debit" in k or "amount" in k), None)
    date_key = next((keys[k] for k in keys if "date" in k), None)
    if desc_key is None:
        desc_key = list(row.keys())[1] if len(row) > 1 else list(row.keys())[0]
    return date_key, desc_key, amt_key


def load_transactions(path):
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_key, desc_key, amt_key = find_columns(row)
            desc = row.get(desc_key, "") if desc_key else ""
            amount = parse_amount(row.get(amt_key, "0") if amt_key else "0")
            if not desc or amount is None or amount <= 0:
                continue
            rows.append({
                "date": row.get(date_key, "") if date_key else "",
                "description": desc,
                "amount": amount,
                "category": categorize(desc),
            })
    return rows


def print_summary(transactions):
    totals = defaultdict(float)
    for t in transactions:
        if t["category"] != "Income":
            totals[t["category"]] += t["amount"]

    grand = sum(totals.values())
    print("\nSPENDING SUMMARY")
    print("=" * 72)
    print(f"{'Category':<32} {'Actual':>10} {'Target':>10} {'Variance':>10}  Status")
    print("-" * 72)

    for cat in sorted(totals, key=lambda c: -totals[c]):
        actual = totals[cat]
        target = TARGETS.get(cat, 0)
        variance = actual - target
        status = "OK" if variance <= 0 else "OVER"
        print(f"{cat:<32} {actual:>10,.0f} {target:>10,.0f} {variance:>+10,.0f}  {status}")

    print("-" * 72)
    print(f"{'TOTAL':<32} {grand:>10,.0f}")
    print(f"\nTransactions analyzed: {len(transactions)}")


def main():
    parser = argparse.ArgumentParser(description="Categorize bank transactions")
    parser.add_argument("csv_file", type=Path, help="Bank statement CSV export")
    parser.add_argument("--month", help="Filter by month (YYYY-MM)")
    args = parser.parse_args()

    if not args.csv_file.exists():
        raise SystemExit(
            "File not found: {}\n\n"
            "Tips:\n"
            "  • Use the full path to your CSV, e.g. ~/Downloads/statement.csv\n"
            "  • From repo root: python3 budget-tracker/categorize_transactions.py your_statement.csv\n"
            "  • On Mac, use python3 (not python — system python is 2.7)".format(args.csv_file)
        )

    txns = load_transactions(args.csv_file)
    if args.month:
        txns = [t for t in txns if args.month in t["date"]]

    print_summary(txns)


if __name__ == "__main__":
    main()
