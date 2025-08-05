"""
Format Detection Utilities
Helps identify the format type of uploaded data for dynamic prompt selection
"""

import pandas as pd
import logging
from src.core.format_registry import FormatRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_format_from_dataframe(df: pd.DataFrame) -> str:
    """
    Detect format type from processed DataFrame.
    
    Args:
        df: Processed DataFrame from tidy_sheet_all or similar preprocessing
        
    Returns:
        str: Format name (e.g., "t12_monthly_financial", "weekly_database")
    """
    try:
        # Initialize format registry
        registry = FormatRegistry()
        
        # Try to detect format using registry
        detected_format = registry.detect_format(df)
        
        if detected_format:
            logger.info(f"Detected format: {detected_format}")
            return detected_format
        else:
            logger.warning("Could not detect format, defaulting to t12_monthly_financial")
            return "t12_monthly_financial"
            
    except Exception as e:
        logger.error(f"Error detecting format: {str(e)}")
        return "t12_monthly_financial"

def detect_format_from_file_path(file_path: str) -> str:
    """
    Detect format type from file name patterns.
    
    Args:
        file_path: Path to the uploaded file
        
    Returns:
        str: Format name based on file name patterns
    """
    try:
        file_path_lower = file_path.lower()
        
        # Check for common file name patterns
        if any(pattern in file_path_lower for pattern in ['t12', 't-12', 'twelve', 'monthly']):
            return "t12_monthly_financial"
        elif any(pattern in file_path_lower for pattern in ['weekly', 'week', 'database']):
            return "weekly_database"
        else:
            logger.info(f"No specific pattern detected in filename: {file_path}, defaulting to t12_monthly_financial")
            return "t12_monthly_financial"
            
    except Exception as e:
        logger.error(f"Error detecting format from file path: {str(e)}")
        return "t12_monthly_financial"

def get_format_display_name(format_name: str) -> str:
    """
    Get user-friendly display name for format.
    
    Args:
        format_name: Internal format name
        
    Returns:
        str: User-friendly format name
    """
    format_names = {
        "t12_monthly_financial": "T12 Monthly Financial",
        "weekly_database": "Weekly Database",
        "quarterly_financial": "Quarterly Financial",
        "annual_financial": "Annual Financial"
    }
    
    return format_names.get(format_name, format_name.replace("_", " ").title())

def store_detected_format(format_name: str):
    """
    Store detected format in session state for use throughout the application.
    
    Args:
        format_name: Detected format name
    """
    try:
        import streamlit as st
        st.session_state['detected_format'] = format_name
        st.session_state['format_display_name'] = get_format_display_name(format_name)
        logger.info(f"Stored detected format: {format_name}")
    except Exception as e:
        logger.error(f"Error storing detected format: {str(e)}")

def get_stored_format() -> str:
    """
    Get the stored format from session state.
    
    Returns:
        str: Stored format name or default
    """
    try:
        import streamlit as st
        return st.session_state.get('detected_format', 't12_monthly_financial')
    except Exception as e:
        logger.error(f"Error getting stored format: {str(e)}")
        return "t12_monthly_financial"
