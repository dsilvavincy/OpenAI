"""
Streamlit UI for AI-Driven T12 Data Question Generator - Dual-Mode Version
"""
import streamlit as st
import pandas as pd
import io
import os
import time
from datetime import datetime

# Import our dual-mode UI system
from src.ui.modes.mode_manager import render_current_mode, get_current_mode

# Legacy imports for backward compatibility (will be removed)
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
    """Main application entry point using dual-mode UI system."""
    # Initialize session state for API key from environment
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = os.getenv("OPENAI_API_KEY", "")
    
    # Initialize progress tracking for backward compatibility
    create_progress_tracker()
    
    # Main app header
    st.title("🏢 AI-Driven T12 Property Analysis Tool")
    
    # File uploader in main content area
    uploaded_file = st.file_uploader(
        "📁 Upload your T12 Excel file to generate AI-powered property performance insights",
        type=['xlsx', 'xls'],
        help="Upload your T12 property financial data in Excel format"
    )
    
    # Render the appropriate UI mode
    render_current_mode(uploaded_file)

if __name__ == "__main__":
    main()
