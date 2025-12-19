import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path.cwd()))

from src.core.local_analysis import PropertyAnalyzer

def verify_ballantyne():
    csv_path = 'exports/CRES Monthly Financial Workbook_monthly_20251219_120936.csv'
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found")
        return

    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    df['MonthParsed'] = pd.to_datetime(df['MonthParsed'])
    
    analyzer = PropertyAnalyzer(df, pd.DataFrame())
    
    print("Analyzing Ballantyne...")
    result = analyzer.analyze_property('Ballantyne')
    
    print("-" * 30)
    print(f"Property: {result['property_name']}")
    print(f"Identified Report Period: {result['report_period']}")
    print(f"Identified Prior Period: {result['prior_period']}")
    
    if 'debug' in result:
        print(f"Detection Reason: {result['debug'].get('detection_reason')}")
    
    current_metrics = result['current_month']
    print("\nKey Metrics for Identified Period:")
    print(f"Effective Gross Income: {current_metrics.get('net_eff_gross_income')}")
    print(f"Total Expense: {current_metrics.get('total_expense')}")
    print(f"EBITDA (NOI): {current_metrics.get('ebitda_noi')}")
    
    # Check what data exists for Nov and Dec
    print("\nRaw Data Inspection (Nov/Dec 2025):")
    target_months = ['2025-11-01', '2025-12-01']
    metrics = ['Net Eff. Gross Income', 'Total Expense', 'EBITDA (NOI)']
    
    for m in target_months:
        print(f"\n{m}:")
        for metric in metrics:
            row = df[(df['Property'] == 'Ballantyne') & 
                     (df['MonthParsed'] == m) & 
                     (df['Metric'] == metric)]
            val = row['Value'].iloc[0] if not row.empty else "N/A"
            budget = row['BudgetValue'].iloc[0] if not row.empty else "N/A"
            print(f"  {metric}: Actual={val}, Budget={budget}")

if __name__ == "__main__":
    verify_ballantyne()
