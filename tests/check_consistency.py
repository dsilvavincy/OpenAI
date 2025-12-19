import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.format_registry import process_file

def consistency_check():
    file_path = Path(r'C:\Users\VINCY\OneDrive - Vincy R Dsilva\VBA\Brendan\AI Project\OpenAI\data\CRES Monthly Financial Workbook.xlsm')
    sheet_name = 'Solas Glendale'
    metric_name = 'Property Asking Rent'
    
    # 1. Read Raw
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="openpyxl")
    # Row 7 is header, Row 8 is first data row
    # Actuals Index 1-12
    raw_actuals = df_raw.iloc[7, 1:13].tolist()
    # Budgets Index 17-28
    raw_budgets = df_raw.iloc[7, 17:29].tolist()
    
    print(f"--- Raw Values for {metric_name} ({sheet_name}) ---")
    print(f"Actuals (Col 2-13): {raw_actuals}")
    print(f"Budgets (Col 18-29): {raw_budgets}")
    
    # 2. Read Processed
    df, _ = process_file(file_path)
    processed = df[(df['Sheet'] == sheet_name) & (df['Metric'] == metric_name) & (df['IsYTD'] == False)]
    # Sort by MonthParsed
    processed = processed.sort_values('MonthParsed')
    
    print(f"\n--- Processed Values for {metric_name} ({sheet_name}) ---")
    print(processed[['Month', 'Value', 'BudgetValue']].to_string(index=False))
    
    # 3. Quick Match Check
    # We expect the values to match
    # Note: processed might have more/different months if Actuals and Budgets didn't overlap perfectly
    
if __name__ == "__main__":
    consistency_check()
