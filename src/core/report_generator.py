"""Generates HTML reports for the T12 Property Analysis Tool.

This class is responsible for creating visually rich, data-driven HTML tables
derived from the processed financial data. It handles:
1.  Merged KPI Table (Current Month + YTD)
2.  Financial Data Table (Monthly view with conditional formatting)
3.  Portfolio Snapshot Table (from 'Internal' sheet with custom arrow logic)
"""

import pandas as pd
import numpy as np
from datetime import datetime

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
            ("net_eff_gross_income", "Total Income"),
            ("total_expense", "Total Expenses"),
            ("ebitda_noi", "Net Operating Income")
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
                <td class='metric-header'>Expense Ratio</td>
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
             
             exp_data = mom_changes.get('total_expense', {})
             exp_pct = exp_data.get('change_pct', 0)
             exp_abs = exp_data.get('change_abs', 0)
             
             # For Negative Expenses:
             # Increase (+ve change) -> Closer to 0 -> Savings -> GREEN
             # Decrease (-ve change) -> Further from 0 -> Overspending -> RED
             exp_color = "val-green" if exp_pct >= 0 else "val-red"
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
        try:
             mult_down = float(ws_db["Q15"].value or 0)
             mult_side = float(ws_db["R15"].value or 0)
             mult_up_ang = float(ws_db["S15"].value or 0)
             mult_green = float(ws_db["T15"].value or 0)
        except:
             mult_down, mult_side, mult_up_ang, mult_green = -0.075, 0, 0.075, 0.1 # Fallback defaults

        # 2. Find Property Row in Internal Sheet
        target_row = None
        for row in ws_internal.iter_rows(min_row=5, max_col=2):
            cell_val = row[1].value # Column B
            if cell_val and str(cell_val).strip().lower() == property_name.strip().lower():
                target_row = row[0].row
                break
        
        if not target_row:
             return f"<p>Property '{property_name}' not found in Portfolio Snapshot.</p>"
             
        # 3. Read Row Data (Cols B to AD -> 2 to 30)
        headers = []
        for col in range(2, 31):
            h_val = ws_internal.cell(row=4, column=col).value
            headers.append(h_val or f"Col_{col}")
            
        row_vals = []
        for col in range(2, 31):
            val = ws_internal.cell(row=target_row, column=col).value
            row_vals.append(val)
            
        # 4. Generate HTML
        html = f"{self.css_styles}\n<div style='overflow-x:auto;'><table class='report-table'><thead>"
        
        # --- SUPER HEADER ROW ---
        # Based on user description + typical layout
        # Col 1-5 (Phys Occ to DSCR): Operations
        # Col 6-11: NOI % Variance
        # Col 12-17: Revenue % Variance
        # Col 18-23: Expenses % Variance
        # ... and so on.
        # We need to map this carefully to the filtered columns.
        
        # Filter headers first to know what we are displaying
        display_headers = []
        displayed_indices = []
        for i, h in enumerate(headers):
            # Robust check for hidden column
            h_clean = str(h).replace('\n', ' ').replace('  ', ' ')
            if "In Place Eff. Rate Prior Month" not in h_clean:
                display_headers.append(h)
                displayed_indices.append(i)
        
        # Define Groups (Count visible columns in each group)
        # Groups from user image/inference:
        # A. Cur. Mnth. Operations - Financial Based
        #    - Physical Occupancy
        #    - Economic Occupancy
        #    - In Place Eff. Rate (Prior hidden)
        #    - Debt Yield
        #    - DSCR
        #    COUNT: 4 visible (if Debt Yield/DSCR involved) -> Wait, 5 items listed in code: Phys, Econ, Rate, Debt, DSCR.
        
        # B. NOI - % Variance
        #    - Cur vs Bdgt, T3 vs Bdgt, YTD vs Bdgt, T3 Seq, T1 vs T1, T3 vs T3
        #    COUNT: 6 columns
        
        # C. Revenue - % Variance
        #    - Same 6 columns
        
        # D. Expenses - % Variance
        #    - Same 6 columns?
        
        # Let's count total visible columns: 5 (Ops) + 6 (NOI) + 6 (Rev) + 6 (Exp) = 23?
        # Total headers range(2, 31) -> 29 columns.
        # 29 - 1 (hidden) = 28.
        # Where are the other 5? Maybe NOI only 6?
        
        # Let's add the super header row dynamically or hardcoded?
        # Hardcoding is safer for alignment if we know the structure.
        # Ops: 5 cols. (Phys, Econ, Rate, Debt, DSCR)
        # NOI: 6 cols
        # Rev: 6 cols
        # Exp: 6 cols
        # Total 23. Extra columns?
        # Let's check headers length: 29.
        # 29 - 23 = 6 columns left. Maybe "Net Income"? Or maybe only 3 groups?
        
        # Safer bet: Render Super Header ONLY for the known variance groups.
        html += "<tr>"
        # Spacer for Metadata columns (Property Name, Client, Portfolio Manager, State, # of Units)
        html += "<th colspan='5' style='background-color:#262730; border:none;'></th>" 
        
        html += "<th colspan='5' style='text-align:center; background-color:#444'>Cur. Mnth. Operations - Financial Based</th>"
        html += "<th colspan='6' style='text-align:center; background-color:#555'>NOI - % Variance</th>"
        html += "<th colspan='6' style='text-align:center; background-color:#444'>Revenue - % Variance</th>"
        html += "<th colspan='6' style='text-align:center; background-color:#555'>Expenses - % Variance</th>"
        # Any remaining?
        remaining = len(display_headers) - (5 + 5 + 6 + 6 + 6)
        if remaining > 0:
             html += f"<th colspan='{remaining}'>Other</th>"
        html += "</tr>"
        
        # --- SUB HEADER ROW ---
        html += "<tr>"
        for h in display_headers:
            html += f"<th>{h}</th>"
        html += "</tr></thead><tbody><tr>"
        
        # Helper: Find Prior Value for Arrow Logic (In Place Eff. Rate)
        prior_rate_val = 0
        try:
            # Locate index of "In Place Eff. Rate Prior Month"
            # Locate index of "In Place Eff. Rate Prior Month"
            for i, h in enumerate(headers):
                h_c = str(h).replace('\n', ' ').replace('  ', ' ')
                if "In Place Eff. Rate Prior Month" in h_c:
                    prior_rate_val = float(row_vals[i] or 0)
                    break
        except:
            prior_rate_val = 0

        for idx, val in enumerate(row_vals):
            header = headers[idx]
            h_str = str(header).strip()
            
            # 1. HIDING Logic
            # Robust check matching header logic
            h_clean_val = str(header).replace('\n', ' ').replace('  ', ' ')
            if "In Place Eff. Rate Prior Month" in h_clean_val:
                continue
                
            # 2. VALUE FORMATTING
            display_val = "-"
            raw_val = 0
            is_valid_num = False
            
            try:
                if val is not None:
                    raw_val = float(val)
                    is_valid_num = True
            except:
                pass
                
            if is_valid_num:
                # Percentage Logic, excluding DSCR or raw numbers
                is_pct = any(x in h_str for x in [
                    "Occupancy", "Yield", "vs Bdgt", "Sequential", "vs T1 Prior", "vs T3 Prior"
                ])
                if "DSCR" in h_str: 
                    is_pct = False
                    
                if is_pct:
                    display_val = f"{raw_val:.1%}" if abs(raw_val) < 10 else f"{raw_val:.1f}%"
                elif "DSCR" in h_str:
                    display_val = f"{raw_val:.2f}"
                elif "Rate" in h_str: # In Place Eff. Rate
                    display_val = f"${raw_val:,.0f}"
                else:
                    display_val = f"{raw_val:,.2f}" # Fallback
            else:
                display_val = str(val) if val is not None else "-"

            # 3. CONDITIONAL FORMATTING (Colors & Arrows)
            css_class = ""
            arrow_html = ""
            
            if is_valid_num:
                # A. Physical Occupancy (>90 Grn, >85 Yel)
                if "Physical Occupancy" in h_str:
                    if raw_val >= 0.90: css_class = "val-green"
                    elif raw_val >= 0.85: css_class = "val-yellow"
                    else: css_class = "val-red"
                
                # B. Economic Occupancy (>85 Grn, >75 Yel)
                elif "Economic Occupancy" in h_str:
                    if raw_val >= 0.85: css_class = "val-green"
                    elif raw_val >= 0.75: css_class = "val-yellow"
                    else: css_class = "val-red"
                    
                # C. Debt Yield (>7.5% Grn, >5.95% Yel) - Assuming decimal here if < 1, else scaled
                elif "Debt Yield" in h_str:
                     cutoff_green = 0.075
                     cutoff_yellow = 0.0595
                     if raw_val > 1: # scaled check
                         cutoff_green = 7.5
                         cutoff_yellow = 5.95
                     
                     if raw_val >= cutoff_green: css_class = "val-green"
                     elif raw_val >= cutoff_yellow: css_class = "val-yellow"
                     else: css_class = "val-red"
                     
                # D. DSCR (>1.15 Grn, >1.0 Yel)
                elif "DSCR" in h_str:
                    if raw_val >= 1.15: css_class = "val-green"
                    elif raw_val >= 1.0: css_class = "val-yellow"
                    else: css_class = "val-red"
                    
                # E. "Vs Budget" (3% Grn, 0% Yel) - Removed Sequential from here
                elif any(x in h_str for x in ["vs Bdgt"]): 
                    cutoff_g = 0.03
                    cutoff_y = 0.0
                    if raw_val > 2: # scaled check
                        cutoff_g = 3.0
                        cutoff_y = 0.0
                    
                    if raw_val >= cutoff_g: css_class = "val-green"
                    elif raw_val >= cutoff_y: css_class = "val-yellow"
                    else: css_class = "val-red"

                # F. ARROWS
                # "In Place Eff. Rate" (calculated vs Prior Month)
                # Use h_clean_val for robust matching
                if "In Place Eff. Rate" in h_clean_val and "Prior" not in h_clean_val:
                     change_pct = 0
                     if prior_rate_val != 0:
                         change_pct = (raw_val - prior_rate_val) / prior_rate_val
                     
                     # Using multipliers from DB:
                     # Green: >= 0.1 (mult_green) -> Up Arrow
                     # Up Ang: >= 0.075 -> Angled Up
                     # Side: >= 0 -> Side
                     # Down: >= -0.075 -> Angled Down
                     # Else -> Down Arrow
                     
                     # Check if change_pct is positive/negative vs multiplier
                     if change_pct >= mult_green: arrow_html = "▲ "
                     elif change_pct >= mult_up_ang: arrow_html = "⇗ "
                     elif change_pct >= mult_side: arrow_html = "▶ "
                     elif change_pct >= mult_down: arrow_html = "⇘ "
                     else: arrow_html = "▼ "
                     
                     # Color the arrow
                     if change_pct > 0: arrow_html = f"<span style='color:green;font-weight:bold'>{arrow_html}</span>"
                     elif change_pct < 0: arrow_html = f"<span style='color:red;font-weight:bold'>{arrow_html}</span>"
                     else: arrow_html = f"<span style='color:#ccc'>{arrow_html}</span>"
                     
                     display_val = f"{arrow_html}{display_val}"
                     
                # "T1 Current vs T1 Prior Year" AND "T3 Current vs T3 Prior Year" AND "Sequential" -> Arrow
                if "vs T1 Prior Year" in h_str or "vs T3 Prior Year" in h_str or "Sequential" in h_str:
                     # raw_val is the % itself
                     if raw_val >= 0.01: arrow_html = "<span style='color:green;font-weight:bold'>▲</span> "
                     elif raw_val >= -0.01: arrow_html = "<span style='color:#ccc'>▶</span> "
                     else: arrow_html = "<span style='color:red;font-weight:bold'>▼</span> "
                     display_val = f"{arrow_html}{display_val}"
                     css_class = ""
        
            html += f"<td class='{css_class}'>{display_val}</td>"
            
        html += "</tr></tbody></table></div>"
        return html

    def generate_financial_table(self, df: pd.DataFrame) -> str:
        """Generates the Monthly Financial Data HTML table with conditional formatting."""
        if df.empty:
            return "<p>No financial data available.</p>"
            
        # Whitelist of metrics AND Order definition
        # Based on user request (Sheet Order)
        ALLOWED_METRICS = [
            "Debt Yield",
            "1 Month DSCR",
            "3 Month DSCR",
            "12 Month DSCR", 
            "Physical Occupancy", # Matches 'Physical Occupancy (Stats)' if exists, or just 'Physical Occupancy'
            "Economic Occupancy",
            "Break Even Occ. - NOI",
            "Break Even Occ. - Cash Flow",
            "Asking Rent (Stats)", # Specialized to exclude 'Property Asking Rent'
            # "Gross Scheduled Rent", # Removed per user request
            "Inplace Eff. Rent",
            "Occupied Inplace Eff. Rent",
            "Concession %"
        ]

        html = f"{self.css_styles}\n<div style='overflow-x:auto;'><table class='report-table'><thead><tr><th>Metric</th>"
        
        # Re-sort dataframe to match ALLOWED_METRICS order
        # Create a categorical type for Metric column (index)
        df = df.copy()
        df['sort_key'] = 999
        
        for idx, metric_pattern in enumerate(ALLOWED_METRICS):
            # Find partial matches for this pattern
            mask = df.index.str.contains(metric_pattern, case=False, regex=False)
            df.loc[mask, 'sort_key'] = idx
            
        # Sort by key (matches user order), then by name (for ties)
        df = df.sort_values(['sort_key', 'Metric' if 'Metric' in df.columns else df.index.name or 'index'])
        # Drop rows that didn't match any allowed pattern (sort_key 999)
        df = df[df['sort_key'] != 999]
        
        # Header Row (Months)
        date_cols = [c for c in df.columns if c not in ['Metric', 'sheet_source', 'sort_key']]
        for col in date_cols:
            formatted_col = str(col)
            try:
                # 1. Check strict types
                if isinstance(col, (pd.Timestamp, datetime)):
                    formatted_col = col.strftime("%b-%y")
                else:
                    # 2. Robust String convert
                    # Handle raw strings like '2024-11-30 00:00:00'
                    s_col = str(col).strip()
                    # If it looks like a long timestamp string, try taking the date part
                    if " " in s_col:
                        s_col = s_col.split(" ")[0] # '2024-11-30'
                    
                    dt = pd.to_datetime(s_col, errors='coerce')
                    if pd.notna(dt):
                        formatted_col = dt.strftime("%b-%y")
            except:
                pass
                
            html += f"<th>{formatted_col}</th>"
        html += "</tr></thead><tbody>"
        
        # Data Rows
        for idx, row in df.iterrows():
            metric = row.name # index is Metric
            
            # Whitelist Filtering is mostly handled by sort logic above
            # Clean Metric Name for Display (Remove '(Stats)')
            display_metric = str(metric).replace('(Stats)', '').strip()
                
            html += f"<tr><td class='metric-header'>{display_metric}</td>"
            for col in date_cols:
                val = row[col]
                
                # Format Value String
                if pd.isna(val):
                    display_val = "-"
                else:
                    display_val = str(val)
                    try:
                        if isinstance(val, (int, float)):
                             # Percentage formatting logic
                             if any(x in str(metric).lower() for x in ['occupancy', 'yield', 'percent', '%', 'concession']):
                                 if "DSCR" not in metric and abs(val) <= 1:
                                     display_val = f"{val:.1%}"
                                 elif "DSCR" in metric:
                                     display_val = f"{val:.2f}"
                                 else:
                                     display_val = f"{val:.1%}" # Fallback
                             elif val > 100 or val < -100: # Heuristic for dollar amounts
                                 display_val = f"${val:,.0f}"
                             else:
                                 display_val = f"{val:.2f}"
                    except:
                        pass

                # No color class applied
                html += f"<td>{display_val}</td>"
            html += "</tr>"

            
        html += "</tbody></table></div>"
        return html
