import sys
from pathlib import Path
import pandas as pd
from rich import print

# Add src to path
sys.path.append(str(Path.cwd()))

from src.core.format_registry import format_registry

FILE_PATH = "data/CRES - Portfolio Database.xlsm"

def verify_processor():
    print(f"Testing DatabaseT12Processor with {FILE_PATH}...")
    
    # Check detection
    processor = format_registry.detect_format(FILE_PATH)
    if not processor:
        print("[red]Format detection failed![/red]")
        return
        
    print(f"Detected Format: [green]{processor.format_name}[/green]")
    
    # Process
    try:
        df = processor.process(FILE_PATH)
        print(f"Processing complete. DataFrame shape: {df.shape}")
        
        if df.empty:
            print("[red]Error: Resulting DataFrame is empty.[/red]")
            return
            
        print("\n[bold]Sample Data:[/bold]")
        print(df.head())
        
        # Verify YTD
        ytd_rows = df[df['IsYTD'] == True]
        print(f"\n[bold]YTD Rows Check:[/bold] Found {len(ytd_rows)} YTD rows.")
        if not ytd_rows.empty:
            print(ytd_rows.head())
        else:
            print("[red]Warning: No YTD rows generated.[/red]")
            
        # Verify Properties
        props = df['Property'].unique()
        print(f"\n[bold]Properties Found:[/bold] {len(props)}")
        print(props[:5])
        
        # Verify Budget Nullification (Spot Check)
        print("\n[bold]Budget Logic Check:[/bold]")
        # Find a row with 'Physical Occupancy' just to see
        occ_rows = df[df['Metric'].str.contains("Physical Occupancy", case=False, na=False)]
        if not occ_rows.empty:
            print("Physical Occupancy Budget Values (Should be NaN/None):")
            print(occ_rows[['Metric', 'Period', 'BudgetValue']].head())
            
    except Exception as e:
        print(f"[red]Processing Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_processor()
