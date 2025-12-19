import pandas as pd
import json
from pathlib import Path

def inspect():
    file_path = r'C:\Users\VINCY\OneDrive - Vincy R Dsilva\VBA\Brendan\AI Project\OpenAI\data\CRES Monthly Financial Workbook.xlsm'
    try:
        xls = pd.ExcelFile(file_path, engine="openpyxl")
        sheet_name = 'Solas Glendale'
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        # Get Row 7 (header)
        header_row = df.iloc[6].tolist()
        # Get Row 8 (data)
        data_row = df.iloc[7].tolist()
        
        # Clean for inspection
        info = {
            "sheet_name": sheet_name,
            "header": [str(x) if not pd.isna(x) else None for x in header_row],
            "sample_data": [str(x) if not pd.isna(x) else None for x in data_row],
            "total_rows": len(df),
            "total_cols": len(df.columns)
        }
        
        with open('inspection_results.json', 'w') as f:
            json.dump(info, f, indent=2)
        print("Inspection saved to inspection_results.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
