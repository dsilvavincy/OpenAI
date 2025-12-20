"""Generates HTML reports for the T12 Property Analysis Tool.

This class is responsible for creating visually rich, data-driven HTML tables
derived from the processed financial data. It handles:
1.  Merged KPI Table (Current Month + YTD)
2.  Financial Data Table (Monthly view with conditional formatting)
3.  Portfolio Snapshot Table (from 'Internal' sheet with custom arrow logic)
"""

import pandas as pd
import numpy as np

class ReportGenerator:
    """Generates HTML components for the AI analysis report."""
    
    def __init__(self):
        # CSS Styles for Tables
        self.css_styles = """
        <style>
            .report-table {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 25px;
                font-size: 0.9em;
                background-color: #262730; /* Force dark background matches visual */
                color: #ffffff !important; /* Force pure white text */
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
            }
            .report-table thead tr {
                background-color: #009879;
                color: #ffffff;
                text-align: left;
            }
            .report-table th, .report-table td {
                padding: 12px 15px;
                border: 1px solid #444;
            }
            .report-table tbody tr {
                border-bottom: 1px solid #444;
            }
            
            .report-table tbody tr:last-of-type {
                border-bottom: 2px solid #009879;
            }
            
            /* High Contrast Status Colors */
            .val-green { background-color: #1e4620 !important; color: #a3e6b1 !important; font-weight: bold; }
            .val-yellow { background-color: #4d3e04 !important; color: #fdf2ce !important; font-weight: bold; }
            .val-red { background-color: #5a1a1e !important; color: #f8d7da !important; font-weight: bold; }
            
            /* Arrow Colors - Brightened for Dark Mode */
            .arrow-up { color: #4cd137 !important; font-weight: bold; }   
            .arrow-side { color: #fbc531 !important; font-weight: bold; } 
            .arrow-down { color: #e84118 !important; font-weight: bold; } 
            
            .metric-header { font-weight: bold; color: #ffffff !important; }
        </style>
        """

    def generate_combined_kpi_table(self, monthly_kpi: dict, ytd_kpi: dict, mom_changes: dict = None) -> str:
        """Creates the merged Monthly + YTD KPI table.
        Refines names as requested:
        - Net Eff. Gross Income -> Total Monthly Income
        - Total Expense -> Total Monthly Expenses
        - EBITDA -> Monthly Net Operating Income
        - Adds: Monthly Expense Ratio
        - Adds: MoM Income/Expense Changes
        - Removes: Delinquency Rate
        """
        # Define the row mapping: (Original Key -> Display Name)
        # Note: Keys are converted to snake_case by PropertyAnalyzer
        rows_to_display = [
            ("net_eff_gross_income", "Total Monthly Income"),
            ("total_expense", "Total Monthly Expenses"),
            ("ebitda_noi", "Net Operating Income (EBITDA)")
        ]
        
        html = f"{self.css_styles}\n"
        html += """<table class='report-table'>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Current Month</th>
                    <th>YTD (Cumulative)</th>
                </tr>
            </thead>
            <tbody>"""
            
        # 1. Standard Metrics
        for snake_key, display_name in rows_to_display:
            val_mo = monthly_kpi.get(snake_key, 0)
            val_ytd = ytd_kpi.get(snake_key, 0)
            
            # Format currency
            fmt_mo = f"${val_mo:,.0f}" if isinstance(val_mo, (int, float)) else str(val_mo)
            fmt_ytd = f"${val_ytd:,.0f}" if isinstance(val_ytd, (int, float)) else str(val_ytd)
            
            html += f"<tr><td class='metric-header'>{display_name}</td><td>{fmt_mo}</td><td>{fmt_ytd}</td></tr>"

        # 2. Add Expense Ratio (Expenses / Income)
        # Calculate Monthly
        inc_mo = monthly_kpi.get("net_eff_gross_income", 0)
        exp_mo = monthly_kpi.get("total_expense", 0)
        ratio_mo = (exp_mo / inc_mo) if inc_mo and inc_mo != 0 else 0
        
        # Calculate YTD
        inc_ytd = ytd_kpi.get("net_eff_gross_income", 0)
        exp_ytd = ytd_kpi.get("total_expense", 0)
        ratio_ytd = (exp_ytd / inc_ytd) if inc_ytd and inc_ytd != 0 else 0
        
        # Format as percentage
        html += f"""
            <tr>
                <td class='metric-header'>Monthly Expense Ratio</td>
                <td>{ratio_mo:.1%}</td>
                <td>{ratio_ytd:.1%}</td>
            </tr>
        """
        
        # 3. Add MoM Changes (Income and Expense)
        # mom_changes structure: {'income_pct': float, 'expense_pct': float, 'income_abs': float, 'expense_abs': float}
        if mom_changes:
             # Income Change
             # Backend sends: mom_changes['net_eff_gross_income'] = {'change_pct': ..., 'change_abs': ...}
             inc_data = mom_changes.get('net_eff_gross_income', {})
             inc_pct = inc_data.get('change_pct', 0)
             inc_abs = inc_data.get('change_abs', 0)
             
             inc_color = "val-green" if inc_pct >= 0 else "val-red"
             inc_arrow = "▲" if inc_pct >= 0 else "▼"
             
             html += f"<tr><td class='metric-header'>MoM Income Change</td><td class='{inc_color}'>{inc_arrow} {inc_pct:+.1f}% (${inc_abs:,.0f})</td><td>-</td></tr>"
             
             # Expense Change
             exp_data = mom_changes.get('total_expense', {})
             exp_pct = exp_data.get('change_pct', 0)
             exp_abs = exp_data.get('change_abs', 0)
             
             # Higher expense is RED
             exp_color = "val-red" if exp_pct > 0 else "val-green" 
             exp_arrow = "▲" if exp_pct >= 0 else "▼"
             
             html += f"<tr><td class='metric-header'>MoM Expense Change</td><td class='{exp_color}'>{exp_arrow} {exp_pct:+.1f}% (${exp_abs:,.0f})</td><td>-</td></tr>"
        
        html += "</tbody></table>"
        return html

    def generate_portfolio_table(self, wb, property_name: str) -> str:
        """Generates the Portfolio Snapshot table from 'Internal' sheet."""
        if "CRES - Portfolio (Internal)" not in wb.sheetnames or "DB" not in wb.sheetnames:
            return ""

        ws_internal = wb["CRES - Portfolio (Internal)"]
        ws_db = wb["DB"]
        
        # 1. Get Multipliers from DB sheet (Q15:T15)
        # Assuming Q15=Down, R15=Side, S15=UpAng, T15=Green
        # Values in VBA might be retrieved differently, specifically checking ranges.
        # Let's read Q15, R15, S15, T15.
        try:
             mult_down = float(ws_db["Q15"].value or 0)
             mult_side = float(ws_db["R15"].value or 0)
             mult_up_ang = float(ws_db["S15"].value or 0)
             mult_green = float(ws_db["T15"].value or 0)
        except:
             return "<p>Error reading multipliers from DB sheet.</p>"

        # 2. Find Property Row in Internal Sheet
        # Header is Row 4. Data starts Row 5.
        # Column B is Property Name.
        target_row = None
        for row in ws_internal.iter_rows(min_row=5, max_col=2):
            cell_val = row[1].value # Column B
            if cell_val and str(cell_val).strip().lower() == property_name.strip().lower():
                target_row = row[0].row
                break
        
        if not target_row:
             return f"<p>Property '{property_name}' not found in Portfolio Snapshot.</p>"
             
        # 3. Read Row Data (Cols B to AD -> 2 to 30)
        # We need headers from Row 4
        headers = []
        for col in range(2, 31):
            h_val = ws_internal.cell(row=4, column=col).value
            headers.append(h_val or f"Col_{col}")
            
        row_vals = []
        for col in range(2, 31):
            val = ws_internal.cell(row=target_row, column=col).value
            row_vals.append(val)
            
        # 4. Generate HTML
        html = f"{self.css_styles}\n<div style='overflow-x:auto;'><table class='report-table'><thead><tr>"
        for h in headers:
            html += f"<th>{h}</th>"
        html += "</tr></thead><tbody><tr>"
        
        for idx, val in enumerate(row_vals):
            col_idx = idx + 2 # 1-based column index
            header = headers[idx]
            display_val = str(val) if val is not None else ""
            css_class = ""
            icon_html = ""
            
            # Formatting
            if isinstance(val, (int, float)):
                 if "Accuarcy" in header or "Occ" in header or "Yield" in header or "DSCR" in header or "vs Bdgt" in header:
                      display_val = f"{val:.1%}" if abs(val) < 10 else f"{val:.1f}%" # Heuristic
                 elif val > 1000 or val < -1000:
                      display_val = f"${val:,.0f}"
                 else:
                      display_val = f"{val:,.2f}"

            # --- SMART ARROW LOGIC (Column J: In Place Eff. Rate?) ---
            # VBA Logic:
            # vI = wsPort.Cells(i, "I").value
            # compare vI * multiplier vs vJ (Value in J)
            # Actually VBA compares vJ against thresholds derived from vI * Multiplier?
            # Let's re-read user provided VBA:
            # vI = wsPort.Cells(i, "I").value
            # Set rngJ = wsPort.Cells(i, "J")
            # rngJ value is compared against vI * mult...
            # Wait, "I" is col 9. "J" is col 10.
            # Header I is "Gross Scheduled Rent" (from screenshot? No, earlier screenshot I=Debt Yield?)
            # Let's align with VBA blindly: 
            # Col 9 (I) is the "Base". Col 10 (J) is the "Target".
            
            # Let's find index for Col 9 (idx=7) and Col 10 (idx=8)
            col_9_val = row_vals[7] if len(row_vals) > 7 else 0 # Col I
            
            if col_idx == 10: # Column J
                try:
                    vI = float(col_9_val)
                    vJ = float(val) if val is not None else 0
                    
                    # Logic from VBA:
                    # Criteria 2 (Down): >= vI * multDown
                    # Criteria 3 (Side): >= vI * multSide
                    # Criteria 4 (UpAng): >= vI * multUpAng
                    # Criteria 5 (Green): >= vI * multGreen
                    
                    # IconSet logic is usually < val1, < val2, etc. 
                    # But .Operator = xlGreaterEqual implies: 
                    # if Val >= T_Green -> Green Up Arrow
                    # else if Val >= T_UpAng -> Up Angled
                    # ...
                    
                    if vJ >= vI * mult_green:
                        icon_html = "<span class='arrow-up'>&#9650;</span> " # Up Arrow
                    elif vJ >= vI * mult_up_ang:
                        icon_html = "<span class='arrow-up'>&#8599;</span> " # Angled Up
                    elif vJ >= vI * mult_side:
                        icon_html = "<span class='arrow-side'>&#9654;</span> " # Side
                    elif vJ >= vI * mult_down:
                        icon_html = "<span class='arrow-down'>&#8600;</span> " # Angled Down
                    else:
                        icon_html = "<span class='arrow-down'>&#9660;</span> " # Down Arrow
                        
                except Exception as e:
                    pass # Non-numeric

            # --- STANDARD COLOR SCALES for other columns ---
            # Reusing logic from financial table if headers match
            # Phys Occ (Col F, idx 4), Econ Occ (Col G, idx 5)
            # Debt Yield (Col K?), DSCR (Col L?)
            # CRES - Portfolio (Internal) differs slightly in layout from Financial Data
            # Let's infer based on header string
            
            h_lower = str(header).lower()
            if "physical occupan" in h_lower:
                 v = float(val) if isinstance(val, (int, float)) else 0
                 if v >= 0.90: css_class = "val-green"
                 elif v >= 0.85: css_class = "val-yellow"
                 else: css_class = "val-red"
            elif "economic occupan" in h_lower:
                 v = float(val) if isinstance(val, (int, float)) else 0
                 if v >= 0.85: css_class = "val-green"
                 elif v >= 0.75: css_class = "val-yellow"
                 else: css_class = "val-red"
            elif "dscr" in h_lower:
                 v = float(val) if isinstance(val, (int, float)) else 0
                 if v >= 1.15: css_class = "val-green"
                 elif v >= 1.0: css_class = "val-yellow"
                 else: css_class = "val-red"
            elif "vs bdgt" in h_lower: # Cur Mnth vs Bdgt, YTD vs Bdgt
                 v = float(val) if isinstance(val, (int, float)) else 0
                 if v >= 0: css_class = "val-green"
                 elif v >= -0.10: css_class = "val-yellow"
                 else: css_class = "val-red"

            
            html += f"<td class='{css_class}'>{icon_html}{display_val}</td>"
            
        html += "</tr></tbody></table></div>"
        return html

    def generate_financial_table(self, df: pd.DataFrame) -> str:
        """Generates the Monthly Financial Data HTML table with conditional formatting."""
        if df.empty:
            return "<p>No financial data available.</p>"
            
        # Whitelist of metrics to display (Exact match or substring, handle case sensitivity)
        # Based on user request
        ALLOWED_METRICS = [
            "Debt Yield",
            "1 Month DSCR",
            "3 Month DSCR",
            "12 Month DSCR", 
            "Physical Occupancy",
            "Economic Occupancy",
            "Break Even Occ. - NOI",
            "Break Even Occ. - Cash Flow",
            "Asking Rent",
            "Gross Scheduled Rent",
            "Inplace Eff. Rent", # Matches 'Inplace Eff. Rent (GSR - Conc)'
            "Occupied Inplace Eff. Rent",
            "Concession %"
        ]

        html = f"{self.css_styles}\n<div style='overflow-x:auto;'><table class='report-table'><thead><tr><th>Metric</th>"
        
        # Header Row (Months)
        date_cols = [c for c in df.columns if c not in ['Metric', 'sheet_source']]
        for col in date_cols:
            html += f"<th>{col}</th>"
        html += "</tr></thead><tbody>"
        
        # Specific Formatting Rules
        def get_format_class(metric, value):
            try:
                val = float(value)
            except:
                return ""
                
            m_lower = metric.lower()
            
            # Physical Occupancy (90/85)
            if "physical occupancy" in m_lower:
                if val >= 0.90: return "val-green"
                if val >= 0.85: return "val-yellow"
                return "val-red"
                
            # Economic Occupancy (85/75)
            if "economic occupancy" in m_lower:
                if val >= 0.85: return "val-green"
                if val >= 0.75: return "val-yellow"
                return "val-red"
                
            # Debt Yield (7.5 / 5.95) - Note: Input might be 7.5 or 0.075 depending on scale
            # Assuming percentage is decimal (0.075)
            if "debt yield" in m_lower:
                 if val >= 0.075: return "val-green"
                 if val >= 0.0595: return "val-yellow"
                 return "val-red"

            # DSCR (1.15 / 1.0)
            if "dscr" in m_lower or "debt service coverage" in m_lower:
                if val >= 1.15: return "val-green"
                if val >= 1.0: return "val-yellow"
                return "val-red"
            
            return ""

        # Data Rows
        for idx, row in df.iterrows():
            metric = row.name # index is Metric
            
            # Whitelist Filtering
            is_allowed = False
            for allowed in ALLOWED_METRICS:
                if allowed.lower() in str(metric).lower():
                    is_allowed = True
                    break
            
            if not is_allowed:
                continue
                
            html += f"<tr><td class='metric-header'>{metric}</td>"
            for col in date_cols:
                val = row[col]
                
                # Format Value String
                display_val = str(val)
                if isinstance(val, (int, float)):
                    if "Occupancy" in metric or "Yield" in metric or "Rate" in metric or "DSCR" in metric or "Concession" in metric:
                         # Handle 0.95 vs 95.0
                         # If value < 2 and likely a percentage, format as %. Else numeric.
                         # DSCR is usually > 1 but < 5.
                         if "DSCR" in metric:
                             display_val = f"{val:.2f}"
                         elif abs(val) <= 1: 
                             display_val = f"{val:.1%}"
                         else: # e.g. 5.15 mean 5.15% ? Or raw number?
                             # In T12, Occupancy usually 0.95.
                             if "Occupancy" in metric and abs(val) > 1:
                                 # Maybe it's 95.0?
                                 display_val = f"{val:.1f}%"
                             else:
                                 display_val = f"{val:.1%}"
                    elif val > 1000 or val < -1000: # Likely currency
                         display_val = f"${val:,.0f}"
                    else:
                         display_val = f"{val:,.2f}"
                
                # Get CSS Class
                css_class = get_format_class(metric, val)
                html += f"<td class='{css_class}'>{display_val}</td>"
            html += "</tr>"
            
        html += "</tbody></table></div>"
        return html
