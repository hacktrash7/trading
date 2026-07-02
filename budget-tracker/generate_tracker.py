#!/usr/bin/env python3
"""Generate the monthly budget tracker Excel workbook."""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# Budget categories with June 2026 actuals and recommended targets
BUDGET_CATEGORIES = [
    ("Investments (Zerodha)", 71000, 55000, "Fixed monthly SIP; adjust based on liquidity needs"),
    ("Family transfers", 18060, 18060, "Fixed obligation — budget as non-negotiable"),
    ("Credit card payment", 13180, 8000, "Audit CC statement monthly; pay via UPI when possible"),
    ("Groceries", 2178, 2000, "DMart/BigBasket bulk orders"),
    ("Restaurant dining", 5253, 3000, "Max 2–3 sit-down meals per month"),
    ("Street food / canteen", 3594, 2500, "Office lunch alternatives"),
    ("Desserts (Polar Bear etc.)", 924, 300, "Max 1–2 visits per month"),
    ("Office snacks / tea", 750, 300, "Carry flask; use Infosys cafeteria"),
    ("Office cafe (Cowrks)", 598, 200, "Use only when necessary"),
    ("Transport (Metro)", 180, 200, "Already optimal"),
    ("Software subscriptions", 2376, 1500, "Cursor AI — review tier / annual plan"),
    ("Other subscriptions", 2, 200, "YouTube, streaming, etc."),
    ("Healthcare", 2290, 2500, "Variable; claim via corporate insurance"),
    ("Education / training", 1875, 2000, "Skill-building — keep if ROI-positive"),
    ("Shopping (Amazon etc.)", 1842, 1000, "Non-gift discretionary purchases"),
    ("Gift cards", 4240, 0, "Avoid prepaid unless planned gift"),
    ("Luxury / big purchases", 30867, 2500, "Sinking fund: max ₹2,500/month accrual"),
    ("Misc / buffer", 0, 2000, "Unexpected expenses"),
]

JUNE_TRANSACTIONS = [
    ("01-Jun", "SOMASUNDAR", "Family transfers", 16000, "Debit"),
    ("01-Jun", "Sparsh Hospital", "Healthcare", 2290, "Debit"),
    ("01-Jun", "Zerodha (net)", "Investments (Zerodha)", 71000, "Debit"),
    ("01-Jun", "CC Bill Payment", "Credit card payment", 13180, "Debit"),
    ("01-Jun", "Centre for", "Education / training", 1875, "Debit"),
    ("03-Jun", "DMart", "Groceries", 911, "Debit"),
    ("07-Jun", "Munchzeste", "Restaurant dining", 1125, "Debit"),
    ("10-Jun", "TR Enterprise", "Restaurant dining", 1070, "Debit"),
    ("15-Jun", "Cursor AI", "Software subscriptions", 2376, "Debit"),
    ("17-Jun", "Amazon gift card", "Gift cards", 4240, "Debit"),
    ("21-Jun", "Chulha Cha", "Restaurant dining", 1180, "Debit"),
    ("21-Jun", "Rajat Agarwal", "Family transfers", 1100, "Debit"),
    ("28-Jun", "Titan", "Luxury / big purchases", 30867, "Debit"),
    ("28-Jun", "Truffles", "Restaurant dining", 1155, "Debit"),
    ("28-Jun", "FGM", "Shopping (Amazon etc.)", 1502, "Debit"),
    ("30-Jun", "Salary — Johnson Controls", "Income", 158853, "Credit"),
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
GREEN_FILL = PatternFill("solid", fgColor="C6EFCE")
RED_FILL = PatternFill("solid", fgColor="FFC7CE")
YELLOW_FILL = PatternFill("solid", fgColor="FFEB9C")
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

CATEGORIES = [c[0] for c in BUDGET_CATEGORIES] + ["Income", "Misc / buffer"]


def style_header(ws, row, cols):
    for col in range(1, cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER


def auto_width(ws, max_col):
    for col in range(1, max_col + 1):
        letter = get_column_letter(col)
        max_len = 0
        for row in ws[letter]:
            if row.value:
                max_len = max(max_len, len(str(row.value)))
        ws.column_dimensions[letter].width = min(max_len + 3, 45)


def build_budget_sheet(wb):
    ws = wb.active
    ws.title = "Budget vs Actual"
    headers = ["Category", "June Actual (₹)", "Monthly Target (₹)", "Your Spend (₹)", "Variance (₹)", "Status", "Notes"]
    ws.append(headers)
    style_header(ws, 1, len(headers))

    for i, (cat, actual, target, notes) in enumerate(BUDGET_CATEGORIES, start=2):
        ws.cell(row=i, column=1, value=cat)
        ws.cell(row=i, column=2, value=actual)
        ws.cell(row=i, column=3, value=target)
        ws.cell(row=i, column=4, value=0)
        ws.cell(row=i, column=5, value=f"=D{i}-C{i}")
        ws.cell(row=i, column=6, value=f'=IF(D{i}=0,"Enter spend",IF(E{i}<=0,"✓ On track","⚠ Over"))')
        ws.cell(row=i, column=7, value=notes)
        for col in range(1, 8):
            ws.cell(row=i, column=col).border = THIN_BORDER
            if col in (2, 3, 4, 5):
                ws.cell(row=i, column=col).number_format = '#,##0'

    total_row = len(BUDGET_CATEGORIES) + 2
    ws.cell(row=total_row, column=1, value="TOTAL (excl. income)").font = Font(bold=True)
    ws.cell(row=total_row, column=2, value=f"=SUM(B2:B{total_row - 1})").number_format = '#,##0'
    ws.cell(row=total_row, column=3, value=f"=SUM(C2:C{total_row - 1})").number_format = '#,##0'
    ws.cell(row=total_row, column=4, value=f"=SUM(D2:D{total_row - 1})").number_format = '#,##0'
    ws.cell(row=total_row, column=5, value=f"=D{total_row}-C{total_row}").number_format = '#,##0'

    summary_row = total_row + 2
    ws.cell(row=summary_row, column=1, value="Monthly salary (target income)").font = Font(bold=True)
    ws.cell(row=summary_row, column=3, value=158853).number_format = '#,##0'
    ws.cell(row=summary_row + 1, column=1, value="Projected surplus (Income − Actual spend)").font = Font(bold=True)
    ws.cell(row=summary_row + 1, column=4, value=f"=C{summary_row}-D{total_row}").number_format = '#,##0'
    ws.cell(row=summary_row + 2, column=1, value="Savings rate (%)").font = Font(bold=True)
    ws.cell(row=summary_row + 2, column=4, value=f"=IF(C{summary_row}>0,D{summary_row + 1}/C{summary_row},0)").number_format = '0.0%'

    ws.freeze_panes = "A2"
    auto_width(ws, 7)


def build_log_sheet(wb):
    ws = wb.create_sheet("Transaction Log")
    headers = ["Date", "Description", "Category", "Amount (₹)", "Type", "Month", "Notes"]
    ws.append(headers)
    style_header(ws, 1, len(headers))

    dv = DataValidation(type="list", formula1=f'"{",".join(CATEGORIES)}"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"C2:C500")

    type_dv = DataValidation(type="list", formula1='"Debit,Credit"', allow_blank=True)
    ws.add_data_validation(type_dv)
    type_dv.add("E2:E500")

    for row in range(2, 52):
        ws.cell(row=row, column=6, value=f'=IF(A{row}="","",TEXT(A{row},"MMM-YYYY"))')

    ws.freeze_panes = "A2"
    auto_width(ws, 7)


def build_baseline_sheet(wb):
    ws = wb.create_sheet("June 2026 Baseline")
    headers = ["Date", "Description", "Category", "Amount (₹)", "Type"]
    ws.append(headers)
    style_header(ws, 1, len(headers))

    for txn in JUNE_TRANSACTIONS:
        ws.append(list(txn))
        row = ws.max_row
        for col in (4,):
            ws.cell(row=row, column=col).number_format = '#,##0'

    ws.freeze_panes = "A2"
    auto_width(ws, 5)


def build_dashboard_sheet(wb):
    ws = wb.create_sheet("Dashboard")
    ws["A1"] = "Monthly Budget Dashboard"
    ws["A1"].font = Font(size=16, bold=True)

    metrics = [
        ("", ""),
        ("Key targets (based on June 2026 analysis)", ""),
        ("Monthly salary", 158853),
        ("Target living expenses", 53113),
        ("Target investments", 55000),
        ("Target family transfers", 18060),
        ("Target projected surplus", 32780),
        ("", ""),
        ("Rules of thumb", ""),
        ("Max restaurant spend", 3000),
        ("Max luxury accrual", 2500),
        ("Cooling-off period for purchases > ₹5,000", "7 days"),
        ("Credit card bill cap", 8000),
    ]
    for i, (label, value) in enumerate(metrics, start=2):
        ws.cell(row=i, column=1, value=label)
        ws.cell(row=i, column=2, value=value)
        if isinstance(value, (int, float)) and value > 100:
            ws.cell(row=i, column=2).number_format = '#,##0'

    auto_width(ws, 2)


def main():
    wb = Workbook()
    build_budget_sheet(wb)
    build_log_sheet(wb)
    build_baseline_sheet(wb)
    build_dashboard_sheet(wb)
    out = "/workspace/budget-tracker/monthly_budget_tracker.xlsx"
    wb.save(out)
    print(f"Created {out}")


if __name__ == "__main__":
    main()
