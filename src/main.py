"""
Main entry point for AI-Driven T12 Data Question Generator
"""
from src.preprocess import tidy_sheet_all
from src.kpi_summary import generate_kpi_summary
from src.prompt import build_prompt, call_openai

import sys

if __name__ == "__main__":
    # Step 1: Upload T12 Excel File (for now, use a hardcoded path or sys.argv)
    excel_path = sys.argv[1] if len(sys.argv) > 1 else "sample_t12.xlsx"
    
    try:
        print("Processing T12 data...")
        
        # Step 2: Preprocess the Data
        df = tidy_sheet_all(excel_path)
        print(f"Successfully processed {len(df)} data points")

        # Step 3: Generate a KPI Summary
        kpi_summary = generate_kpi_summary(df)
        print("Generated KPI summary")

        # Step 4: Define Standard Instructions & Build Prompt
        system_prompt, user_prompt = build_prompt(kpi_summary)

        # Step 5: Call OpenAI API
        response = call_openai(system_prompt, user_prompt)

        # Step 6: Display Output
        print("\n" + "="*50)
        print("AI GENERATED PROPERTY ANALYSIS")
        print("="*50)
        print(response)
        print("="*50)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
