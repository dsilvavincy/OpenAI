"""
Test the integrated scalable format and KPI system.

This script tests:
1. Format detection and processing
2. KPI calculation with the new system
3. Comparison with old KPI system
4. Full integration workflow
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.core.format_registry import format_registry, process_file
from src.core.kpi_registry import kpi_registry, calculate_kpis
from src.core.kpi_summary import generate_kpi_summary  # Old system for comparison

def test_integrated_system():
    """Test the integrated format and KPI system."""
    print("=== Testing Integrated Format + KPI System ===\n")
    
    # Test with actual data file
    test_file = Path("data/Data.xlsx")
    
    if not test_file.exists():
        print("❌ Test file data/Data.xlsx not found")
        return
    
    try:
        print("1. Processing file with new format system...")
        df, processor = process_file(test_file)
        print(f"   ✅ Processed with: {processor.format_name}")
        print(f"   📊 Data shape: {df.shape}")
        print(f"   📋 Columns: {list(df.columns)}")
        
        print("\n2. Testing new KPI calculation system...")
        new_kpi_summary = calculate_kpis(df, processor.format_name)
        print(f"   ✅ KPI calculation completed")
        print(f"   📄 Summary length: {len(new_kpi_summary)} characters")
        
        # Get calculation issues if any
        calc_issues = kpi_registry.get_calculation_issues(processor.format_name)
        if calc_issues:
            print(f"   ⚠️  Calculation issues: {len(calc_issues)}")
            for issue in calc_issues[:3]:
                print(f"      - {issue}")
        else:
            print("   ✅ No calculation issues")
        
        print("\n3. Comparing with old KPI system...")
        try:
            # Convert new format to old format for comparison
            old_format_df = df.copy()
            old_format_df = old_format_df.rename(columns={'Period': 'Month', 'PeriodParsed': 'MonthParsed'})
            old_kpi_summary = generate_kpi_summary(old_format_df)
            
            print(f"   📄 Old summary length: {len(old_kpi_summary)} characters")
            print(f"   📄 New summary length: {len(new_kpi_summary)} characters")
            
            # Compare key sections
            old_has_revenue = "REVENUE PERFORMANCE" in old_kpi_summary
            new_has_revenue = "REVENUE PERFORMANCE" in new_kpi_summary
            old_has_trends = "TRENDS" in old_kpi_summary
            new_has_trends = "TRENDS" in new_kpi_summary
            old_has_ratios = "RATIOS" in old_kpi_summary
            new_has_ratios = "RATIOS" in new_kpi_summary
            
            print(f"   Revenue section - Old: {old_has_revenue}, New: {new_has_revenue}")
            print(f"   Trends section - Old: {old_has_trends}, New: {new_has_trends}")
            print(f"   Ratios section - Old: {old_has_ratios}, New: {new_has_ratios}")
            
        except Exception as e:
            print(f"   ⚠️  Could not compare with old system: {str(e)}")
        
        print("\n4. Registry Information:")
        available_formats = kpi_registry.list_available_formats()
        print(f"   Available KPI calculators: {available_formats}")
        
        for format_name in available_formats:
            key_metrics = kpi_registry.get_key_metrics(format_name)
            print(f"   {format_name} key metrics: {len(key_metrics) if key_metrics else 0}")
        
        print("\n5. Sample of New KPI Output:")
        print("   " + "="*50)
        # Show first 1000 characters of new KPI summary
        sample_output = new_kpi_summary[:1000]
        for line in sample_output.split('\n'):
            print(f"   {line}")
        if len(new_kpi_summary) > 1000:
            print("   ...")
            print(f"   [Showing first 1000 of {len(new_kpi_summary)} characters]")
        print("   " + "="*50)
        
        print("\n✅ Integrated system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in integrated test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integrated_system()
