#!/usr/bin/env python3
"""
Categorize bank/UPI transactions and summarize spending by category.

Usage (macOS — use python3, NOT python):
  python3 budget-tracker/categorize_transactions.py your_statement.csv
  ./budget-tracker/run_categorizer.sh your_statement.csv

Never commit real bank CSV exports to a public repository.
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

try:
    from local_config import RENT_PATTERN  # type: ignore
except ImportError:
    RENT_PATTERN = r"rent|landlord|lease"

# Generic merchant patterns only — no personal names or UPI handles
RULES = [
    (r"zerodha|iccl|broking", "Investments (Zerodha)"),
    (r"cc billpay|billpay|credit card", "Credit card payment"),
    (RENT_PATTERN, "Rent"),
    (r"salary|neft.*salary|payroll", "Income"),
    (r"int\.pd|interest", "Income"),
    (r"hospital|clinic|pharma|medi", "Healthcare"),
    (r"course|training|udemy|coursera", "Education / training"),
    (r"dmart|avenue sup|bigbasket|grocery|supermarket|innovative", "Groceries"),
    (r"restaurant|dine|bistro|cafe", "Restaurant dining"),
    (r"dessert|ice cream", "Desserts"),
    (r"canteen|food court|food", "Street food / canteen"),
    (r"cursor|github|copilot|software|adobe", "Software subscriptions"),
    (r"youtube|netflix|spotify|prime video|hotstar", "Other subscriptions"),
    (r"metro|bmrc|transport", "Transport (Metro)"),
    (r"luxury|watch|jewel|titan", "Luxury / big purchases"),
    (r"gift card|giftc", "Gift cards"),
    (r"amazon|flipkart|myntra|shopping", "Shopping (online)"),
]

try:
    from config import PLUXEE_GROCERIES, RENT_TARGET, ZERODHA_TARGET
except ImportError:
    PLUXEE_GROCERIES = 5000
    RENT_TARGET = 15000
    ZERODHA_TARGET = 100000

TARGETS = {
    "Investments (Zerodha)": ZERODHA_TARGET,
    "Rent": RENT_TARGET,
    "Personal transfers": 0,
    "Credit card payment": 0,
    "Pluxee — groceries (benefit)": PLUXEE_GROCERIES,
    "Groceries (from salary)": 0,
    "Groceries": 0,
    "Weekend expenses": 2000,
    "Restaurant dining (weekdays)": 500,
    "Restaurant dining": 500,
    "Street food / canteen (weekdays)": 2500,
    "Street food / canteen": 2500,
    "Desserts": 300,
    "Office snacks / tea": 300,
    "Office cafe": 200,
    "Transport (Metro)": 200,
    "Software subscriptions": 1500,
    "Other subscriptions": 200,
    "Healthcare": 200,
    "Education / training": 0,
    "Shopping (online)": 1000,
    "Gift cards": 0,
    "Luxury / big purchases": 0,
    "Misc / buffer": 2000,
}


def categorize(description):
    text = description.lower()
    for pattern, category in RULES:
        if re.search(pattern, text):
            return category
    return "Misc / buffer"


def parse_amount(raw):
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
    print("{:<32} {:>10} {:>10} {:>10}  {}".format(
        "Category", "Actual", "Target", "Variance", "Status"))
    print("-" * 72)

    for cat in sorted(totals, key=lambda c: -totals[c]):
        actual = totals[cat]
        target = TARGETS.get(cat, 0)
        variance = actual - target
        status = "OK" if variance <= 0 else "OVER"
        print("{:<32} {:>10,.0f} {:>10,.0f} {:>+10,.0f}  {}".format(
            cat, actual, target, variance, status))

    print("-" * 72)
    print("{:<32} {:>10,.0f}".format("TOTAL", grand))
    print("\nTransactions analyzed: {}".format(len(transactions)))


def main():
    parser = argparse.ArgumentParser(description="Categorize bank transactions")
    parser.add_argument("csv_file", type=Path, help="Bank statement CSV export (keep local, do not commit)")
    parser.add_argument("--month", help="Filter by month (YYYY-MM)")
    args = parser.parse_args()

    if not args.csv_file.exists():
        raise SystemExit(
            "File not found: {}\n\n"
            "Tips:\n"
            "  • Use the full path to your CSV, e.g. ~/Downloads/statement.csv\n"
            "  • From repo root: python3 budget-tracker/categorize_transactions.py your_statement.csv\n"
            "  • On Mac, use python3 (not python — system python is 2.7)\n"
            "  • Never commit real bank CSVs to a public repo".format(args.csv_file)
        )

    txns = load_transactions(args.csv_file)
    if args.month:
        txns = [t for t in txns if args.month in t["date"]]

    print_summary(txns)


if __name__ == "__main__":
    main()
