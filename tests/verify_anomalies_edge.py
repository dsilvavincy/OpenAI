import pandas as pd
import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path.cwd()))

from src.core.local_analysis import PropertyAnalyzer

def verify_edge_anomalies():
    csv_path = 'exports/CRES Monthly Financial Workbook_monthly_20251219_120936.csv'
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found")
        return

    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    df['MonthParsed'] = pd.to_datetime(df['MonthParsed'])
    
    # Analyze Edge on 65th
    property_name = "Edge on 65th"
    print(f"Analyzing {property_name}...")
    
    # Check if property exists in data
    props = df['Property'].unique()
    if property_name not in props:
        print(f"Property '{property_name}' not found. Available: {props}")
        # Try partial match
        for p in props:
            if "Edge" in str(p):
                print(f"Did you mean '{p}'?")
                property_name = p
                break
    
    analyzer = PropertyAnalyzer(df, pd.DataFrame())
    result = analyzer.analyze_property(property_name)
    
    print("-" * 30)
    print(f"Report Period: {result['report_period']}")
    print("-" * 30)
    
    anomalies = result.get('metric_anomalies', [])
    print(f"Anomalies Found: {len(anomalies)}")
    
    if anomalies:
        for idx, a in enumerate(anomalies):
            print(f"{idx+1}. {a['metric']} ({a['type']}): {a['current']} vs {a['prior']} (Diff: {a.get('abs_change', 0)})")
    else:
        print("No anomalies found by scanner.")
        
    # Manual check of a known potential anomaly if lists is empty
    # Let's print top 5 MoM changes just to see what the raw data looks like
    print("\n--- Top 5 Raw MoM Changes (Diagnostic) ---")
    current_metrics = analyzer._filter_by_property(df, property_name)
    latest = result['current_month']
    
    # We can't access private methods easily, so let's just inspect the result's mom_changes
    mom = result.get('mom_changes', {})
    if mom:
        sorted_mom = sorted(mom.items(), key=lambda x: abs(x[1].get('absolute_change', 0)), reverse=True)[:5]
        for k, v in sorted_mom:
            print(f"{k}: {v}")

if __name__ == "__main__":
    verify_edge_anomalies()
