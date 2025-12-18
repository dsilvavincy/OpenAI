"""
Production Upload - Streamlined file upload for production mode

Handles file upload with immediate processing and clean user feedback.
Focuses on the essential workflow without debug features.
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class ProductionUpload:
    """Production mode file upload handler."""
    
    def render(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """
        Render the file upload section - streamlined for production.
        
        Args:
            uploaded_file: Current uploaded file object
            config: Configuration from sidebar
        """
        st.markdown("### 📁 Upload T12 Data")
        
        # Use session state to persist uploaded file
        if 'current_uploaded_file' not in st.session_state:
            st.session_state['current_uploaded_file'] = None
        
        uploaded_file = st.file_uploader(
            "Choose your T12 Excel file",
            type=['xlsx', 'xls'],
            help="Upload your T12 property financial data for AI analysis",
            key="production_file_uploader"
        )
        
        # Only process if not already processed
        if uploaded_file is not None:
            st.session_state['current_uploaded_file'] = uploaded_file
            if 'processed_monthly_df' not in st.session_state or 'processed_ytd_df' not in st.session_state:
                with st.spinner("📊 Processing file..."):
                    monthly_df, ytd_df = self._handle_file_upload(uploaded_file)
                    if monthly_df is not None:
                        st.session_state['processed_monthly_df'] = monthly_df
                        st.session_state['processed_ytd_df'] = ytd_df
                        st.session_state['uploaded_file'] = uploaded_file
                        
                        # Skip saving to exports folder as requested
                        # self._save_processed_data(monthly_df, ytd_df, uploaded_file.name)
                        
                        st.success("✅ File processed successfully! Monthly and YTD data available.")
                        st.rerun()  # Refresh to show results layout
    
    def _handle_file_upload(self, uploaded_file):
        """
        Process uploaded T12 file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (monthly_df, ytd_df) or (None, None) if processing failed
        """
        try:
            from src.core.cres_batch_processor import process_cres_workbook
            import io
            excel_buffer = io.BytesIO(uploaded_file.getvalue())
            monthly_df, ytd_df = process_cres_workbook(excel_buffer)
            if monthly_df is not None and not monthly_df.empty:
                st.success(f"✅ Processed {len(monthly_df)} monthly rows with {monthly_df['Metric'].nunique()} unique metrics")
            else:
                st.error("❌ No monthly data found in file")
            if ytd_df is not None and not ytd_df.empty:
                st.success(f"✅ Processed {len(ytd_df)} YTD rows")
            else:
                st.warning("⚠️ No YTD data found in file")
            return monthly_df, ytd_df
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Please ensure your file is a valid T12 Excel format")
            return None, None
    
