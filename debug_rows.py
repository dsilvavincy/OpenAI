import openpyxl
import pandas as pd

file_path = r'c:\Users\VINCY\OneDrive - Vincy R Dsilva\VBA\Brendan\AI Project\OpenAI\data\CRES - Portfolio Database.xlsm'

try:
    wb = openpyxl.load_workbook(file_path, read_only=True)
    sheets = wb.sheetnames
    print(f"Sheets: {sheets}")
    
    # Pick first 'Fin' sheet
    fin_sheet = next((s for s in sheets if 'Fin' in s), None)
    
    if fin_sheet:
        print(f"\nAnalyzing Sheet: {fin_sheet}")
        df = pd.read_excel(file_path, sheet_name=fin_sheet, header=None, engine='openpyxl')
        
        print("\n--- ROW INSPECTION (0-indexed logic) ---")
        # Print valid rows around expected Revenue/Expense boundaries
        # User says Rev 8-20, Exp 23-38. 
        # Excel Row 8 = Index 7.
        
        for i in range(7, 60):
            val = str(df.iloc[i, 0]).strip() if pd.notna(df.iloc[i, 0]) else ""
            if val:
                print(f"Index {i} (Excel {i+1}): {val}")
                
except Exception as e:
    print(f"Error: {e}")
