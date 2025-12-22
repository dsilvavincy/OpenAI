"""
Streamlit UI for AI-Driven T12 Data Question Generator - Dual-Mode Version
"""
import streamlit as st
import pandas as pd
import io
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Global Print CSS - Ensures headers stay with tables when printing to PDF
st.markdown("""
<style>
@media print {
    /* Prevent headers from being orphaned at page bottom */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid !important;
        break-after: avoid !important;
    }
    
    /* Prevent tables from breaking across pages */
    table, .report-table, .stDataFrame {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    
    /* Force major sections to start on new page */
    [data-testid="stVerticalBlock"] > div:has(h4) {
        page-break-before: auto;
    }
    
    /* Keep Streamlit blocks together */
    .element-container {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    
    /* Ensure headers and their following content stay together */
    .element-container:has(h4) {
        page-break-after: avoid !important;
        break-after: avoid !important;
    }
}
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point using dual-mode UI system."""
    # Initialize session state for API key from environment
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = os.getenv("OPENAI_API_KEY", "")
    
    # Initialize progress tracking for backward compatibility
    create_progress_tracker()
    
    # Render the appropriate UI mode (no duplicate file uploader)
    render_current_mode()

if __name__ == "__main__":
    main()
