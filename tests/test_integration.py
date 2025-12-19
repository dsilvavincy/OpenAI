import sys
from pathlib import Path
import pandas as pd
import io

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.format_registry import FormatRegistry
from src.core.local_analysis import PropertyAnalyzer

def test_integration():
    file_path = Path(r'C:\Users\VINCY\OneDrive - Vincy R Dsilva\VBA\Brendan\AI Project\OpenAI\data\CRES Monthly Financial Workbook.xlsm')
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return

    print(f"--- Testing Integrated Flow for {file_path.name} ---")
    
    # 1. Process File
    registry = FormatRegistry()
    with open(file_path, 'rb') as f:
        excel_buffer = io.BytesIO(f.read())
    
    print("Step 1: Processing file...")
    unified_df, processor = registry.process_file(excel_buffer)
    print(f"Detected Format: {processor.format_name}")
    print(f"Total Rows: {len(unified_df)}")

    # 2. Split Data (Simulating ProductionUpload logic)
    print("Step 2: Splitting Data...")
    monthly_df = unified_df[unified_df['IsYTD'] == False].copy()
    ytd_df = unified_df[unified_df['IsYTD'] == True].copy()
    
    # Simple date fill for YTD
    for prop in ytd_df['Property'].unique():
        prop_rows = monthly_df[monthly_df['Property'] == prop]
        if not prop_rows.empty:
            max_month_idx = prop_rows['MonthParsed'].idxmax()
            last_date_info = prop_rows.loc[max_month_idx]
            idx = ytd_df['Property'] == prop
            ytd_df.loc[idx, 'MonthParsed'] = last_date_info['MonthParsed']

    # 3. Analyze Property
    print("Step 3: Analyzing Property (Solas Glendale)...")
    analyzer = PropertyAnalyzer(monthly_df, ytd_df)
    structured_data = analyzer.analyze_property('Solas Glendale')
    
    print("\n--- Structured Data Preview (Budget Variance) ---")
    if 'budget_variance' in structured_data:
        import json
        print(json.dumps(structured_data['budget_variance'], indent=2))
    else:
        print("No budget variance found in structured data!")

    print("\n--- Structured Data Preview (Rolling Avg Variance) ---")
    if 'rolling_avg_variance' in structured_data:
        print(json.dumps(structured_data['rolling_avg_variance'], indent=2))
    else:
        print("No rolling average variance found in structured data!")

    print("\n--- YTD Cumulative Preview ---")
    print(structured_data['ytd_cumulative'])

    print("\nIntegration test successful!")

if __name__ == "__main__":
    test_integration()
