import pandas as pd
import openpyxl
from rich import print

FILE_PATH = "data/CRES - Portfolio Database.xlsm"

def inspect_workbook():
    print(f"Loading {FILE_PATH} (this might take a moment)...")
    wb = openpyxl.load_workbook(FILE_PATH, read_only=True, data_only=True)
    
    sheets = wb.sheetnames
    print(f"Total Sheets: {len(sheets)}")
    print(f"Sample Sheets: {sheets[:10]}")
    
    # Find a pair
    fin_sheet = next((s for s in sheets if s.endswith("-Fin")), None)
    bgt_sheet = next((s for s in sheets if s.endswith("-Bgt")), None)
    
    if fin_sheet:
        print(f"\nInspecting Financial Sheet: [bold]{fin_sheet}[/bold]")
        df_fin = pd.read_excel(FILE_PATH, sheet_name=fin_sheet, header=None, nrows=10, engine='openpyxl')
        print("Row 7 (Header Candidate):")
        print(df_fin.iloc[6].values[:10]) # First 10 cols
        
    if bgt_sheet:
        print(f"\nInspecting Budget Sheet: [bold]{bgt_sheet}[/bold]")
        df_bgt = pd.read_excel(FILE_PATH, sheet_name=bgt_sheet, header=None, nrows=10, engine='openpyxl')
        print("Row 7 (Header Candidate):")
        print(df_bgt.iloc[6].values[:10])

if __name__ == "__main__":
    inspect_workbook()
