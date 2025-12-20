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
        
        # Persistence Logic
        CACHE_DIR = Path(".cache")
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_MONTHLY = CACHE_DIR / "monthly_df.pkl"
        CACHE_YTD = CACHE_DIR / "ytd_df.pkl"
        
        # Check for cached data to offer restore
        if 'processed_monthly_df' not in st.session_state and CACHE_MONTHLY.exists() and CACHE_YTD.exists():
            if st.button("🔄 Restore Previous Session Data", type="primary"):
                try:
                    st.session_state['processed_monthly_df'] = pd.read_pickle(CACHE_MONTHLY)
                    st.session_state['processed_ytd_df'] = pd.read_pickle(CACHE_YTD)
                    st.session_state['current_uploaded_file'] = "Restored Session"
                    st.success("✅ Previous session restored!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not restore session: {e}")
        
        # Use session state to persist uploaded file
        if 'current_uploaded_file' not in st.session_state:
            st.session_state['current_uploaded_file'] = None
        
        uploaded_file = st.file_uploader(
            "Choose your T12 Excel file",
            type=['xlsx', 'xls', 'xlsm'],
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
                        
                        # Cache to disk for persistence across refreshes
                        monthly_df.to_pickle(CACHE_MONTHLY)
                        ytd_df.to_pickle(CACHE_YTD)
                        
                        # Save to exports folder as requested
                        self._save_processed_data(monthly_df, ytd_df, uploaded_file.name)
                        
                        st.success("✅ File processed successfully! Monthly and YTD data available.")
                        st.rerun()  # Refresh to show results layout
    
    def _handle_file_upload(self, uploaded_file):
        """
        Process uploaded T12 file using FormatRegistry for automatic detection.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (monthly_df, ytd_df) or (None, None) if processing failed
        """
        try:
            from src.core.format_registry import FormatRegistry
            from src.utils.format_detection import store_detected_format
            import io
            
            # Reset buffer
            uploaded_file.seek(0)
            excel_buffer = io.BytesIO(uploaded_file.getvalue())
            
            # Use registry to detect and process
            registry = FormatRegistry()
            unified_df, processor = registry.process_file(excel_buffer)
            
            if unified_df is None or unified_df.empty:
                st.error("❌ No data could be extracted from the file.")
                return None, None
                
            # Store detected format for prompt selection
            store_detected_format(processor.format_name)
            
            # Split into monthly and YTD for the analysis engine
            monthly_df, ytd_df = self._split_unified_df(unified_df)
            
            if monthly_df is not None and not monthly_df.empty:
                metrics_count = monthly_df['Metric'].nunique()
                properties_count = monthly_df['Property'].nunique()
                st.success(f"✅ Processed {properties_count} properties, {metrics_count} unique metrics")
            else:
                st.error("❌ No monthly data found in file")
            
            if ytd_df is None or ytd_df.empty:
                st.warning("⚠️ No YTD data found in file")
                
            return monthly_df, ytd_df
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Please ensure your file is a valid T12 Excel format")
            import traceback
            st.expander("Error Details").code(traceback.format_exc())
            return None, None

    def _split_unified_df(self, df):
        """Split unified DataFrame into monthly and YTD DataFrames for analysis."""
        if df is None or df.empty:
            return None, None
            
        # Split by the IsYTD flag
        monthly_df = df[df['IsYTD'] == False].copy()
        ytd_df = df[df['IsYTD'] == True].copy()
        
        # Fill in date info for YTD rows based on last month of each property
        # This aligns with how PropertyAnalyzer expects YTD data
        for prop in ytd_df['Property'].unique():
            prop_rows = monthly_df[monthly_df['Property'] == prop]
            if not prop_rows.empty:
                # Find the latest month for this property
                max_month_idx = prop_rows['MonthParsed'].idxmax()
                last_date_info = prop_rows.loc[max_month_idx]
                
                idx = ytd_df['Property'] == prop
                ytd_df.loc[idx, 'Month'] = last_date_info['Month']
                ytd_df.loc[idx, 'MonthParsed'] = last_date_info['MonthParsed']
                ytd_df.loc[idx, 'Year'] = last_date_info['Year']
                ytd_df.loc[idx, 'Month_Name'] = last_date_info['Month_Name']
        
        # Drop the IsYTD helper column if it exists to keep DataFrames clean
        if 'IsYTD' in monthly_df.columns:
            monthly_df = monthly_df.drop(columns=['IsYTD'])
        if 'IsYTD' in ytd_df.columns:
            ytd_df = ytd_df.drop(columns=['IsYTD'])
            
        return monthly_df, ytd_df

    def _save_processed_data(self, monthly_df, ytd_df, filename):
        """Save processed DataFrames to the exports folder."""
        import os
        from pathlib import Path
        from datetime import datetime
        
        try:
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(filename).stem
            
            monthly_path = export_dir / f"{base_name}_monthly_{timestamp}.csv"
            ytd_path = export_dir / f"{base_name}_ytd_{timestamp}.csv"
            
            monthly_df.to_csv(monthly_path, index=False)
            ytd_df.to_csv(ytd_path, index=False)
            
            # Save a unified version for convenience
            unified_path = export_dir / f"{base_name}_unified_{timestamp}.csv"
            pd.concat([monthly_df, ytd_df], ignore_index=True).to_csv(unified_path, index=False)
            
            st.info(f"📁 Processed data exported to `{export_dir}`")
            
        except Exception as e:
            st.warning(f"⚠️ Could not save CSVs to exports folder: {str(e)}")
    
