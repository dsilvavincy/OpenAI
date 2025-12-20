
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.report_generator import ReportGenerator
from src.core.local_analysis import PropertyAnalyzer

def test_kpi_table_generation():
    rg = ReportGenerator()
    
    mock_monthly = {
        "Net Eff. Gross Income": 100000,
        "Total Expense": 45000,
        "EBITDA": 55000
    }
    mock_ytd = {
        "Net Eff. Gross Income": 1200000,
        "Total Expense": 540000,
        "EBITDA": 660000
    }
    
    html = rg.generate_combined_kpi_table(mock_monthly, mock_ytd)
    print("KPI Table HTML Length:", len(html))
    assert "Total Monthly Income" in html
    assert "Monthly Net Operating Income" in html
    assert "45.0%" in html # Monthly Expense Ratio check (45000/100000)

def test_financial_table_generation():
    rg = ReportGenerator()
    
    # Create simple dataframe
    data = {
        "Metric": ["Physical Occupancy", "Net Rental Income"],
        "Jan 2024": [0.95, 50000],
        "Feb 2024": [0.88, 51000]
    }
    df = pd.DataFrame(data).set_index("Metric")
    
    html = rg.generate_financial_table(df)
    print("Financial Table HTML Length:", len(html))
    assert "val-green" in html # 0.95 occ should be green
    assert "val-yellow" in html # 0.88 occ should be yellow

def test_analyzer_variances():
    # Mock data for analyzer
    data = []
    metrics = ["Rental Income", "Payroll Expense", "Marketing"]
    
    # Current month
    data.append({"Period": "2024-03-01", "Metric": "Rental Income", "Value": 90000, "BudgetValue": 100000}) # -10% -> Variance? No, exact 10%. Need > 10%
    data.append({"Period": "2024-03-01", "Metric": "Payroll Expense", "Value": 15000, "BudgetValue": 10000}) # +50% -> Variance
    data.append({"Period": "2024-03-01", "Metric": "Marketing", "Value": 5000, "BudgetValue": 5000})
    
    # Past data for anomalies
    dates = ["2023-12-01", "2024-01-01", "2024-02-01"]
    vals = [5000, 5000, 5000] # T3 Avg = 5000
    for d, v in zip(dates, vals):
        data.append({"Period": d, "Metric": "Marketing", "Value": v, "BudgetValue": 5000})
        data.append({"Period": d, "Metric": "Rental Income", "Value": 100000, "BudgetValue": 100000})
        data.append({"Period": d, "Metric": "Payroll Expense", "Value": 10000, "BudgetValue": 10000})
        
    df = pd.DataFrame(data)
    df["Period"] = pd.to_datetime(df["Period"])
    df["MonthParsed"] = df["Period"]
    
    # Init with empty mock DFs to satisfy constructor
    # analyzer = PropertyAnalyzer(pd.DataFrame(), pd.DataFrame()) # This was for individual methods
    # For analyze_property, we should pass the df as monthly_df
    
    # We need a proper setup for analyze_property to work.
    # It filters by property_name.
    df["Property"] = "Test Property"
    analyzer = PropertyAnalyzer(df, pd.DataFrame()) # Pass df as monthly
    
    # DEBUG
    print("Analyzer Latest Month:", analyzer._get_latest_month(df))
    
    variances = analyzer._get_budget_variances(df)
    anomalies = analyzer._get_trailing_anomalies(df)
    
    print("Variances Detected:", variances)
    assert any(x['metric'] == 'Payroll Expense' for x in variances['Expenses'])
    
    # NEW: Test full analyze_property
    print("Testing analyze_property integration...")
    try:
        result = analyzer.analyze_property("Test Property")
        print("analyze_property successful!")
        assert "budget_variances" in result
        assert "trailing_anomalies" in result
        assert "expense_ratio" in result
        print("Result Keys validated.")
    except Exception as e:
        print(f"analyze_property failed: {e}")
        raise e
    
    # Rental Income (90k vs 100k) is exactly -10%. Logic was > 0.10. 
    # abs(-0.10) is not > 0.10. So it should NOT be included if strictly >.
    
    # Test Anomalies
    # Marketing current is 5000. T3 avg is 5000. No anomaly.
    # Let's add an anomaly case.
    # New metric: Repairs
    cols = ["Period", "Metric", "Value", "BudgetValue"]
    t3 = [100, 100, 100]
    curr = 500 # 5x spike
    
    extra_rows = []
    for d, v in zip(dates, t3):
        extra_rows.append({"Period": pd.to_datetime(d), "Metric": "Repairs", "Value": v, "BudgetValue": 0})
    extra_rows.append({"Period": pd.to_datetime("2024-03-01"), "Metric": "Repairs", "Value": curr, "BudgetValue": 0})
    
    df2 = pd.concat([df, pd.DataFrame(extra_rows)], ignore_index=True)
    anomalies2 = analyzer._get_trailing_anomalies(df2)
    print("Anomalies Detected:", anomalies2)
    
    assert any(x['metric'] == 'Repairs' for x in anomalies2['Expenses'])

if __name__ == "__main__":
    test_kpi_table_generation()
    test_financial_table_generation()
    test_analyzer_variances()
    print("All tests passed!")
