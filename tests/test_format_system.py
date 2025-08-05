"""
Test the new scalable format system with existing T12 data.

This script tests:
1. Format detection
2. Format processing  
3. Data validation
4. Registry functionality
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.core.format_registry import format_registry, process_file, list_available_formats
from src.core.formats.t12_processor import T12MonthlyFinancialProcessor

def test_format_system():
    """Test the new format system."""
    print("=== Testing Scalable Format System ===\n")
    
    # 1. Test registry
    print("1. Available formats:")
    formats = list_available_formats()
    for fmt in formats:
        print(f"   - {fmt}")
    print()
    
    # 2. Test format info
    print("2. T12 Format Info:")
    t12_info = format_registry.get_format_info("T12_Monthly_Financial")
    if t12_info:
        print(f"   Name: {t12_info['name']}")
        print(f"   Description: {t12_info['description']}")
        print(f"   Expected metrics: {len(t12_info['expected_metrics'])}")
    print()
    
    # 3. Test with sample file (if exists)
    sample_files = [
        "data/Data.xlsx",
        "data/temp_Data.xlsx", 
        "data/sample_t12.xlsx",
        "data/T12_sample.xlsx", 
        "data/test_data.xlsx"
    ]
    
    test_file = None
    for file_path in sample_files:
        if Path(file_path).exists():
            test_file = Path(file_path)
            break
    
    if test_file:
        print(f"3. Testing with file: {test_file}")
        try:
            # Process file using new system
            df, processor = process_file(test_file)
            
            print(f"   ✅ Processed successfully with: {processor.format_name}")
            print(f"   📊 Data shape: {df.shape}")
            print(f"   📋 Columns: {list(df.columns)}")
            print(f"   📈 Unique metrics: {df['Metric'].nunique()}")
            print(f"   📅 Date range: {df['PeriodParsed'].min()} to {df['PeriodParsed'].max()}")
            
            # Show quality issues
            quality_issues = processor.get_quality_issues()
            if quality_issues:
                print(f"   ⚠️  Quality issues: {len(quality_issues)}")
                for issue in quality_issues[:3]:  # Show first 3
                    print(f"      - {issue}")
            else:
                print("   ✅ No quality issues found")
            
            print("\n   Sample data:")
            print(df.head(10).to_string())
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    else:
        print("3. No sample T12 file found to test with")
        print("   Please add a sample file to data/ folder to test processing")
    
    print("\n=== Format System Test Complete ===")

if __name__ == "__main__":
    test_format_system()
