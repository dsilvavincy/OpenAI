"""
Developer Upload Section - Enhanced file upload with debugging tools
"""
import streamlit as st
import os
from typing import Optional, Dict, Any
from src.ui.validation import validate_uploaded_file
from src.ui.progress import update_progress
from src.ui.data_analysis import display_file_processing_section

class DeveloperUploadSection:
    """Enhanced file upload section with developer tools."""
    
    def render(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render enhanced file upload section with collapsible developer tools."""
        from src.ui.shared_file_manager import SharedFileManager
        
        st.markdown("### 📁 File Upload & Processing")
        
        # Sync any legacy session state data
        SharedFileManager.sync_legacy_session_state()
        
        # Check if we already have an uploaded file from any mode
        existing_file = SharedFileManager.get_uploaded_file()
        
        uploaded_file = st.file_uploader(
            "T12 Excel File",
            type=['xlsx', 'xls'],
            help="Upload your T12 property financial data",
            key="developer_file_uploader"
        )
        
        # Update shared file manager when file changes
        if uploaded_file is not None:
            # Check if this is a new file
            if SharedFileManager.is_file_changed(uploaded_file):
                SharedFileManager.set_uploaded_file(uploaded_file)
                
                # Basic file info (always visible)
                SharedFileManager.display_file_info(uploaded_file)
                
                # File Analysis (collapsible)
                with st.expander("🔍 File Analysis & Validation", expanded=config.get('show_format_details', False)):
                    st.info(f"**Type:** {uploaded_file.type}")
                    
                    # Format detection
                    if config.get('auto_detect_format', True):
                        self._perform_format_detection(uploaded_file, config)
                    
                    # File validation details
                    self._show_validation_results(uploaded_file)
                
                # Process file with detailed feedback
                df = self._process_file_with_debug(uploaded_file, config)
                
                if df is not None:
                    st.success(f"✅ **Processing complete:** {df.shape[0]} rows, {df['Metric'].nunique()} metrics")
                    
                    # Store in shared session state
                    SharedFileManager.set_processed_df(df)
                    
                    # Data Quality Checks (collapsible)
                    with st.expander("📊 Data Quality & Structure", expanded=False):
                        self._render_data_quality_analysis(df)
                    
                    # Raw Data Viewer (collapsible)
                    if config.get('show_raw_data', True):
                        with st.expander("👁️ Raw Data Preview", expanded=False):
                            self._render_raw_data_viewer(df)
        elif existing_file is not None:
            # Show info about existing file from other mode
            st.info("📄 **File from previous session/mode:**")
            SharedFileManager.display_file_info()
            
            # Show processed data if available
            df = SharedFileManager.get_processed_df()
            if df is not None:
                st.success(f"✅ **Data available:** {df.shape[0]} rows, {df['Metric'].nunique()} metrics")
                
                # Data Quality Checks (collapsible)
                with st.expander("📊 Data Quality & Structure", expanded=False):
                    self._render_data_quality_analysis(df)
                
                # Raw Data Viewer (collapsible)
                if config.get('show_raw_data', True):
                    with st.expander("👁️ Raw Data Preview", expanded=False):
                        self._render_raw_data_viewer(df)
            
            # Option to clear and upload new file
            if st.button("🗑️ Clear and Upload New File", key="dev_clear_existing_file"):
                SharedFileManager.clear_uploaded_file()
                st.rerun()
    
    def _perform_format_detection(self, uploaded_file, config: Dict[str, Any]):
        """Perform format detection with detailed feedback."""
        with st.spinner("Detecting format..."):
            try:
                from src.core.format_registry import format_registry
                import tempfile
                
                # Save file temporarily for format detection
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                processor = format_registry.detect_format(tmp_file_path)
                if processor:
                    st.success(f"✅ **Detected Format:** {processor.format_name}")
                    if config.get('show_format_details', False):
                        st.info(f"**Processor:** {processor.__class__.__name__}")
                else:
                    st.warning("⚠️ Format not auto-detected, using default T12 processor")
                
                # Clean up temp file with better error handling
                try:
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                except PermissionError:
                    pass  # File might still be in use, skip cleanup
                except Exception as cleanup_error:
                    if config.get('debug_mode', False):
                        st.warning(f"⚠️ Cleanup warning: {str(cleanup_error)}")
                    
            except Exception as e:
                st.error(f"❌ Format detection error: {str(e)}")
    
    def _show_validation_results(self, uploaded_file):
        """Show file validation results."""
        try:
            validation = validate_uploaded_file(uploaded_file)
            if validation['valid']:
                st.success("✅ File validation passed")
            else:
                st.error(f"❌ Validation failed: {validation.get('error', 'Unknown error')}")
        except Exception as e:
            st.warning(f"⚠️ Validation check failed: {str(e)}")
    
    def _render_data_quality_analysis(self, df):
        """Render data quality analysis section."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Rows", df.shape[0])
            st.metric("Total Columns", df.shape[1])
            st.metric("Unique Metrics", df['Metric'].nunique() if 'Metric' in df.columns else 0)
        
        with col2:
            # Missing data analysis
            missing_data = df.isnull().sum().sum()
            st.metric("Missing Values", missing_data)
            
            # Date range analysis
            if 'MonthParsed' in df.columns:
                valid_dates = df['MonthParsed'].notna().sum()
                st.metric("Valid Dates", valid_dates)
        
        # Data types summary
        if st.checkbox("Show Column Types", value=False):
            st.write("**Column Types:**")
            st.dataframe(df.dtypes.to_frame('Type'), use_container_width=True)
    
    def _process_file_with_debug(self, uploaded_file, config: Dict[str, Any]):
        """Process file with debugging information."""
        try:
            # File validation with detailed feedback
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
                return None
                
            update_progress('file_validation', True)
            
            # Process the file
            df = display_file_processing_section(uploaded_file)
            
            if df is not None:
                update_progress('data_processing', True)
                
            return df
            
        except Exception as e:
            st.error(f"❌ File processing error: {str(e)}")
            if config.get('debug_mode', False):
                st.exception(e)
            return None
    
    def _render_raw_data_viewer(self, df):
        """Render raw data viewer with export options."""
        with st.expander("📊 Raw Data Viewer"):
            st.dataframe(df, use_container_width=True)
            
            # Data export options
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "processed_data.csv",
                "text/csv"
            )
