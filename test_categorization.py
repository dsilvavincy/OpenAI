import pandas as pd
import logging
from src.core.formats.database_t12_processor import DatabaseT12Processor
from src.core.local_analysis import PropertyAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pipeline():
    file_path = r'c:\Users\VINCY\OneDrive - Vincy R Dsilva\VBA\Brendan\AI Project\OpenAI\data\CRES - Portfolio Database.xlsm'
    
    print(f"--- TESTING PIPELINE WITH: {file_path} ---")
    
    # 1. Instantiate Processor
    processor = DatabaseT12Processor()
    
    # 2. Process File
    print("Running processor.process()...")
    try:
        df = processor.process(file_path)
    except Exception as e:
        print(f"PROCESSOR FAILED: {e}")
        return

    print(f"DataFrame Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # 3. Check RowOrder
    if "RowOrder" not in df.columns:
        print("CRITICAL FAIL: RowOrder column MISSING in output DataFrame!")
    else:
        print("PASS: RowOrder column exists.")
        min_row = df["RowOrder"].min()
        max_row = df["RowOrder"].max()
        print(f"RowOrder Range: {min_row} to {max_row}")
        
        # Check specific metric
        check_metrics = ["Asset Management Fees", "Partnership Professional Fees", "Monthly Cash Flow"]
        for m in check_metrics:
            matches = df[df["Metric"].str.contains(m, na=False, case=False)]
            if not matches.empty:
                r_val = matches["RowOrder"].iloc[0]
                print(f"Metric '{m}' found at RowOrder: {r_val}")
            else:
                print(f"Metric '{m}' NOT FOUND.")

    # 4. Run Analysis
    print("\nRunning PropertyAnalyzer._get_budget_variances()...")
    
    monthly_df = df[df["IsYTD"] == False].copy()
    ytd_df = df[df["IsYTD"] == True].copy()
    
    # Initialize with required args
    analyzer = PropertyAnalyzer(monthly_df, ytd_df)
    
    # Mock 'latest_date'
    latest = analyzer._get_latest_month(monthly_df)
    print(f"Latest Month detected: {latest}", flush=True)
    
    variances = analyzer._get_budget_variances(monthly_df) # Logic filters internally
    
    print("\n--- BUDGET VARIANCES ---", flush=True)
    for cat, items in variances.items():
        print(f"\nCATEGORY: {cat}", flush=True)
        for item in items:
            print(f"  - {item['metric']}: {item['variance_pct']}%", flush=True)
            
    print("\n--- TRAILING ANOMALIES ---", flush=True)
    # MUST Use monthly_df to avoid mixed types in sorting
    anomalies = analyzer._get_trailing_anomalies(monthly_df)
    for cat, items in anomalies.items():
        print(f"\nCATEGORY: {cat}", flush=True)
        for item in items:
            print(f"  - {item['metric']} (Dev: {item['deviation_pct']}%)")

if __name__ == "__main__":
    test_pipeline()
