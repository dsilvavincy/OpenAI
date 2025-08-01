"""
Streamlit UI for AI-Driven T12 Data Question Generator
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from src.preprocess import tidy_sheet_all
from src.kpi_summary import generate_kpi_summary
from src.prompt import build_prompt, call_openai

# Page configuration
st.set_page_config(
    page_title="T12 Property Analysis Tool",
    page_icon="🏢",
    layout="wide"
)

def main():
    st.title("🏢 AI-Driven T12 Property Analysis Tool")
    st.markdown("Upload your T12 Excel file to generate AI-powered property performance insights")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key to enable AI analysis"
        )
        
        # Property information
        st.header("Property Information")
        property_name = st.text_input("Property Name", placeholder="e.g., Sunset Apartments")
        property_address = st.text_input("Property Address", placeholder="e.g., 123 Main St, City, State")
        
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📁 Upload T12 Data")
        
        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Upload your T12 property financial data in Excel format"
        )
        
        if uploaded_file is not None:
            try:
                # Show file details
                st.success(f"File uploaded: {uploaded_file.name}")
                st.info(f"File size: {len(uploaded_file.read())} bytes")
                uploaded_file.seek(0)  # Reset file pointer
                
                # Process the file
                with st.spinner("Processing T12 data..."):
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.read())
                    
                    # Process the data
                    df = tidy_sheet_all(temp_path)
                    st.success(f"Successfully processed {len(df)} data points")
                    
                    # Show data preview
                    st.subheader("📊 Data Preview")
                    st.dataframe(df.head(10), use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                return
    
    with col2:
        st.header("📈 Analysis Results")
        
        if uploaded_file is not None and 'df' in locals():
            try:
                # Generate KPI Summary
                with st.spinner("Generating KPI summary..."):
                    kpi_summary = generate_kpi_summary(df)
                
                # Show KPI Summary
                st.subheader("📋 KPI Summary")
                st.text_area("", kpi_summary, height=300, disabled=True)
                
                # AI Analysis
                if api_key and st.button("🤖 Generate AI Analysis", type="primary"):
                    with st.spinner("Analyzing with AI..."):
                        system_prompt, user_prompt = build_prompt(kpi_summary)
                        ai_response = call_openai(system_prompt, user_prompt, api_key)
                    
                    st.subheader("🧠 AI-Generated Analysis")
                    st.markdown(ai_response)
                    
                    # Export options
                    st.subheader("📄 Export Options")
                    
                    # Generate report content
                    report_content = generate_report(
                        property_name, 
                        property_address, 
                        kpi_summary, 
                        ai_response
                    )
                    
                    # Download button
                    st.download_button(
                        label="📄 Download Report",
                        data=report_content,
                        file_name=f"T12_Analysis_{property_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                
                elif not api_key:
                    st.warning("Please enter your OpenAI API key in the sidebar to generate AI analysis")
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

def generate_report(property_name, property_address, kpi_summary, ai_analysis):
    """Generate a formatted report for download"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
T12 PROPERTY ANALYSIS REPORT
============================

Property: {property_name}
Address: {property_address}
Generated: {timestamp}

KPI SUMMARY
===========
{kpi_summary}

AI ANALYSIS
===========
{ai_analysis}

---
Generated by AI-Driven T12 Analysis Tool
"""
    return report

if __name__ == "__main__":
    main()
