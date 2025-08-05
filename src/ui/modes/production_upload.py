"""
Production Upload - Streamlined file upload for production mode

Handles file upload with immediate processing and clean user feedback.
Focuses on the essential workflow without debug features.
"""
import streamlit as st
import pandas as pd
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
        
        # Update session state when file changes
        if uploaded_file is not None:
            st.session_state['current_uploaded_file'] = uploaded_file
            # Process file immediately
            with st.spinner("📊 Processing file..."):
                df = self._handle_file_upload(uploaded_file)
                
                if df is not None:
                    # Store in session state
                    st.session_state['processed_df'] = df
                    st.session_state['uploaded_file'] = uploaded_file
                    st.success("✅ File processed successfully!")
                    st.rerun()  # Refresh to show results layout
    
    def _handle_file_upload(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Process uploaded T12 file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Processed DataFrame or None if processing failed
        """
        try:
            # Import processing functions
            from src.core.preprocess import tidy_sheet_all
            import io
            
            # Read Excel file directly from memory (no temp file needed)
            excel_buffer = io.BytesIO(uploaded_file.getvalue())
            
            # Process the file
            df = tidy_sheet_all(excel_buffer)
            
            if df is not None and not df.empty:
                st.success(f"✅ Processed {len(df)} rows with {df['Metric'].nunique()} unique metrics")
                return df
            else:
                st.error("❌ No data found in file")
                return None
                    
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Please ensure your file is a valid T12 Excel format")
            return None
