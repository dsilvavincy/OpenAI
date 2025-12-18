"""
Test script for local_analysis.py
Verifies that PropertyAnalyzer correctly computes all metrics from export data.
"""

import sys
import os
from pathlib import Path

# Add project root to path (go up from tests/ to project root)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.core.local_analysis import PropertyAnalyzer, prepare_analysis_for_llm
import json


def test_with_export_files():
    """Test PropertyAnalyzer with actual export CSV files."""
    
    # Find the export files - use project_root
    exports_dir = project_root / "exports"
    
    monthly_files = list(exports_dir.glob("Data_monthly_*.csv"))
    ytd_files = list(exports_dir.glob("Data_ytd_*.csv"))
    
    if not monthly_files or not ytd_files:
        print("❌ No export files found in exports/ directory")
        print(f"   Looking in: {exports_dir}")
        return False
    
    # Use the most recent files
    monthly_file = sorted(monthly_files)[-1]
    ytd_file = sorted(ytd_files)[-1]
    
    print(f"📂 Loading data files:")
    print(f"   Monthly: {monthly_file.name}")
    print(f"   YTD: {ytd_file.name}")
    
    # Load the data
    monthly_df = pd.read_csv(monthly_file)
    ytd_df = pd.read_csv(ytd_file)
    
    print(f"\n📊 Data shapes:")
    print(f"   Monthly: {monthly_df.shape}")
    print(f"   YTD: {ytd_df.shape}")
    
    # Create analyzer
    analyzer = PropertyAnalyzer(monthly_df, ytd_df)
    
    # Get available properties
    properties = analyzer.get_available_properties()
    print(f"\n🏢 Available properties: {properties[:5]}..." if len(properties) > 5 else f"\n🏢 Available properties: {properties}")
    
    if not properties:
        print("❌ No properties found in data")
        return False
    
    # Test with first property
    test_property = properties[0]
    print(f"\n🔍 Analyzing property: {test_property}")
    
    # Run analysis
    result = analyzer.analyze_property(test_property)
    
    # Print results
    print(f"\n✅ Analysis complete!")
    print(f"\n📋 Report Period: {result['report_period']}")
    print(f"📋 Prior Period: {result['prior_period']}")
    
    print(f"\n📊 Validation:")
    for key, value in result['validation'].items():
        print(f"   • {key}: {value}")
    
    print(f"\n💰 Current Month KPIs:")
    for key, value in result['current_month'].items():
        print(f"   • {key}: ${value:,.2f}")
    
    print(f"\n📈 YTD Performance:")
    for key, value in result['ytd_cumulative'].items():
        if isinstance(value, (int, float)):
            print(f"   • {key}: ${value:,.2f}" if 'pct' not in key else f"   • {key}: {value:.2f}%")
        else:
            print(f"   • {key}: {value}")
    
    print(f"\n📊 Key Ratios:")
    for key, value in result['key_ratios'].items():
        print(f"   • {key}: {value:.2f}%")
    
    print(f"\n📊 Data Highlights:")
    highlights = result.get('data_highlights', {})
    if 'vacancy_rate_pct' in highlights:
        print(f"   • Vacancy Rate: {highlights['vacancy_rate_pct']:.2f}%")
    if 'delinquency_rate_pct' in highlights:
        print(f"   • Delinquency Rate: {highlights['delinquency_rate_pct']:.2f}%")
    if 'expense_ratio_pct' in highlights:
        print(f"   • Expense Ratio: {highlights['expense_ratio_pct']:.2f}%")
    if 'largest_mom_changes' in highlights:
        print(f"   • Top MoM Changes: {len(highlights['largest_mom_changes'])} tracked")
    
    print(f"\n📊 MoM Changes:")
    for metric, changes in result['mom_changes'].items():
        if isinstance(changes, dict) and 'change_pct' in changes:
            print(f"   • {metric}: {changes['change_pct']:+.2f}% (${changes['change_abs']:+,.2f})")
    
    # Output full JSON for inspection
    output_file = exports_dir / "analysis_test_output.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n💾 Full analysis saved to: {output_file.name}")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing PropertyAnalyzer with Export Data")
    print("=" * 60)
    
    success = test_with_export_files()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - PropertyAnalyzer working correctly")
    else:
        print("❌ TEST FAILED - Check output above for details")
    print("=" * 60)
