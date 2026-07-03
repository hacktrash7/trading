#!/usr/bin/env python3
"""Generate the monthly budget tracker Excel workbook."""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# Budget categories with June 2026 actuals and updated monthly targets
SALARY = 158853
PLUXEE_GROCERIES = 5600  # ₹4,400 + ₹1,200 corporate meal/grocery benefit
ZERODHA_TARGET = 120000

BUDGET_CATEGORIES = [
    ("Investments (Zerodha)", 71000, ZERODHA_TARGET, "Transfer ₹1.2L to Zerodha on 1st–2nd of month"),
    ("Rent (Somasundar)", 16000, 16000, "Monthly rent — pay on 1st of month via UPI"),
    ("Personal transfers", 2060, 0, "June: Rajat ₹1,100 + Govind ₹960 — budget only if recurring"),
    ("Credit card payment", 13180, 0, "No CC bills — pay everything via UPI/debit"),
    ("Pluxee — groceries (benefit)", 0, PLUXEE_GROCERIES, "₹4,400 + ₹1,200 loaded monthly; DMart/BigBasket only"),
    ("Groceries (from salary)", 2178, 0, "Use Pluxee first; salary only if Pluxee exhausted"),
    ("Restaurant dining", 5253, 2500, "Max 2 sit-down meals per month"),
    ("Street food / canteen", 3594, 2500, "Office lunch — use Infosys cafeteria when possible"),
    ("Desserts (Polar Bear etc.)", 924, 300, "Max 1 visit per month"),
    ("Office snacks / tea", 750, 300, "Carry flask; avoid daily ₹35 UPI"),
    ("Office cafe (Cowrks)", 598, 200, "Use only when necessary"),
    ("Transport (Metro)", 180, 200, "Already optimal"),
    ("Software subscriptions", 2376, 1500, "Cursor AI — review tier / annual plan"),
    ("Other subscriptions", 2, 200, "YouTube, streaming, etc."),
    ("Healthcare", 2290, 200, "One-time in June (Sparsh Hospital); keep small buffer only"),
    ("Education / training", 1875, 0, "Only if actively enrolled in a course"),
    ("Shopping (Amazon etc.)", 1842, 1000, "Non-essential purchases only"),
    ("Gift cards", 4240, 0, "Avoid prepaid unless planned gift"),
    ("Luxury / big purchases", 30867, 0, "No luxury spend — use 7-day rule if > ₹5,000"),
    ("Misc / buffer", 0, 2000, "Unexpected expenses from salary"),
]

JUNE_TRANSACTIONS = [
    ("01-Jun", "SOMASUNDAR", "Rent (Somasundar)", 16000, "Debit"),
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
    ("21-Jun", "Rajat Agarwal", "Personal transfers", 1100, "Debit"),
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

CATEGORIES = [c[0] for c in BUDGET_CATEGORIES] + ["Income", "Pluxee — groceries (benefit)", "Misc / buffer"]

# Salary-side spend targets (excludes Pluxee benefit)
SALARY_LIVING_TARGET = sum(
    target for cat, _, target, _ in BUDGET_CATEGORIES
    if cat not in ("Investments (Zerodha)", "Pluxee — groceries (benefit)", "Groceries (from salary)")
)
SALARY_OUTFLOW_TARGET = ZERODHA_TARGET + SALARY_LIVING_TARGET
SALARY_SURPLUS_TARGET = SALARY - SALARY_OUTFLOW_TARGET


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
    ws.cell(row=summary_row, column=1, value="Monthly salary (bank)").font = Font(bold=True)
    ws.cell(row=summary_row, column=3, value=SALARY).number_format = '#,##0'
    ws.cell(row=summary_row + 1, column=1, value="Pluxee grocery benefit (separate)").font = Font(bold=True)
    ws.cell(row=summary_row + 1, column=3, value=PLUXEE_GROCERIES).number_format = '#,##0'
    ws.cell(row=summary_row + 2, column=1, value="Zerodha investment target").font = Font(bold=True)
    ws.cell(row=summary_row + 2, column=3, value=ZERODHA_TARGET).number_format = '#,##0'
    ws.cell(row=summary_row + 3, column=1, value="Living spend from salary (target)").font = Font(bold=True)
    ws.cell(row=summary_row + 3, column=3, value=SALARY_LIVING_TARGET).number_format = '#,##0'
    ws.cell(row=summary_row + 4, column=1, value="Projected salary surplus (Salary − Actual spend)").font = Font(bold=True)
    ws.cell(row=summary_row + 4, column=4, value=f"=C{summary_row}-D{total_row}").number_format = '#,##0'
    ws.cell(row=summary_row + 5, column=1, value="Total to Zerodha + surplus wealth").font = Font(bold=True)
    ws.cell(row=summary_row + 5, column=3, value=f"=C{summary_row + 2}+C{summary_row + 4}").number_format = '#,##0'

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
    ws["A1"] = "Monthly Budget Dashboard — Updated Plan"
    ws["A1"].font = Font(size=16, bold=True)

    metrics = [
        ("", ""),
        ("Income", ""),
        ("Monthly salary (bank)", SALARY),
        ("Pluxee groceries (₹4,400 + ₹1,200)", PLUXEE_GROCERIES),
        ("Total monthly resources", SALARY + PLUXEE_GROCERIES),
        ("", ""),
        ("Fixed outflows (from salary)", ""),
        ("Zerodha investment", ZERODHA_TARGET),
        ("Rent (Somasundar)", 16000),
        ("Personal transfers", 0),
        ("Credit card", 0),
        ("", ""),
        ("Living budget (from salary only)", ""),
        ("Restaurants + street food + snacks", 5600),
        ("Transport + subscriptions", 1700),
        ("Healthcare + shopping + misc", 3200),
        ("Groceries from salary", 0),
        ("Total living from salary", SALARY_LIVING_TARGET),
        ("", ""),
        ("Projected salary surplus", SALARY_SURPLUS_TARGET),
        ("Total wealth building (Zerodha + surplus)", ZERODHA_TARGET + SALARY_SURPLUS_TARGET),
        ("Wealth rate (% of salary)", round((ZERODHA_TARGET + SALARY_SURPLUS_TARGET) / SALARY * 100, 1)),
        ("", ""),
        ("Rules", ""),
        ("Transfer ₹1.2L to Zerodha", "1st–2nd of month"),
        ("Use Pluxee for all groceries first", "DMart / BigBasket"),
        ("Max restaurant spend", 2500),
        ("Cooling-off for purchases > ₹5,000", "7 days"),
        ("No credit card bills", "UPI/debit only"),
    ]
    for i, (label, value) in enumerate(metrics, start=2):
        ws.cell(row=i, column=1, value=label)
        ws.cell(row=i, column=2, value=value)
        if isinstance(value, (int, float)) and abs(value) > 100:
            ws.cell(row=i, column=2).number_format = '#,##0'
        elif isinstance(value, float):
            ws.cell(row=i, column=2).number_format = '0.0'

    auto_width(ws, 2)


def build_monthly_plan_sheet(wb):
    ws = wb.create_sheet("Monthly Plan")
    ws["A1"] = "Next Month — Salary Allocation Plan"
    ws["A1"].font = Font(size=14, bold=True)

    plan = [
        ("Step", "Action", "Amount (₹)", "When", "From"),
        (1, "Transfer to Zerodha", ZERODHA_TARGET, "1st–2nd", "Salary"),
        (2, "Rent — Somasundar", 16000, "1st of month", "Salary"),
        (3, "Load Pluxee — groceries", PLUXEE_GROCERIES, "Auto/credited", "Employer benefit"),
        (4, "Restaurants (max 2 outings)", 2500, "Through month", "Salary"),
        (5, "Office lunch / street food", 2500, "Through month", "Salary"),
        (6, "Snacks + desserts + office cafe", 500, "Through month", "Salary"),
        (7, "Metro transport", 200, "Through month", "Salary"),
        (8, "Cursor AI + subscriptions", 1700, "Monthly", "Salary"),
        (9, "Healthcare / pharmacy (buffer only)", 200, "As needed — June was one-time", "Salary"),
        (10, "Shopping (non-essential)", 1000, "As needed", "Salary"),
        (11, "Misc / emergency buffer", 2000, "Reserve", "Salary"),
        (12, "Groceries", 0, "Use Pluxee only", "Pluxee"),
        ("", "SALARY OUTFLOW TOTAL", SALARY_OUTFLOW_TARGET, "", "Salary"),
        ("", "PROJECTED SALARY SURPLUS", SALARY_SURPLUS_TARGET, "Keep in bank / sweep FD", "Salary"),
        ("", "TOTAL WEALTH BUILDING", ZERODHA_TARGET + SALARY_SURPLUS_TARGET, "Zerodha + savings", ""),
    ]
    for row_idx, row_data in enumerate(plan, start=3):
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = THIN_BORDER
            if col_idx == 3 and isinstance(val, (int, float)) and val != "":
                cell.number_format = '#,##0'
            if row_idx == 3:
                cell.fill = HEADER_FILL
                cell.font = HEADER_FONT

    auto_width(ws, 5)


def main():
    wb = Workbook()
    build_budget_sheet(wb)
    build_log_sheet(wb)
    build_baseline_sheet(wb)
    build_dashboard_sheet(wb)
    build_monthly_plan_sheet(wb)
    out = "/workspace/budget-tracker/monthly_budget_tracker.xlsx"
    wb.save(out)
    print(f"Created {out}")


if __name__ == "__main__":
    main()
