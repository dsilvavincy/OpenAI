"""
Data preprocessing for T12 Excel files
Enhanced version based on robust Excel parsing
"""
import re
import pandas as pd
from pathlib import Path

# Regex pattern to match month format like "Jul 2024"
ptr_month = re.compile(r"^[A-Za-z]{3} \d{4}$")

def parse_money(x):
    """Convert Excel-style ($123.45) strings or $1,234 to float."""
    if pd.isna(x): 
        return pd.NA
    s = str(x).strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()$").replace(",", "")
    try:
        return -float(s) if neg else float(s)
    except:
        return pd.NA

def tidy_sheet_all(excel_path, sheet_name=None):
    """
    Convert wide-format Excel sheet to long-format tidy dataframe.
    
    Args:
        excel_path: Path to Excel file (string or Path object)
        sheet_name: Name of sheet to process (defaults to first sheet)
    
    Returns:
        pd.DataFrame: Long-format DataFrame with columns [Sheet, Metric, Month, MonthParsed, IsYTD, Value]
    """
    try:
        # Convert to Path object if string
        path = Path(excel_path) if isinstance(excel_path, str) else excel_path
        
        # Read Excel file to get sheet names if not specified
        if sheet_name is None:
            excel_file = pd.ExcelFile(path, engine="openpyxl")
            sheet_name = excel_file.sheet_names[0]  # Use first sheet
        
        # Read raw data without headers
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")
        
        # 1. Find header row (first row with any month label)
        header_rows = raw[raw.apply(lambda r: r.astype(str).str.contains(ptr_month).any(), axis=1)]
        if header_rows.empty:
            raise ValueError("No header row with month format found. Expected format: 'Jul 2024', 'Aug 2024', etc.")
        
        header_idx = header_rows.index[0]

        # 2. Slice from header row onwards
        df = raw.iloc[header_idx:].reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.iloc[1:].rename(columns={df.columns[0]: "Metric"})

        # 3. Remove empty rows and repeated headers
        df = df[df["Metric"].notna()]
        df = df[~df["Metric"].astype(str).str.contains(ptr_month)]
        df["Metric"] = df["Metric"].astype(str).str.strip()

        # 4. Unpivot months into long format
        # Get all columns except Metric that contain data
        month_columns = [col for col in df.columns if col != "Metric" and not pd.isna(col)]
        df_long = df.melt(id_vars="Metric", value_vars=month_columns, var_name="Month", value_name="Value")

        # 5. Parse money values
        df_long["Value"] = df_long["Value"].apply(parse_money)

        # 6. Separate YTD as flag and parse dates
        df_long["IsYTD"] = df_long["Month"].astype(str).str.upper() == "YTD"
        df_long["MonthParsed"] = pd.to_datetime(df_long["Month"], format="%b %Y", errors="coerce")

        # 7. Add sheet name for traceability
        df_long["Sheet"] = sheet_name

        # 8. Drop empty rows
        df_long = df_long.dropna(subset=["Value"]).reset_index(drop=True)

        # 9. Add additional helpful columns for analysis
        df_long["Year"] = df_long["MonthParsed"].dt.year
        df_long["Month_Name"] = df_long["MonthParsed"].dt.strftime("%b")
        df_long["Is_Negative"] = df_long["Value"] < 0

        return df_long[["Sheet", "Metric", "Month", "MonthParsed", "IsYTD", "Value", "Year", "Month_Name", "Is_Negative"]]
        
    except Exception as e:
        raise ValueError(f"Error processing T12 file: {str(e)}")

def validate_t12_format(df):
    """
    Validate that the processed DataFrame has expected T12 structure
    """
    required_columns = ["Sheet", "Metric", "Month", "Value"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    if df.empty:
        raise ValueError("No data found in processed DataFrame")
    
    # Check for expected T12 metrics (basic validation)
    common_t12_metrics = [
        "Property Asking Rent", "Effective Rental Income", "Gross Scheduled Rent",
        "Vacancy", "Loss to lease", "Concessions", "Delinquency"
    ]
    
    found_metrics = df["Metric"].str.contains("|".join(common_t12_metrics), case=False).any()
    if not found_metrics:
        print("Warning: No common T12 metrics found. Please verify data format.")
    
    return True

# Legacy function name for backward compatibility
def extract_year(month_str):
    """Extract year from month string like 'Jul 2024'"""
    try:
        return month_str.split()[-1]
    except:
        return None

def extract_month_name(month_str):
    """Extract month name from month string like 'Jul 2024'"""
    try:
        return month_str.split()[0]
    except:
        return None
