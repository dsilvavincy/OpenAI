"""
Standard T12 Workbook Processor

Handles the new fixed-format T12 workbooks with Row 7 headers,
providing support for both Actual and Budget data across all visible sheets.
"""
import re
import pandas as pd
import numpy as np
import openpyxl
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from .base_processor import BaseFormatProcessor

class StandardT12Processor(BaseFormatProcessor):
    """
    Processor for the Standard T12 Workbook format.
    
    Expected format:
    - Header at Row 7
    - Column 1 (Index 0): Metric
    - Columns 2-13 (Index 1-12): Monthly Actuals
    - Column 14 (Index 13): YTD Actual
    - Column 15 (Index 14): YTD Budget
    - Columns 18-29 (Index 17-28): Monthly Budgets
    - Sheet Name = Property Name
    """
    
    def __init__(self):
        super().__init__(
            format_name="Standard_T12_Workbook",
            format_description="Standard T12 format with fixed Row 7 headers and Budget columns"
        )
    
    def can_process(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """Check if Row 7 contains the expected header labels."""
        try:
            # We check the first visible sheet
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            visible_sheets = [s.title for s in wb._sheets if s.sheet_state == 'visible']
            if not visible_sheets:
                return False
            
            check_sheet = sheet_name if sheet_name in visible_sheets else visible_sheets[0]
            df = pd.read_excel(file_path, sheet_name=check_sheet, header=None, nrows=10, engine="openpyxl")
            
            # Row 7 is index 6
            row_7 = df.iloc[6].tolist()
            
            # Check for YTD and Budget in expected places
            has_ytd = str(row_7[13]).upper() == "YTD"
            has_budget = str(row_7[14]).upper() == "BUDGET"
            
            # Check row 8 for common metrics
            row_8 = str(df.iloc[7, 0])
            has_common_metric = any(m in row_8 for m in ["Property Asking Rent", "Rent", "Income"])
            
            return has_ytd and has_budget and has_common_metric
        except Exception:
            return False

    def _normalize_date(self, val):
        """Convert various header values to a standard Month-Year string."""
        if pd.isna(val):
            return "Unknown"
        if isinstance(val, (pd.Timestamp, datetime.datetime)):
            return val.strftime("%b-%y")
        s = str(val).strip()
        # Handle "Jan-25" or "2024-12-31" etc.
        try:
            return pd.to_datetime(s).strftime("%b-%y")
        except:
            return s

    def process(self, file_path: Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Process all visible sheets into a unified long-format DataFrame."""
        self.clear_quality_issues()
        
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        visible_sheets = [s.title for s in wb._sheets if s.sheet_state == 'visible']
        
        if sheet_name and sheet_name in visible_sheets:
            target_sheets = [sheet_name]
        else:
            # Filter out generic template/summary sheets if necessary, 
            # but user said "all visible sheets only" and "each sheet name is the property name"
            target_sheets = [s for s in visible_sheets if s not in ['Portfolio Summary', 'Total Portfolio', 'TEMPLATE']]
        
        all_frames = []
        
        for sheet in target_sheets:
            try:
                df_raw = pd.read_excel(file_path, sheet_name=sheet, header=None, engine="openpyxl")
                if len(df_raw) < 8:
                    continue
                
                header_row = df_raw.iloc[6]
                data_df = df_raw.iloc[7:].copy()
                data_df.columns = [f"col_{i}" for i in range(len(data_df.columns))]
                
                # Add RowOrder to preserve spreadsheet sequence
                data_df["RowOrder"] = range(len(data_df))
                
                # Metric Name (Col 1)
                data_df = data_df[data_df["col_0"].notna()]
                
                def format_metric(val):
                    try:
                        # If it's a pure number (float or int), treat as percentage for valuation
                        if isinstance(val, (int, float)):
                            num = float(val)
                            # Small numbers are typically cap rates/valuation multipliers
                            if 0 < num < 1:
                                perc = num * 100
                                perc_str = f"{int(perc)}" if perc == int(perc) else f"{round(perc, 2)}"
                                return f"Valuation p/unit {perc_str}%"
                    except:
                        pass
                    return str(val).strip()

                data_df["Metric"] = data_df["col_0"].apply(format_metric)
                
                if data_df.empty:
                    continue

                # --- Extract Monthly Actuals (Col 2-13) ---
                actual_months = [self._normalize_date(header_row[i]) for i in range(1, 13)]
                monthly_actuals = data_df[["Metric", "RowOrder"] + [f"col_{i}" for i in range(1, 13)]].copy()
                monthly_actuals.columns = ["Metric", "RowOrder"] + actual_months
                actual_long = monthly_actuals.melt(id_vars=["Metric", "RowOrder"], var_name="Period", value_name="Value")
                
                # --- Extract Monthly Budgets (Col 18-29) ---
                budget_months = [self._normalize_date(header_row[i]) for i in range(17, 29)]
                monthly_budgets = data_df[["Metric", "RowOrder"] + [f"col_{i}" for i in range(17, 29)]].copy()
                
                # USER FEEDBACK: Rows below "Monthly Cash Flow" don't have applicable budgets.
                # Find metrics that are balance sheet items or occupancy items that shouldn't have budgets
                m_cf_series = monthly_budgets['Metric'].str.lower()
                m_cf_found = m_cf_series.str.contains('monthly cash flow', na=False)
                if m_cf_found.any():
                    # Get index of the first occurrence
                    start_nulling = False
                    for idx, row in monthly_budgets.iterrows():
                        if start_nulling:
                            for i in range(17, 29):
                                monthly_budgets.at[idx, f"col_{i}"] = np.nan
                        if 'monthly cash flow' in str(row['Metric']).lower():
                            start_nulling = True
                            
                monthly_budgets.columns = ["Metric", "RowOrder"] + budget_months
                budget_long = monthly_budgets.melt(id_vars=["Metric", "RowOrder"], var_name="Period", value_name="BudgetValue")
                
                # Outer join Actual and Budget on Metric and Period (and RowOrder)
                combined_monthly = pd.merge(actual_long, budget_long, on=["Metric", "Period", "RowOrder"], how="outer")
                combined_monthly["IsYTD"] = False
                
                # --- Extract YTD Totals (Col 14, 15) ---
                ytd_actuals = data_df[["Metric", "RowOrder", "col_13"]].copy()
                ytd_actuals.columns = ["Metric", "RowOrder", "Value"]
                ytd_actuals["Period"] = "YTD"
                ytd_actuals["BudgetValue"] = data_df["col_14"].values
                
                if m_cf_found.any():
                    start_nulling = False
                    for idx, row in ytd_actuals.iterrows():
                        if start_nulling:
                            ytd_actuals.at[idx, "BudgetValue"] = np.nan
                        if 'monthly cash flow' in str(row['Metric']).lower():
                            start_nulling = True
                            
                ytd_actuals["IsYTD"] = True
                
                # --- Combine ---
                sheet_df = pd.concat([combined_monthly, ytd_actuals], ignore_index=True)
                sheet_df["Sheet"] = sheet
                
                # Parse values
                sheet_df["Value"] = sheet_df["Value"].apply(self.parse_money)
                sheet_df["BudgetValue"] = sheet_df["BudgetValue"].apply(self.parse_money)
                
                # Drop rows where both Value and BudgetValue are None (empty rows in Excel)
                sheet_df = sheet_df.dropna(subset=["Value", "BudgetValue"], how="all").reset_index(drop=True)
                
                if not sheet_df.empty:
                    def parse_period(p):
                        if p == "YTD": return pd.NaT
                        try:
                            # Try standard formats
                            for fmt in ("%b-%y", "%b %y", "%Y-%m-%d"):
                                try: return pd.to_datetime(p, format=fmt)
                                except: continue
                            return pd.to_datetime(p, errors='coerce')
                        except:
                            return pd.NaT

                    sheet_df["PeriodParsed"] = sheet_df["Period"].apply(parse_period)
                    all_frames.append(sheet_df)
                
            except Exception as e:
                self.add_quality_issue(f"Error processing sheet '{sheet}': {str(e)}")
        
        if not all_frames:
            return pd.DataFrame(columns=self.get_standardized_columns())
            
        final_df = pd.concat(all_frames, ignore_index=True)
        
        # Rename to match original format
        final_df = final_df.rename(columns={
            "Period": "Month",
            "PeriodParsed": "MonthParsed"
        })
        
        # Add derived columns
        # For YTD rows, MonthParsed is NaT.
        final_df["Property"] = final_df["Sheet"]
        final_df["Year"] = final_df["MonthParsed"].dt.year
        final_df["Month_Name"] = final_df["MonthParsed"].dt.strftime("%B")
        final_df["Is_Negative"] = final_df["Value"] < 0
        
        # Select final columns
        cols = [
            "Sheet", "Property", "Metric", "Month", "MonthParsed", 
            "IsYTD", "Value", "Year", "Month_Name", "Is_Negative",
            "BudgetValue"
        ]
        
        # Ensure only existing columns are selected
        return final_df[[c for c in cols if c in final_df.columns]]

    def validate_format(self, df: pd.DataFrame) -> bool:
        if df.empty:
            raise ValueError("Processed DataFrame is empty.")
        required = ["Sheet", "Metric", "Month", "Value", "BudgetValue"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        return True

    def get_expected_metrics(self) -> List[str]:
        return ["Property Asking Rent", "Gross Scheduled Rent", "EBITDA (NOI)"]
