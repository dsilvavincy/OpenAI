import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.format_registry import process_file

def verify():
    file_path = Path(r'C:\Users\VINCY\OneDrive - Vincy R Dsilva\VBA\Brendan\AI Project\OpenAI\data\CRES Monthly Financial Workbook.xlsm')
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return

    print(f"--- Processing {file_path.name} ---")
    try:
        # We specify the format to ensure we use the new one, or let it auto-detect
        df, processor = process_file(file_path)
        print(f"Detected Format: {processor.format_name}")
        
        print("\n--- Property Summary ---")
        properties = df['Sheet'].unique()
        print(f"Total Properties Found: {len(properties)}")
        for prop in properties:
            prop_data = df[df['Sheet'] == prop]
            metrics = prop_data['Metric'].nunique()
            print(f"- {prop}: {metrics} metrics, {len(prop_data)} rows")

        print("\n--- Sample Data (Solas Glendale - Monthly Actuals vs Budgets) ---")
        # Check a metric that usually has budgets, like Total Expense
        metrics_to_check = ['Property Asking Rent', 'Total Expense', 'Net Eff. Gross Income', 'EBITDA (NOI)']
        for metric in metrics_to_check:
            sample = df[(df['Sheet'] == 'Solas Glendale') & (df['Metric'] == metric) & (df['IsYTD'] == False)].head(3)
            if not sample.empty:
                print(f"\nMetric: {metric}")
                print(sample[['Month', 'Value', 'BudgetValue']].to_string(index=False))
            
        print("\n--- Metrics with Non-Zero Budgets (Solas Glendale) ---")
        non_zero_budgets = df[(df['Sheet'] == 'Solas Glendale') & (df['BudgetValue'] != 0) & (df['IsYTD'] == False)]
        if not non_zero_budgets.empty:
            print(f"Found {non_zero_budgets['Metric'].nunique()} metrics with monthly budgets.")
            print("First 5 metrics with budgets:")
            print(non_zero_budgets['Metric'].unique()[:5])
        else:
            print("No non-zero monthly budgets found!")

        # Save to CSV for full inspection
        output_file = "long_format_preview.csv"
        df.to_csv(output_file, index=False)
        print(f"\nFull long-format data saved to {output_file}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    verify()
