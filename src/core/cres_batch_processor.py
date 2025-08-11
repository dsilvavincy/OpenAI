import re
import pandas as pd
from pathlib import Path

def parse_money(x):
    """Convert Excel-style ($123.45) strings or $1,234 to float."""
    if pd.isna(x): return pd.NA
    s = str(x).strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()$").replace(",", "")
    try:
        return -float(s) if neg else float(s)
    except:
        return pd.NA

ptr_month = re.compile(r"(\d{4}-\d{2}-\d{2})|([A-Za-z]{3}[-/ ]?\d{2,4})|(\d{2}/\d{2}/\d{4})|YTD", re.IGNORECASE)

def tidy_sheet_all(path: Path, sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None, engine="openpyxl")
    header_idx = None
    for i, row in raw.iterrows():
        if any(ptr_month.match(str(cell)) for cell in row):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("No header row with month-like columns found")
    df = raw.iloc[header_idx:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].rename(columns={df.columns[0]: "Metric"})
    df = df[df["Metric"].notna()]
    df = df[~df["Metric"].astype(str).str.contains(ptr_month)]
    df["Metric"] = df["Metric"].astype(str).str.strip()
    def col_to_str(col):
        if isinstance(col, (int, float)) and 25000 < col < 50000:
            try:
                dt = pd.to_datetime('1899-12-30') + pd.to_timedelta(int(col), unit='D')
                return dt.strftime('%Y-%m-%d')
            except Exception:
                return str(col)
        return str(col)
    valid_cols = [col for col in df.columns if col == "Metric" or ptr_month.match(col_to_str(col))]
    rename_map = {col: col_to_str(col) for col in valid_cols if col != "Metric"}
    df = df[valid_cols].rename(columns=rename_map)
    df_long = df.melt(id_vars="Metric", var_name="Month", value_name="Value")
    df_long["Value"] = df_long["Value"].apply(parse_money)
    df_long["IsYTD"] = df_long["Month"].str.upper() == "YTD"
    def parse_month(m):
        if pd.isna(m):
            return pd.NaT
        s = str(m).strip()
        s = re.sub(r"\\s*Actual$", "", s, flags=re.IGNORECASE)
        for fmt in ("%b-%y", "%b-%Y", "%b %y", "%b %Y", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y", "%Y-%m-%d"):
            try:
                dt = pd.to_datetime(s, format=fmt, errors="raise")
                if dt.year < 100:
                    dt = dt.replace(year=dt.year + 2000)
                return dt
            except Exception:
                continue
        try:
            return pd.to_datetime(s, errors="coerce")
        except Exception:
            return pd.NaT
    df_long["MonthParsed"] = df_long["Month"].apply(parse_month)
    df_long["Sheet"] = sheet
    df_long = df_long.dropna(subset=["Value"]).reset_index(drop=True)
    return df_long[["Sheet", "Metric", "Month", "MonthParsed", "IsYTD", "Value"]]

def extract_property(sheet_name):
    return re.sub(r"\s*-?\s*CRES$", "", sheet_name).strip()

def process_cres_workbook(file_path):
    # Accept file path or file-like object (BytesIO)
    if isinstance(file_path, (str, Path)):
        excel_source = Path(file_path)
    else:
        excel_source = file_path  # e.g., BytesIO from Streamlit
    with pd.ExcelFile(excel_source) as xls:
        cres_sheets = [s for s in xls.sheet_names if s.strip().endswith("CRES")]
    frames = []
    for sheet in cres_sheets:
        df = tidy_sheet_all(file_path, sheet)
        df["Property"] = extract_property(sheet)
        frames.append(df)
    if not frames:
        return None, None
    unified_df = pd.concat(frames, ignore_index=True)
    def normalize_month_value(m):
        if pd.isna(m):
            return None
        s = str(m).strip()
        if s.upper() == 'YTD':
            return 'YTD'
        if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            try:
                dt = pd.to_datetime(s, format="%Y-%m-%d", errors="raise")
                return dt.strftime("%Y-%m")
            except Exception:
                pass
        match = re.match(r"^([A-Za-z]+)\s+(\d{4})", s)
        if match:
            s_clean = f"{match.group(1)} {match.group(2)}"
        else:
            s_clean = re.sub(r"\s+(Actual|Estimate|Budget|Forecast|Proj|Projected|Est|Act|Final|Prelim|Preliminary)$", "", s, flags=re.IGNORECASE).strip()
        for fmt in ("%b-%y", "%b-%Y", "%b %y", "%b %Y", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y", "%Y-%m-%d"):
            try:
                dt = pd.to_datetime(s_clean, format=fmt, errors="raise")
                if dt.year < 100:
                    dt = dt.replace(year=dt.year + 2000)
                return dt.strftime("%Y-%m")
            except Exception:
                continue
        try:
            dt = pd.to_datetime(s_clean, errors="coerce")
            if pd.isna(dt):
                return None
            return dt.strftime("%Y-%m")
        except Exception:
            return None
    unified_df['Month'] = unified_df['Month'].apply(normalize_month_value)
    def parse_month_parsed(m):
        if pd.isna(m) or m == 'YTD':
            return pd.NaT
        try:
            return pd.to_datetime(m, format="%Y-%m", errors="coerce")
        except Exception:
            return pd.NaT
    unified_df['MonthParsed'] = unified_df['Month'].apply(parse_month_parsed)
    unified_df['Year'] = unified_df['MonthParsed'].dt.year
    unified_df['Month_Name'] = unified_df['MonthParsed'].dt.strftime('%B')
    unified_df['Is_Negative'] = unified_df['Value'] < 0
    ytd_df = unified_df[unified_df['Month'] == 'YTD'].copy()
    unified_df_no_ytd = unified_df[unified_df['Month'] != 'YTD'].copy()
    if 'IsYTD' in ytd_df.columns:
        ytd_df = ytd_df.drop(columns=['IsYTD'])
    if 'IsYTD' in unified_df_no_ytd.columns:
        unified_df_no_ytd = unified_df_no_ytd.drop(columns=['IsYTD'])
    for prop in ytd_df['Property'].unique():
        prop_rows = unified_df_no_ytd[unified_df_no_ytd['Property'] == prop]
        if not prop_rows.empty:
            max_month = prop_rows['MonthParsed'].max()
            max_month_str = max_month.strftime('%Y-%m') if pd.notna(max_month) else None
            max_year = max_month.year if pd.notna(max_month) else None
            max_month_name = max_month.strftime('%B') if pd.notna(max_month) else None
            idx = ytd_df['Property'] == prop
            ytd_df.loc[idx, 'Month'] = max_month_str
            ytd_df.loc[idx, 'MonthParsed'] = max_month
            ytd_df.loc[idx, 'Year'] = max_year
            ytd_df.loc[idx, 'Month_Name'] = max_month_name
    return unified_df_no_ytd, ytd_df
