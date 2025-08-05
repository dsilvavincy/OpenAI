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
        """Render enhanced file upload section with developer tools."""
        st.markdown("### 📁 Upload & Processing")
        
        # Use session state to persist uploaded file
        if 'dev_uploaded_file' not in st.session_state:
            st.session_state['dev_uploaded_file'] = None
        
        uploaded_file = st.file_uploader(
            "T12 Excel File",
            type=['xlsx', 'xls'],
            help="Upload your T12 property financial data",
            key="developer_file_uploader"
        )
        
        # Update session state when file changes
        if uploaded_file is not None:
            st.session_state['dev_uploaded_file'] = uploaded_file
        elif st.session_state['dev_uploaded_file'] is not None:
            uploaded_file = st.session_state['dev_uploaded_file']
            
        if uploaded_file is not None:
            # Enhanced file analysis
            st.markdown("#### 🔍 File Analysis")
            
            # Show file details
            st.info(f"**File:** {uploaded_file.name}")
            st.info(f"**Size:** {uploaded_file.size:,} bytes")
            st.info(f"**Type:** {uploaded_file.type}")
            
            # Format detection
            if config.get('auto_detect_format', True):
                self._perform_format_detection(uploaded_file)
            
            # Process file with detailed feedback
            df = self._process_file_with_debug(uploaded_file, config)
            
            if df is not None:
                st.success(f"✅ Processing complete")
                st.info(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                st.info(f"**Metrics:** {df['Metric'].nunique()} unique")
                
                # Store in session state
                st.session_state['processed_df'] = df
                st.session_state['uploaded_file'] = uploaded_file
                
                # Raw data viewer (developer mode)
                if config.get('show_raw_data', True):
                    self._render_raw_data_viewer(df)
    
    def _perform_format_detection(self, uploaded_file):
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
                    st.success(f"✅ Detected: {processor.format_name}")
                else:
                    st.warning("⚠️ Format not detected")
                
                # Clean up temp file with better error handling
                try:
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                except PermissionError:
                    pass  # File might still be in use, skip cleanup
                except Exception as cleanup_error:
                    st.warning(f"⚠️ Cleanup warning: {str(cleanup_error)}")
                    
            except Exception as e:
                st.error(f"❌ Format detection error: {str(e)}")
    
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
