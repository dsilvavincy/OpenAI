"""Quick test to verify case-insensitive matching works."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.formats.database_t12_processor import DatabaseT12Processor

# Test case-insensitive matching
file_path = project_root / "data" / "CRES - Portfolio Database.xlsm"
processor = DatabaseT12Processor()

print("Processing with case-insensitive filter...")
df = processor.process(file_path)

# Check if Flats on maple is in the output
properties = sorted(df['Property'].unique())
print(f"\nTotal properties processed: {len(properties)}")

target = "Flats on maple"
if target in properties:
    print(f"✓ '{target}' found in output!")
else:
    print(f"✗ '{target}' NOT found in output")
    print(f"  Looking for case-insensitive matches...")
    for prop in properties:
        if prop.lower() == target.lower():
            print(f"  Found: '{prop}'")
