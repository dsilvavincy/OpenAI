"""
Streamlit UI for AI-Driven T12 Data Question Generator - Modular Version
"""
import streamlit as st
import pandas as pd
import io
import os
import time
from datetime import datetime

# Import our modular components
from src.ui.validation import validate_uploaded_file
from src.ui.progress import create_progress_tracker, update_progress, display_progress
from src.ui.data_analysis import display_data_analysis_section, display_kpi_testing_section, display_prompt_testing_section, display_file_processing_section
from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options
from src.core.kpi_summary import generate_kpi_summary

# Page configuration
st.set_page_config(
    page_title="T12 Property Analysis Tool",
    page_icon="🏢",
    layout="wide"
)

def main():
    st.title("🏢 AI-Driven T12 Property Analysis Tool")
    st.markdown("Upload your T12 Excel file to generate AI-powered property performance insights")
    
    # Initialize progress tracking
    create_progress_tracker()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key input with validation
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key to enable AI analysis"
        )
        
        if api_key:
            if api_key.startswith('sk-') and len(api_key) > 20:
                st.success("✅ API key format looks valid")
            else:
                st.warning("⚠️ API key format may be incorrect")
        
        st.divider()
        
        # Property information
        st.header("🏢 Property Information")
        property_name = st.text_input("Property Name", placeholder="e.g., Sunset Apartments")
        property_address = st.text_input("Property Address", placeholder="e.g., 123 Main St, City, State")
        
        st.divider()
        
        # Display progress
        display_progress()
        
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
            update_progress('file_upload', True)
            
            # File validation
            validation = validate_uploaded_file(uploaded_file)
            
            # Display validation results
            for msg in validation["messages"]:
                if msg.startswith("✅"):
                    st.success(msg)
                elif msg.startswith("❌"):
                    st.error(msg)
                    
            for warning in validation["warnings"]:
                st.warning(warning)
            
            if not validation["is_valid"]:
                return
                
            update_progress('file_validation', True)
            
            # Process the file
            df = display_file_processing_section(uploaded_file)
            
            if df is not None:
                update_progress('data_processing', True)
                
                # Display data analysis tools
                display_data_analysis_section(df)
                display_kpi_testing_section(df)
    
    with col2:
        st.header("📈 Analysis Results")
        
        if uploaded_file is not None and 'df' in locals() and df is not None:
            try:
                # Generate KPI Summary with progress
                kpi_progress = st.progress(0)
                kpi_status = st.empty()
                
                kpi_status.text("📊 Generating KPI summary...")
                kpi_progress.progress(50)
                
                kpi_summary = generate_kpi_summary(df)
                
                kpi_status.text("✅ KPI summary complete!")
                kpi_progress.progress(100)
                
                update_progress('kpi_generation', True)
                
                # Show KPI Summary
                st.subheader("📋 KPI Summary")
                with st.expander("View KPI Summary", expanded=True):
                    st.text_area("", kpi_summary, height=300, disabled=True)
                
                # Display prompt testing tools
                display_prompt_testing_section(kpi_summary, df)
                
                # AI Analysis Section
                processed_output = display_ai_analysis_section(df, kpi_summary, api_key, property_name, property_address)
                
                if processed_output:
                    update_progress('ai_analysis', True)
                    
                    # Display results
                    display_analysis_results(processed_output)
                    
                    # Display export options
                    display_export_options(processed_output, property_name)
                    
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("💡 **Troubleshooting tips:**")
                st.info("• Check that your data was processed correctly")
                st.info("• Verify your OpenAI API key is valid")
                st.info("• Try refreshing the page and uploading again")
        else:
            st.info("👆 Please upload a T12 Excel file to begin analysis")

if __name__ == "__main__":
    main()
