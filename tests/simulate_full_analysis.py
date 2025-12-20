import sys
from pathlib import Path
import pandas as pd
import traceback
from rich import print

# Add src to path
sys.path.append(str(Path.cwd()))

from src.core.format_registry import process_file
from src.core.local_analysis import PropertyAnalyzer

FILE_PATH = "data/CRES - Portfolio Database.xlsm"

def simulate_pipeline():
    print(f"Loading {FILE_PATH} with DatabaseT12Processor...")
    try:
        df, processor = process_file(Path(FILE_PATH), format_name='Database_T12_Workbook')
        print(f"Loaded DataFrame: {df.shape} rows.")
    except Exception as e:
        print(f"[red]Failed to process file: {e}[/red]")
        traceback.print_exc()
        return

    # Simulate UI Logic: Split Monthly/YTD
    # In production_upload.py, we do:
    monthly_df = df[df['IsYTD'] == False].copy()
    ytd_df = df[df['IsYTD'] == True].copy()
    
    # UI Logic: Backfill date info for YTD (mimicking production_upload.py)
    # The actual production_upload.py does this:
    # for prop in ytd_df['Property'].unique():
    #     prop_rows = monthly_df[monthly_df['Property'] == prop]
    #     if not prop_rows.empty:
    #         max_month_idx = prop_rows['MonthParsed'].idxmax()
    #         last_date_info = prop_rows.loc[max_month_idx]
    #         idx = ytd_df['Property'] == prop
    #         # In our corrected DatabaseT12Processor, Month/Year/Month_Name are already present in monthly_df
    #         # But YTD rows have them as NaN.
    #         ytd_df.loc[idx, 'Month'] = last_date_info['Month']
    #         ytd_df.loc[idx, 'MonthParsed'] = last_date_info['MonthParsed']
    #         ytd_df.loc[idx, 'Year'] = last_date_info['Year']
    #         ytd_df.loc[idx, 'Month_Name'] = last_date_info['Month_Name']
    
    # We should replicate this to be sure
    print("Backfilling YTD date metadata...")
    for prop in ytd_df['Property'].unique():
        prop_rows = monthly_df[monthly_df['Property'] == prop]
        if not prop_rows.empty:
             # Filter out NaT in MonthParsed if any
            valid_dates = prop_rows[pd.notna(prop_rows['MonthParsed'])]
            if not valid_dates.empty:
                max_month_idx = valid_dates['MonthParsed'].idxmax()
                last_date_info = monthly_df.loc[max_month_idx]
                
                idx = ytd_df['Property'] == prop
                ytd_df.loc[idx, 'Month'] = last_date_info['Month']
                ytd_df.loc[idx, 'MonthParsed'] = last_date_info['MonthParsed']
                ytd_df.loc[idx, 'Year'] = last_date_info['Year']
                # Month_Name might be object
                ytd_df.loc[idx, 'Month_Name'] = last_date_info['Month_Name']

    print("Initializing PropertyAnalyzer...")
    analyzer = PropertyAnalyzer(monthly_df, ytd_df)
    
    properties = sorted(df['Property'].unique())
    print(f"Found {len(properties)} properties. Testing analysis for each...")
    
    failures = []
    
    for i, prop in enumerate(properties):
        print(f"[{i+1}/{len(properties)}] Analyzing: {prop}...", end="")
        try:
            result = analyzer.analyze_property(prop)
            # Access keys to trigger potential lazy eval issues
            _ = result['metric_anomalies']
            _ = result['current_month']
            print("[green]OK[/green]")
        except Exception as e:
            print(f"[red]FAILED[/red]")
            print(f"Error analyzing {prop}: {str(e)}")
            # traceback.print_exc()
            failures.append((prop, str(e)))
            
    if failures:
        print(f"\n[red]Encountered {len(failures)} failures![/red]")
        for f in failures:
            print(f"- {f[0]}: {f[1]}")
    else:
        print("\n[green]All properties analyzed successfully![/green]")

if __name__ == "__main__":
    simulate_pipeline()
