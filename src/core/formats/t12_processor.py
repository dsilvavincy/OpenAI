"""
T12 Monthly Financial Format Processor

Handles T12 monthly property financial data with monthly columns.
Refactored from the original preprocessing logic to fit the plugin architecture.
"""
import re
import pandas as pd
from pathlib import Path
from typing import Optional, List
from .base_processor import BaseFormatProcessor

class T12MonthlyFinancialProcessor(BaseFormatProcessor):
    """
    Processor for T12 Monthly Financial format.
    
    Expected format:
    - Excel file with monthly columns (Jul 2024, Aug 2024, etc.)
    - Metrics in rows (Property Asking Rent, NOI, etc.)
    - Optional YTD column
    """
    
    def __init__(self):
        super().__init__(
            format_name="T12_Monthly_Financial",
            format_description="T12 Monthly Property Financial Reports with monthly columns"
        )
        # Regex pattern to match month format like "Jul 2024"
        self.month_pattern = re.compile(r"^[A-Za-z]{3} \d{4}$")
    
    def can_process(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """
        Check if file contains T12 monthly format by looking for month headers.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Optional sheet name
            
        Returns:
            bool: True if file appears to be T12 monthly format
        """
        try:
            # Read Excel file to check format
            if sheet_name is None:
                excel_file = pd.ExcelFile(file_path, engine="openpyxl")
                sheet_name = excel_file.sheet_names[0]
            
            # Read raw data without headers to examine structure
            raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="openpyxl")
            
            # Look for month pattern in any row
            month_found = raw.apply(
                lambda r: r.astype(str).str.contains(self.month_pattern).any(), 
                axis=1
            ).any()
            
            # Look for common T12 metrics
            t12_metrics_found = raw.apply(
                lambda r: r.astype(str).str.contains(
                    "Effective Rental Income|Gross Scheduled Rent|NOI|EBITDA|Vacancy|Property Asking Rent", 
                    case=False
                ).any(),
                axis=1
            ).any()
            
            return month_found and t12_metrics_found
            
        except Exception as e:
            print(f"Error checking T12 format: {str(e)}")
            return False
    
    def process(self, file_path: Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Process T12 monthly financial file into standardized format.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Optional sheet name
            
        Returns:
            pd.DataFrame: Standardized long-format DataFrame
        """
        try:
            self.clear_quality_issues()
            
            # Convert to Path object if string
            path = Path(file_path) if isinstance(file_path, str) else file_path
            
            # Read Excel file to get sheet names if not specified
            if sheet_name is None:
                excel_file = pd.ExcelFile(path, engine="openpyxl")
                sheet_name = excel_file.sheet_names[0]
            
            # Read raw data without headers
            raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")
            
            # 1. Find header row (first row with any month label)
            header_rows = raw[raw.apply(lambda r: r.astype(str).str.contains(self.month_pattern).any(), axis=1)]
            if header_rows.empty:
                raise ValueError("No header row with month format found. Expected format: 'Jul 2024', 'Aug 2024', etc.")
            
            header_idx = header_rows.index[0]
            
            # 2. Slice from header row onwards
            df = raw.iloc[header_idx:].reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df.iloc[1:].rename(columns={df.columns[0]: "Metric"})
            
            # 3. Remove empty rows and repeated headers
            df = df[df["Metric"].notna()]
            df = df[~df["Metric"].astype(str).str.contains(self.month_pattern)]
            df["Metric"] = df["Metric"].astype(str).str.strip()
            
            # 4. Unpivot months into long format
            month_columns = [col for col in df.columns if col != "Metric" and not pd.isna(col)]
            df_long = df.melt(id_vars="Metric", value_vars=month_columns, var_name="Period", value_name="Value")
            
            # 5. Parse money values
            df_long["Value"] = df_long["Value"].apply(self.parse_money)
            
            # 6. Separate YTD as flag and parse dates
            df_long["IsYTD"] = df_long["Period"].astype(str).str.upper() == "YTD"
            
            # Only parse PeriodParsed for non-YTD rows
            df_long["PeriodParsed"] = pd.NaT  # Initialize with NaT (Not a Time)
            non_ytd_mask = ~df_long["IsYTD"]
            df_long.loc[non_ytd_mask, "PeriodParsed"] = pd.to_datetime(
                df_long.loc[non_ytd_mask, "Period"], 
                format="%b %Y", 
                errors="coerce"
            )
            
            # 7. Add sheet name for traceability
            df_long["Sheet"] = sheet_name
            
            # 8. Drop empty rows
            df_long = df_long.dropna(subset=["Value"]).reset_index(drop=True)
            
            # 9. Add T12-specific helpful columns
            df_long["Year"] = df_long["PeriodParsed"].dt.year
            df_long["Month_Name"] = df_long["PeriodParsed"].dt.strftime("%b")
            df_long["Is_Negative"] = df_long["Value"] < 0
            
            # 10. Data quality checks
            self._perform_quality_checks(df_long)
            
            # Return with standardized columns first, then format-specific ones
            standard_columns = ["Sheet", "Metric", "Period", "PeriodParsed", "IsYTD", "Value"]
            t12_specific_columns = ["Year", "Month_Name", "Is_Negative"]
            
            return df_long[standard_columns + t12_specific_columns]
            
        except Exception as e:
            raise ValueError(f"Error processing T12 Monthly Financial file: {str(e)}")
    
    def validate_format(self, df: pd.DataFrame) -> bool:
        """
        Validate that the processed DataFrame has expected T12 structure.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Check required columns
        required_columns = ["Sheet", "Metric", "Period", "Value"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        if df.empty:
            raise ValueError("No data found in processed DataFrame")
        
        # Check for expected T12 metrics
        expected_metrics = self.get_expected_metrics()
        found_metrics = df["Metric"].str.contains("|".join(expected_metrics), case=False).any()
        
        if not found_metrics:
            self.add_quality_issue("No common T12 metrics found. Please verify data format.")
            print("Warning: No common T12 metrics found. Please verify data format.")
        
        return True
    
    def get_expected_metrics(self) -> List[str]:
        """
        Get list of expected T12 metrics.
        
        Returns:
            List[str]: Common T12 metric patterns
        """
        return [
            "Property Asking Rent",
            "Effective Rental Income", 
            "Gross Scheduled Rent",
            "Vacancy",
            "Loss to lease",
            "Concessions",
            "Delinquency",
            "EBITDA",
            "NOI",
            "Total Expense",
            "Management Fee",
            "Property Taxes",
            "Insurance",
            "Monthly Cash Flow"
        ]
    
    def _perform_quality_checks(self, df: pd.DataFrame):
        """
        Perform T12-specific data quality checks.
        
        Args:
            df: Processed DataFrame
        """
        # Check for missing values in critical columns
        missing_metrics = df["Metric"].isna().sum()
        missing_periods = df["Period"].isna().sum()
        missing_values = df["Value"].isna().sum()
        
        if missing_metrics > 0:
            self.add_quality_issue(f"Missing Metric values: {missing_metrics}")
        if missing_periods > 0:
            self.add_quality_issue(f"Missing Period values: {missing_periods}")
        if missing_values > 0:
            self.add_quality_issue(f"Missing Value entries: {missing_values}")
        
        # Check for invalid dates (excluding YTD rows)
        non_ytd_rows = df[~df["IsYTD"]]
        invalid_dates = non_ytd_rows["PeriodParsed"].isna().sum()
        if invalid_dates > 0:
            self.add_quality_issue(f"Invalid PeriodParsed dates (non-YTD): {invalid_dates}")
        
        # Report YTD rows separately for info
        ytd_count = df["IsYTD"].sum()
        if ytd_count > 0:
            self.add_quality_issue(f"YTD rows (expected to have null PeriodParsed): {ytd_count}")
        
        # Log quality issues
        self.log_quality_issues()
