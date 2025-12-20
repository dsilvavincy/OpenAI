"""
Database T12 Workbook Processor

Handles the "Portfolio Database" format where:
1. Financials are in a sheet named "[Property]-Fin"
2. Budgets are in a sheet named "[Property]-Bgt"
3. Data is structured as a time-series database (Metrics in Col 1, Dates in Col 2+)
"""
import pandas as pd
import numpy as np
import openpyxl
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from .base_processor import BaseFormatProcessor

class DatabaseT12Processor(BaseFormatProcessor):
    """
    Processor for CRES Portfolio Database format.
    """
    
    def __init__(self):
        super().__init__(
            format_name="Database_T12_Workbook",
            format_description="Dynamic database format with separated -Fin and -Bgt sheets"
        )
    
    def can_process(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """
        Check if file follows the Database T12 format (contains *-Fin and *-Bgt sheets).
        """
        try:
            # If file-like object, reset pointer
            if hasattr(file_path, 'seek'):
                file_path.seek(0)
            wb = openpyxl.load_workbook(file_path, read_only=True, keep_links=False)
            sheet_names = wb.sheetnames
            wb.close()
            
            # Check for at least one pair of matching -Fin and -Bgt sheets
            fin_sheets = [s for s in sheet_names if s.endswith("-Fin")]
            if not fin_sheets:
                return False
                
            for fin in fin_sheets:
                base_name = fin[:-4] # Remove "-Fin"
                if f"{base_name}-Bgt" in sheet_names:
                    return True
            
            return False
            
        except Exception:
            return False

    def process(self, file_path: Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Process the workbook and return a unified DataFrame with Actuals, Budgets, and YTD.
        """
        # If file-like object, reset pointer
        if hasattr(file_path, 'seek'):
            file_path.seek(0)
            
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        all_sheets = wb.sheetnames
        
        # Identify pairs
        pairs = []
        for s in all_sheets:
            if s.endswith("-Fin"):
                base_name = s[:-4]
                bgt_sheet = f"{base_name}-Bgt"
                if bgt_sheet in all_sheets:
                    pairs.append((base_name, s, bgt_sheet))
        
        if not pairs:
            wb.close()
            raise ValueError("No valid Property-Fin/Property-Bgt sheet pairs found.")
            
        final_frames = []
        
        for property_name, fin_sheet, bgt_sheet in pairs:
            # --- Process Financials (Actuals) ---
            if hasattr(file_path, 'seek'):
                file_path.seek(0)
            df_fin = pd.read_excel(file_path, sheet_name=fin_sheet, header=None, engine='openpyxl')
            if len(df_fin) < 8:
                continue
                
            # Header is Row 7 (Index 6)
            header_row = df_fin.iloc[6]
            # Verify Header Content (Col 0 should imply Metric)
            if not (isinstance(header_row[0], str) and ("Actuals" in header_row[0] or "Metric" in header_row[0])):
                # Try to find header if not exactly at 7? User said row 7. Assume row 7.
                pass

            data_fin = df_fin.iloc[7:].copy()
            
            # Identify Date Columns (Col 1 onwards)
            # Filter columns that parse to datetime
            date_col_map = {} # {col_idx: datetime}
            for idx, val in enumerate(header_row):
                if idx == 0: continue # Metric column
                dt = self._parse_header_date(val)
                if dt:
                    date_col_map[idx] = dt
            
            if not date_col_map:
                continue
                
            # Rename columns: Col 0 -> Metric, others -> Date
            cols = list(data_fin.columns)
            rename_dict = {cols[0]: "Metric"}
            for idx, dt in date_col_map.items():
                rename_dict[cols[idx]] = dt
            
            # Keep only Metric + Date columns
            keep_cols = [cols[i] for i in [0] + list(date_col_map.keys())]
            data_fin = data_fin[keep_cols].rename(columns=rename_dict)
            
            # Drop rows with empty Metric
            data_fin = data_fin.dropna(subset=["Metric"])
            
            # Melt Actuals
            actual_long = data_fin.melt(id_vars="Metric", var_name="Period", value_name="Value")
            actual_long["Value"] = pd.to_numeric(actual_long["Value"], errors='coerce').fillna(0)
            
            # --- Process Budgets ---
            if hasattr(file_path, 'seek'):
                file_path.seek(0)
            df_bgt = pd.read_excel(file_path, sheet_name=bgt_sheet, header=None, engine='openpyxl')
            # Assuming aligned structure, but safe to parse dates again
            header_row_bgt = df_bgt.iloc[6]
            data_bgt = df_bgt.iloc[7:].copy()
            
            date_col_map_bgt = {}
            for idx, val in enumerate(header_row_bgt):
                if idx == 0: continue
                dt = self._parse_header_date(val)
                if dt:
                    date_col_map_bgt[idx] = dt
            
            cols_bgt = list(data_bgt.columns)
            rename_dict_bgt = {cols_bgt[0]: "Metric"}
            for idx, dt in date_col_map_bgt.items():
                rename_dict_bgt[cols_bgt[idx]] = dt
                
            keep_cols_bgt = [cols_bgt[i] for i in [0] + list(date_col_map_bgt.keys())]
            data_bgt = data_bgt[keep_cols_bgt].rename(columns=rename_dict_bgt)
            
            # Drop rows with empty Metric
            data_bgt = data_bgt.dropna(subset=["Metric"])
            
            # Apply Budget Nullification Logic (Monthly Cash Flow cutoff)
            # Find "Monthly Cash Flow"
            m_cf_series = data_bgt['Metric'].astype(str).str.lower()
            m_cf_found = m_cf_series.str.contains('monthly cash flow', na=False)
            
            if m_cf_found.any():
                cutoff_index = m_cf_found.idxmax() # Get index of first True
                # Nullify all values for rows numerically > cutoff_index
                rows_to_null = data_bgt.index[data_bgt.index > cutoff_index]
                if not rows_to_null.empty:
                    # Set date columns to NaN
                    date_cols_bgt_list = [c for c in data_bgt.columns if c != "Metric"]
                    data_bgt.loc[rows_to_null, date_cols_bgt_list] = np.nan

            # Melt Budgets
            budget_long = data_bgt.melt(id_vars="Metric", var_name="Period", value_name="BudgetValue")
            budget_long["BudgetValue"] = pd.to_numeric(budget_long["BudgetValue"], errors='coerce')
            
            # --- Merge ---
            # Merge on Metric and Period
            combined = pd.merge(actual_long, budget_long, on=["Metric", "Period"], how="outer")
            combined["Property"] = property_name
            combined["Sheet"] = fin_sheet # Metadata
            combined["IsYTD"] = False
            
            # Ensure Period is datetime for .dt accessor
            combined["Period"] = pd.to_datetime(combined["Period"], errors='coerce')
            
            combined["MonthParsed"] = combined["Period"]
            combined["Month"] = combined["Period"].dt.month
            combined["Year"] = combined["Period"].dt.year
            combined["Month_Name"] = combined["Period"].dt.month_name()
            
            # --- Calculate YTD ---
            # We must calculate YTD for the LATEST available month (or all months?)
            # Standard processor generally provides YTD as a separate "Period='YTD'" row.
            
            if not combined.empty:
                # Find latest date in the data
                valid_dates = [d for d in combined['Period'].unique() if isinstance(d, datetime.datetime)]
                if valid_dates:
                    latest_date = max(valid_dates)
                    current_year = latest_date.year
                    
                    # Filter for current year
                    cy_data = combined[
                        combined['Period'].apply(lambda x: isinstance(x, datetime.datetime) and x.year == current_year)
                    ]
                    
                    # Group by Metric and sum, ensure numeric only
                    # Warning: grouping on Metric can be tricky if names are not unique or messy.
                    # We assume names are standard.
                    ytd_values = cy_data.groupby("Metric")[["Value", "BudgetValue"]].sum().reset_index()
                    ytd_values["Period"] = "YTD"
                    ytd_values["Property"] = property_name
                    ytd_values["Sheet"] = fin_sheet
                    ytd_values["Sheet"] = fin_sheet
                    ytd_values["IsYTD"] = True
                    ytd_values["MonthParsed"] = pd.NaT
                    ytd_values["Month"] = np.nan
                    ytd_values["Year"] = np.nan
                    ytd_values["Month_Name"] = None
                    
                    # Combine Monthly + YTD
                    period_df = pd.concat([combined, ytd_values], ignore_index=True)
                    final_frames.append(period_df)
                else:
                    final_frames.append(combined)
            else:
                 final_frames.append(combined)

        wb.close()
        
        if not final_frames:
            return pd.DataFrame()
            
        return pd.concat(final_frames, ignore_index=True)

    def validate_format(self, df: pd.DataFrame) -> bool:
        """Validate processed DataFrame"""
        required = ["Metric", "Period", "Value", "BudgetValue", "Property"]
        if not all(col in df.columns for col in required):
            raise ValueError(f"Missing required columns. Found: {list(df.columns)}")
        return True

    def get_expected_metrics(self) -> List[str]:
        """Return expected metrics"""
        return ["Net Eff. Gross Income", "Total Expense", "EBITDA (NOI)"]

    def _parse_header_date(self, val: Any) -> Optional[datetime.datetime]:
        """Attempt to parse openpyxl cell value as datetime"""
        if isinstance(val, datetime.datetime):
            return val
        if isinstance(val, str):
            try:
                # Try common formats
                return pd.to_datetime(val).to_pydatetime()
            except:
                pass
        return None
