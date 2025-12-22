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
        from src.ui.theme import (
            COLOR_NAVY, COLOR_TEAL, COLOR_SAGE, COLOR_ORANGE, COLOR_CREAM,
            REPORT_HEADER_BG, REPORT_HEADER_TEXT
        )
        # CSS Styles for Tables
        self.css_styles = f"""
        <style>
            .report-table {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                border-collapse: collapse;
                width: 100%;
                table-layout: fixed; /* Equal column widths */
                margin-bottom: 25px;
                font-size: 0.9em;
                background-color: #ffffff; /* Light background for clean look */
                color: #333333 !important; /* Dark text for readability */
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.05); /* Softer shadow */
            }}
            .report-table thead tr {{
                background-color: {REPORT_HEADER_BG};
                color: {REPORT_HEADER_TEXT};
                text-align: left;
            }}
            .report-table th, .report-table td {{
                padding: 12px 15px;
                border: 1px solid #dddddd; /* Lighter border */
                text-align: center; /* Center align all data columns */
            }}
            .report-table tbody tr {{
                border-bottom: 1px solid #dddddd;
            }}
            
            .report-table tbody tr:nth-of-type(even) {{
                background-color: #f8f9fa; /* Subtle zebra striping */
            }}

            .report-table tbody tr:nth-of-type(odd) {{
                background-color: #ffffff;
            }}
            
            .report-table tbody tr:last-of-type {{
                border-bottom: 2px solid {COLOR_TEAL};
            }}
            
            /* High Contrast Status Colors - GLOBAL (Standard Dark/White) */
            .val-green {{ background-color: #1e4620 !important; color: #ffffff !important; font-weight: bold; }}
            .val-yellow {{ background-color: #4d3e04 !important; color: #fdf2ce !important; font-weight: bold; }}
            .val-red {{ background-color: #5a1a1e !important; color: #ffffff !important; font-weight: bold; }}

            /* Portfolio Specific Bright Colors (User Request) */
            .portfolio-green {{ background-color: #00FF00 !important; color: #000000 !important; font-weight: bold; }}
            .portfolio-yellow {{ background-color: #FFFF00 !important; color: #000000 !important; font-weight: bold; }}
            .portfolio-red {{ background-color: #FF3636 !important; color: #000000 !important; font-weight: bold; }}
            
            /* Arrow Colors - Darker for Light Mode Visibility */
            .arrow-up {{ color: #2e7d32 !important; font-weight: bold; }}   
            .arrow-side {{ color: #f57f17 !important; font-weight: bold; }} 
            .arrow-down {{ color: #c62828 !important; font-weight: bold; }} 
            
            .metric-header {{ font-weight: bold; color: {COLOR_NAVY} !important; text-align: left !important; }}
            
            /* Print-Specific Styles for Chrome PDF Export */
            @media print {{
                /* COMPACT MODE - Reduce sizes for print */
                .report-table {{
                    font-size: 0.75em !important;
                    margin-bottom: 10px !important;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }}
                
                .report-table th, .report-table td {{
                    padding: 4px 6px !important;
                }}
                
                h4 {{
                    font-size: 1em !important;
                    margin: 8px 0 4px 0 !important;
                }}
                
                /* Force each major section to start on a new page */
                .print-section {{
                    page-break-before: always;
                    break-before: page;
                }}
                
                /* Keep headers with their content - never orphan a header */
                h1, h2, h3, h4, h5, h6,
                .section-header {{
                    page-break-after: avoid;
                    break-after: avoid;
                }}
                
                /* Keep table headers with table body */
                .report-table thead {{
                    display: table-header-group;
                }}
                
                .report-table tbody {{
                    page-break-inside: avoid;
                    break-inside: avoid;
                }}
            }}
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
            
            # Scale values by 1000 (data is in thousands)
            if isinstance(val_mo, (int, float)):
                val_mo = val_mo * 1000
            if isinstance(val_ytd, (int, float)):
                val_ytd = val_ytd * 1000
            
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
             inc_abs = inc_data.get('change_abs', 0) * 1000  # Scale by 1000
             
             inc_color = "val-green" if inc_pct >= 0 else "val-red"
             inc_arrow = "▲" if inc_pct >= 0 else "▼"
             
             # User Request: Remove fills (background color) for MoM rows, keep arrows
             # We use inc_color to determine arrow color only, but remove class='val-...' from td
             # Use standard "green"/"red" to match Portfolio Snapshot arrows
             arrow_style = f"color: {'green' if inc_pct >= 0 else 'red'}; font-weight: bold;"
             html += f"<tr><td class='metric-header'>MoM Income Change</td><td><span style='{arrow_style}'>{inc_arrow}</span> {inc_pct:+.1f}% (${inc_abs:,.0f})</td><td>-</td></tr>"
             
             exp_data = mom_changes.get('total_expense', {})
             exp_pct = exp_data.get('change_pct', 0)
             exp_abs = exp_data.get('change_abs', 0) * 1000  # Scale by 1000
             
             # For Negative Expenses:
             # Increase (+ve change) -> Closer to 0 -> Savings -> GREEN
             # Decrease (-ve change) -> Further from 0 -> Overspending -> RED
             exp_color = "val-green" if exp_pct >= 0 else "val-red"
             exp_arrow = "▲" if exp_pct >= 0 else "▼"
             
             exp_arrow = "▲" if exp_pct >= 0 else "▼"
             
             arrow_style_exp = f"color: {'green' if exp_pct >= 0 else 'red'}; font-weight: bold;"
             html += f"<tr><td class='metric-header'>MoM Expense Change</td><td><span style='{arrow_style_exp}'>{exp_arrow}</span> {exp_pct:+.1f}% (${exp_abs:,.0f})</td><td>-</td></tr>"
        
        html += "</tbody></table>"
        return html

    def generate_portfolio_table(self, wb, property_name: str) -> str:
        """Generates the Portfolio Snapshot table from 'Internal' sheet."""
        from src.ui.theme import COLOR_NAVY, COLOR_TEAL, COLOR_SAGE
        try:
            if "CRES - Portfolio (Internal)" not in wb.sheetnames or "DB" not in wb.sheetnames:
                return "<p>Missing required sheets ('CRES - Portfolio (Internal)' or 'DB').</p>"

            ws_internal = wb["CRES - Portfolio (Internal)"]
            ws_db = wb["DB"]
            
            # 1. Get Multipliers from DB sheet (Q15:T15)
            try:
                 mult_down = float(ws_db["Q15"].value or -0.075)
                 mult_side = float(ws_db["R15"].value or 0)
                 mult_up_ang = float(ws_db["S15"].value or 0.075)
                 mult_green = float(ws_db["T15"].value or 0.1)
            except:
                 mult_down, mult_side, mult_up_ang, mult_green = -0.075, 0, 0.075, 0.1

            # 2. Find Property Row in Internal Sheet
            target_row = None
            for row in ws_internal.iter_rows(min_row=5, max_col=2):
                cell_val = row[1].value # Column B
                if cell_val and str(cell_val).strip().lower() == property_name.strip().lower():
                    target_row = row[0].row
                    break
            
            if not target_row:
                 return f"<p>Property '{property_name}' not found in Internal sheet.</p>"
                 
            # 3. Read Row Data (Cols B to AD -> 2 to 30)
            headers = []
            for col in range(2, 31):
                h_val = ws_internal.cell(row=4, column=col).value
                headers.append(h_val or f"Col_{col}")
                
            row_vals = []
            for col in range(2, 31):
                val = ws_internal.cell(row=target_row, column=col).value
                row_vals.append(val)
                
            # Helper to generate a sub-table
            def generate_chunk(chunk_headers, chunk_vals, title, header_bg):
                c_html = f"{self.css_styles}\n<div style='margin-bottom: 20px; overflow-x:auto;'><table class='report-table'><thead>"
                c_html += f"<tr><th colspan='{len(chunk_headers)}' style='text-align:center; background-color:{header_bg}; font-size:1.1em; padding: 8px;'>{title}</th></tr>"
                
                c_html += "<tr>"
                for h in chunk_headers:
                    c_html += f"<th>{h}</th>"
                c_html += "</tr></thead><tbody><tr>"
                
                # Pre-calculate Prior Rate for Arrow Logic
                prior_rate_val = 0
                for i, h in enumerate(headers):
                     h_str = str(h).lower().replace('\n', ' ')
                     # Explicitly match In Place Rate/Rent Prior Month (Exclude YEAR)
                     if ("prior" in h_str) and \
                        ("inplace" in h_str or "in place" in h_str) and \
                        ("rate" in h_str or "rent" in h_str) and \
                        ("year" not in h_str):
                         try: prior_rate_val = float(row_vals[i] or 0)
                         except: pass
                         break

                for idx, val in enumerate(chunk_vals):
                    header = chunk_headers[idx]
                    h_str = str(header).strip()
                    
                    # VALUE FORMATTING
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
                        is_pct = any(x in h_str for x in ["Occupancy", "Yield", "vs Bdgt", "Sequential", "vs T1 Prior", "vs T3 Prior"])
                        if "DSCR" in h_str: is_pct = False
                            
                        if is_pct:
                            display_val = f"{raw_val:.1%}" if abs(raw_val) < 10 else f"{raw_val:.1f}%"
                        elif "DSCR" in h_str:
                            display_val = f"{raw_val:.2f}"
                        elif "Rate" in h_str: # In Place Eff. Rate
                            display_val = f"${raw_val:,.0f}"
                        else:
                            display_val = f"{raw_val:,.2f}"
                    else:
                        display_val = str(val) if val is not None else "-"

                    # CONDITIONAL FORMATTING
                    css_class = ""
                    arrow_html = ""
                    
                    if is_valid_num:
                        if "Physical Occupancy" in h_str:
                            css_class = "portfolio-green" if raw_val >= 0.90 else "portfolio-yellow" if raw_val >= 0.85 else "portfolio-red"
                        elif "Economic Occupancy" in h_str:
                            css_class = "portfolio-green" if raw_val >= 0.85 else "portfolio-yellow" if raw_val >= 0.75 else "portfolio-red"
                        elif "Debt Yield" in h_str:
                             cut_g, cut_y = (7.5, 5.95) if raw_val > 1 else (0.075, 0.0595)
                             css_class = "portfolio-green" if raw_val >= cut_g else "portfolio-yellow" if raw_val >= cut_y else "portfolio-red"
                        elif "DSCR" in h_str:
                            css_class = "portfolio-green" if raw_val >= 1.15 else "portfolio-yellow" if raw_val >= 1.0 else "portfolio-red"
                        elif "vs Bdgt" in h_str: 
                            cut_g, cut_y = (3.0, 0.0) if raw_val > 2 else (0.03, 0.0)
                            css_class = "portfolio-green" if raw_val >= cut_g else "portfolio-yellow" if raw_val >= cut_y else "portfolio-red"

                        # ARROWS
                        # Match "In Place Eff. Rate", "Inplace Eff. Rent", etc.
                        is_rate_col = ("inplace" in h_str.lower() or "in place" in h_str.lower()) and \
                                      ("rate" in h_str.lower() or "rent" in h_str.lower())
                        
                        if is_rate_col and "prior" not in h_str.lower():
                             change = (raw_val - prior_rate_val) / prior_rate_val if prior_rate_val != 0 else 0
                             
                             # Custom Thresholds for Rent/Rate (More sensitive than 7.5%)
                             # Use 0.5% for angled, 1.0% for full arrow
                             t_green = 0.01
                             t_up = 0.005
                             t_down = -0.005
                             t_red = -0.01
                             
                             if change >= t_green: arrow_html = "▲ "
                             elif change >= t_up: arrow_html = "⇗ "
                             elif change > t_down: arrow_html = "▶ " # Flat / Steady
                             elif change > t_red: arrow_html = "⇘ "
                             else: arrow_html = "▼ "
                             
                             color = "green" if change > 0 else "red" if change < 0 else "#888"
                             
                             # Add Tooltip for Debugging
                             tooltip = f"Current: {raw_val:,.0f} | Prior: {prior_rate_val:,.0f} | Change: {change:.2%}"
                             arrow_html = f"<span title='{tooltip}' style='color:{color};font-weight:bold;cursor:help;'>{arrow_html}</span>"
                             display_val = f"{arrow_html}{display_val}"
                             
                        if "vs T1 Prior Year" in h_str or "vs T3 Prior Year" in h_str or "Sequential" in h_str:
                             color = "green" if raw_val >= 0.01 else "#ccc" if raw_val >= -0.01 else "red"
                             symbol = "▲" if raw_val >= 0.01 else "▶" if raw_val >= -0.01 else "▼"
                             arrow_html = f"<span style='color:{color};font-weight:bold'>{symbol}</span> "
                             display_val = f"{arrow_html}{display_val}"
                             css_class = ""
                
                    c_html += f"<td class='{css_class}'>{display_val}</td>"
                    
                c_html += "</tr></tbody></table></div>"
                return c_html

            # --- PREPARE DATA CHUNKS ---
            # --- PREPARE DATA CHUNKS ---
            headers_cl = []
            indices_cl = []
            for i, h in enumerate(headers):
                 # Robust Normalize: Replace newlines and multiple spaces
                 h_norm = str(h).replace('\n', ' ').replace('  ', ' ').strip()
                 if "In Place Eff. Rate Prior Month" not in h_norm:
                     headers_cl.append(h)
                     indices_cl.append(i)
            
            n = len(headers_cl)
            
            # SLICING LOGIC (5 Groups based on User Request)
            # Total Cleansed Columns = 28
            # 1. Details: 5 cols (Prop Name, Client, PM, State, Units)
            # 2. Operations: 5 cols (Visible)
            # 3. NOI Variance: 6 cols
            # 4. Revenue Variance: 6 cols
            # 5. Expense Variance: 6 cols
            
            idx_1 = min(5, n)
            idx_2 = min(10, n)
            idx_3 = min(16, n)
            idx_4 = min(22, n)
            
            html_out = ""
            
            # Group 1: Details
            if n > 0:
                g1_idx = indices_cl[:idx_1]
                # Use COLOR_TEAL for Property Details to contrast with Navy headers
                html_out += generate_chunk(headers_cl[:idx_1], [row_vals[i] for i in g1_idx], "Property Details", COLOR_TEAL)
            
            # Group 2: Operations
            if n > idx_1:
                g2_idx = indices_cl[idx_1:idx_2]
                # Use COLOR_TEAL for Operations
                html_out += generate_chunk(headers_cl[idx_1:idx_2], [row_vals[i] for i in g2_idx], "Cur. Mnth. Operations - Financial Based", COLOR_TEAL)
            
            # Group 3: NOI
            if n > idx_2:
                g3_idx = indices_cl[idx_2:idx_3]
                # Use COLOR_TEAL for NOI variance
                html_out += generate_chunk(headers_cl[idx_2:idx_3], [row_vals[i] for i in g3_idx], "NOI - % Variance", COLOR_TEAL)

            # Group 4: Revenue
            if n > idx_3:
                g4_idx = indices_cl[idx_3:idx_4]
                # Use COLOR_TEAL for Revenue
                html_out += generate_chunk(headers_cl[idx_3:idx_4], [row_vals[i] for i in g4_idx], "Revenue - % Variance", COLOR_TEAL)
                
            # Group 5: Expenses
            if n > idx_4:
                g5_idx = indices_cl[idx_4:]
                # Use COLOR_TEAL for Expenses
                html_out += generate_chunk(headers_cl[idx_4:], [row_vals[i] for i in g5_idx], "Expenses - % Variance", COLOR_TEAL)
                
            return html_out
            
        except Exception as e:
            return f"<p style='color:red;'>Error generating portfolio table: {str(e)}</p>"

    def generate_financial_table(self, df: pd.DataFrame) -> str:
        """Generates the Monthly Financial Data HTML table with conditional formatting."""
        if df.empty:
            return "<p>No financial data available.</p>"
            
        # Whitelist of metrics AND Order definition
        # Based on user request (Sheet Order)
        ALLOWED_METRICS = [
            "Debt Yield",
            "1 Month DSCR",
            "12 Month DSCR", 
            "Physical Occupancy", # Matches 'Physical Occupancy (Stats)' if exists, or just 'Physical Occupancy'
            "Economic Occupancy",
            "Break Even Occ. - NOI",
            "Break Even Occ. - Cash Flow",
            "Asking Rent (Stats)", # Specialized to exclude 'Property Asking Rent'
            # "Gross Scheduled Rent", # Removed per user request
            "Inplace Eff. Rent",
            "Occupied Inplace Eff. Rent",
            "Concession %",
            "Delinquency %",
            "Trailing 12 month NOI"
        ]

        html = f"{self.css_styles}\n<div style='overflow-x:auto;'><table class='report-table'><thead><tr><th>Metric</th>"
        
        # Re-sort dataframe to match ALLOWED_METRICS order
        # Create a categorical type for Metric column (index)
        df = df.copy()
        
        # Ensure 'Metric' is the index for filtering if it's currently a column
        if 'Metric' in df.columns:
            df = df.set_index('Metric')
            
        df['sort_key'] = 999
        
        for idx, metric_pattern in enumerate(ALLOWED_METRICS):
            # Find partial matches for this pattern
            # Ensure index is treated as string
            mask = df.index.astype(str).str.contains(metric_pattern, case=False, regex=False)
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
                             if any(x in str(metric).lower() for x in ['occupancy', 'yield', 'percent', '%', 'concession', 'break even']):
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
    def generate_ai_variance_tables(self, ai_data: dict) -> str:
        """Renders AI-generated JSON narratives as professional HTML tables."""
        if not ai_data or not isinstance(ai_data, dict):
            return "<p><i>No narrative data available to render.</i></p>"
            
        html = f"{self.css_styles}\n"
        
        # Helper for robust sorting (highest positive % -> lowest negative %)
        def get_sort_val(item):
            # Check common keys for percentage change
            val = item.get("variance_pct", item.get("change_pct", item.get("deviation_pct", 0)))
            try:
                # Handle strings like "5.2%" or "-10.5"
                if isinstance(val, str):
                    val = val.replace('%', '').strip()
                return float(val)
            except:
                return -999999.0 # Push errors to bottom
        
        # 1. Budget Variances Section
        html += "<h3 style='margin-top: 30px;'>1️⃣ Budget Variances</h3>"
        
        # User defined exclusions for variance reporting
        excluded_metrics = [
            "gross scheduled rent", "effective rental income", "total other income",
            "net eff. gross income", "total income", "total expense", "ebitda",
            "total below line", "monthly cash flow", "total cash"
        ]
        
        bv = ai_data.get("budget_variances", {})
        if not bv or (not bv.get("Revenue") and not bv.get("Expenses")):
             html += "<p>No significant budget variances reported.</p>"
        else:
            for cat in ["Revenue", "Expenses"]:
                items = bv.get(cat, [])
                if not items: continue
                
                # Sort by ACTUAL variance PERCENTAGE (descending - Highest to Lowest)
                items.sort(key=get_sort_val, reverse=True)
                
                html += f"<h4>{cat}</h4>"
                html += "<table class='report-table'><thead><tr><th style='width: 25%;'>Metric</th><th style='width: 12%;'>Actual</th><th style='width: 12%;'>Budget</th><th style='width: 12%;'>Variance %</th><th>Investigative Questions</th></tr></thead><tbody>"
                for item in items:
                    metric = item.get("metric", "Unknown")
                    
                    # POST-PROCESSING FILTER check
                    m_lower = metric.lower().strip()
                    if any(ex in m_lower for ex in excluded_metrics):
                        continue
                        
                    actual = item.get("actual", 0)
                    budget = item.get("budget", 0)
                    var_pct = item.get("variance_pct", 0)
                    questions = item.get("questions", [])
                    q_html = "<br>".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
                    
                    fmt_actual = f"${actual:,.2f}" if isinstance(actual, (int, float)) else str(actual)
                    fmt_budget = f"${budget:,.2f}" if isinstance(budget, (int, float)) else str(budget)
                    
                    html += f"<tr><td class='metric-header'>{metric}</td><td>{fmt_actual}</td><td>{fmt_budget}</td><td>{var_pct}%</td><td style='text-align: left;'>{q_html}</td></tr>"
                html += "</tbody></table>"
                
        # 2. Trailing Anomalies Section
        html += "<h3 style='margin-top: 40px;'>2️⃣ Trailing Anomalies</h3>"
        ta = ai_data.get("trailing_anomalies", {})
        if not ta or (not ta.get("Revenue") and not ta.get("Expenses")):
             html += "<p>No significant trailing anomalies reported.</p>"
        else:
            for cat in ["Revenue", "Expenses"]:
                items = ta.get(cat, [])
                if not items: continue
                
                # Sort by ACTUAL deviation percentage (descending - Highest to Lowest)
                items.sort(key=get_sort_val, reverse=True)
                
                html += f"<h4>{cat}</h4>"
                html += "<table class='report-table'><thead><tr><th style='width: 25%;'>Metric</th><th style='width: 12%;'>Current</th><th style='width: 12%;'>T3 Avg</th><th style='width: 12%;'>Deviation %</th><th>Investigative Questions</th></tr></thead><tbody>"
                for item in items:
                    metric = item.get("metric", "Unknown")
                    
                    # POST-PROCESSING FILTER check
                    m_lower = metric.lower().strip()
                    if any(ex in m_lower for ex in excluded_metrics):
                        continue

                    current = item.get("current", 0)
                    t3_avg = item.get("t3_avg", 0)
                    dev_pct = item.get("deviation_pct", 0)
                    questions = item.get("questions", [])
                    q_html = "<br>".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
                    
                    fmt_current = f"${current:,.2f}" if isinstance(current, (int, float)) else str(current)
                    fmt_t3 = f"${t3_avg:,.2f}" if isinstance(t3_avg, (int, float)) else str(t3_avg)
                    
                    html += f"<tr><td class='metric-header'>{metric}</td><td>{fmt_current}</td><td>{fmt_t3}</td><td>{dev_pct}%</td><td style='text-align: left;'>{q_html}</td></tr>"
                html += "</tbody></table>"
                
        return html
