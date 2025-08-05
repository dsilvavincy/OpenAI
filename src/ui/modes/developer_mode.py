"""
Developer Mode - Advanced UI with debugging tools and settings

Developer mode provides:
- All production features plus advanced tools
- Debug console and logging
- Raw data inspection
- Prompt testing and customization
- Advanced settings and controls
- Performance monitoring
"""
import streamlit as st
import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_mode import BaseUIMode

class DeveloperMode(BaseUIMode):
    """
    Developer UI Mode with advanced features and debugging tools.
    
    Features:
    - All production mode features
    - Debug console and detailed logging
    - Raw data inspection tools
    - Prompt testing interface
    - Advanced configuration options
    - Performance monitoring
    - Format management tools
    """
    
    def __init__(self):
        super().__init__(
            mode_name="developer",
            mode_description="Advanced interface with debugging tools, raw data access, and detailed settings"
        )
    
    def render_sidebar(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
        """
        Render comprehensive sidebar with advanced developer tools.
        
        Args:
            api_key: Current API key value
            property_name: Current property name
            property_address: Current property address
            
        Returns:
            Dict with updated configuration values
        """
        st.markdown("### ⚙️ Configuration")
        
        # API Key with advanced options
        default_api_key = os.getenv("OPENAI_API_KEY", api_key)
        updated_api_key = st.text_input(
            "OpenAI API Key", 
            value=default_api_key,
            type="password",
            help="Your OpenAI API key for AI analysis"
        )
        
        # Advanced API settings
        with st.expander("🔧 Advanced API Settings"):
            model_selection = st.selectbox(
                "OpenAI Model",
                ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                index=1,
                help="Select the OpenAI model to use"
            )
            temperature = st.slider(
                "Temperature",
                0.0, 2.0, 0.7, 0.1,
                help="Controls randomness in AI responses"
            )
            max_tokens = st.number_input(
                "Max Tokens",
                100, 4000, 2000,
                help="Maximum length of AI response"
            )
        
        # Detailed API validation
        if updated_api_key:
            if updated_api_key.startswith('sk-') and len(updated_api_key) > 20:
                st.success("✅ API key format valid")
                st.caption(f"Key: sk-...{updated_api_key[-8:]}")
            else:
                st.error("❌ Invalid API key format")
                st.caption("Expected format: sk-...")
        
        st.markdown("---")
        
        # Property information with metadata
        st.markdown("### 🏢 Property Details")
        updated_property_name = st.text_input(
            "Property Name", 
            value=property_name,
            placeholder="e.g., Sunset Apartments"
        )
        updated_property_address = st.text_input(
            "Property Address", 
            value=property_address,
            placeholder="e.g., 123 Main St, City, State"
        )
        
        # Additional property metadata
        with st.expander("📋 Additional Metadata"):
            property_type = st.selectbox(
                "Property Type",
                ["Apartment Complex", "Office Building", "Retail Center", "Mixed Use", "Other"]
            )
            units_count = st.number_input("Number of Units", 0, 10000, 0)
            acquisition_date = st.date_input("Acquisition Date", value=None)
        
        st.markdown("---")
        
        # Debug and Performance Settings
        st.markdown("### 🐛 Debug Settings")
        debug_mode = st.checkbox("Enable Debug Logging", value=False)
        show_raw_data = st.checkbox("Show Raw Data", value=True)
        show_performance = st.checkbox("Show Performance Metrics", value=False)
        
        # Format Detection Settings
        with st.expander("🔍 Format Detection"):
            auto_detect_format = st.checkbox("Auto-detect Format", value=True)
            force_format = st.selectbox(
                "Force Format (if not auto-detecting)",
                ["None", "T12_Monthly_Financial", "Weekly_Database"],
                index=0
            )
        
        st.markdown("---")
        
        # Progress tracking with details
        st.markdown("### 📊 Progress & Status")
        self.display_progress_tracking()
        
        # System status
        with st.expander("🖥️ System Status"):
            st.text(f"Python version: {st.__version__}")
            st.text(f"Session ID: {st.session_state.get('session_id', 'N/A')}")
            if 'last_analysis_time' in st.session_state:
                st.text(f"Last analysis: {st.session_state.last_analysis_time}")
        
        return {
            "api_key": updated_api_key,
            "property_name": updated_property_name,
            "property_address": updated_property_address,
            "model_selection": model_selection,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "property_type": property_type,
            "units_count": units_count,
            "acquisition_date": acquisition_date,
            "debug_mode": debug_mode,
            "show_raw_data": show_raw_data,
            "show_performance": show_performance,
            "auto_detect_format": auto_detect_format,
            "force_format": force_format if force_format != "None" else None
        }
    
    def render_main_content(self, uploaded_file: Optional[Any], config: Dict[str, Any]) -> None:
        """
        Render comprehensive main content with developer tools.
        
        Args:
            uploaded_file: Uploaded file object (if any)
            config: Configuration dictionary from sidebar
        """
        # Developer header with mode info
        st.title("🏢 Property Analysis Dashboard (Developer Mode)")
        st.markdown("Advanced interface with debugging tools, raw data access, and detailed controls")
        
        # Show debug info if enabled
        if config.get('debug_mode', False):
            with st.expander("🐛 Debug Information", expanded=False):
                st.json(config)
        
        # Three-column layout for developer mode
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            self._render_upload_section(uploaded_file, config)
        
        with col2:
            self._render_results_section(uploaded_file, config)
        
        with col3:
            self._render_developer_tools(config)
    
    def _render_upload_section(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render enhanced file upload section with developer tools."""
        st.markdown("### 📁 Upload & Processing")
        
        uploaded_file = st.file_uploader(
            "T12 Excel File",
            type=['xlsx', 'xls'],
            help="Upload your T12 property financial data"
        )
        
        if uploaded_file is not None:
            # Enhanced file processing with format detection
            st.markdown("#### 🔍 File Analysis")
            
            # Show file details
            st.info(f"**File:** {uploaded_file.name}")
            st.info(f"**Size:** {uploaded_file.size:,} bytes")
            st.info(f"**Type:** {uploaded_file.type}")
            
            # Format detection
            if config.get('auto_detect_format', True):
                with st.spinner("Detecting format..."):
                    from src.core.format_registry import format_registry
                    import tempfile
                    
                    # Save file temporarily for format detection
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        processor = format_registry.detect_format(tmp_file_path)
                        if processor:
                            st.success(f"✅ Detected: {processor.format_name}")
                        else:
                            st.warning("⚠️ Format not detected")
                    except Exception as e:
                        st.error(f"❌ Format detection error: {str(e)}")
                    finally:
                        os.unlink(tmp_file_path)  # Clean up temp file
            
            # Process file with detailed feedback
            df = self.handle_file_upload(uploaded_file)
            
            if df is not None:
                st.success(f"✅ Processing complete")
                st.info(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                st.info(f"**Metrics:** {df['Metric'].nunique()} unique")
                st.info(f"**Time periods:** {df[~df['IsYTD']]['Period'].nunique() if 'Period' in df.columns else 'N/A'}")
                
                # Store in session state
                st.session_state['processed_df'] = df
                st.session_state['uploaded_file'] = uploaded_file
                
                # Raw data viewer (developer mode)
                if config.get('show_raw_data', True):
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
    
    def _render_results_section(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render enhanced results section with developer insights."""
        st.markdown("### 📈 Analysis Results")
        
        if 'processed_df' not in st.session_state:
            st.info("👆 Upload a T12 file to begin analysis")
            return
        
        df = st.session_state['processed_df']
        api_key = config.get('api_key', '')
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
            return
        
        try:
            # Use new scalable system with performance monitoring
            from src.core.kpi_registry import kpi_registry
            import time
            
            format_name = config.get('force_format', "T12_Monthly_Financial")
            
            # KPI Generation with timing
            start_time = time.time()
            with st.spinner("📊 Generating KPI analysis..."):
                kpi_summary = kpi_registry.calculate_kpis(df, format_name)
            kpi_time = time.time() - start_time
            
            # Show performance metrics if enabled
            if config.get('show_performance', False):
                st.metric("KPI Generation Time", f"{kpi_time:.2f}s")
            
            # Enhanced KPI display
            st.markdown("#### 📋 Financial Summary")
            
            # KPI summary with analytics
            tabs = st.tabs(["📄 Summary", "📊 Analytics", "🔧 Debug"])
            
            with tabs[0]:
                st.text_area("KPI Summary", kpi_summary, height=400, label_visibility="collapsed")
            
            with tabs[1]:
                self._render_kpi_analytics(df, format_name)
            
            with tabs[2]:
                if config.get('debug_mode', False):
                    self._render_kpi_debug(df, format_name, kpi_summary)
            
            # Enhanced AI Analysis
            self._render_enhanced_ai_analysis(df, kpi_summary, config)
            
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
            if config.get('debug_mode', False):
                st.exception(e)
    
    def _render_developer_tools(self, config: Dict[str, Any]):
        """Render developer tools panel."""
        st.markdown("### 🛠️ Developer Tools")
        
        # Prompt testing tools
        from src.ui.data_analysis import display_prompt_testing_section
        
        if 'processed_df' in st.session_state:
            df = st.session_state['processed_df']
            
            # Get current KPI summary for prompt testing
            try:
                from src.core.kpi_registry import kpi_registry
                format_name = config.get('force_format', "T12_Monthly_Financial")
                kpi_summary = kpi_registry.calculate_kpis(df, format_name)
                
                st.markdown("#### 🧪 Prompt Testing")
                display_prompt_testing_section(kpi_summary, df)
                
            except Exception as e:
                st.error(f"Error loading prompt testing: {str(e)}")
        
        # Format registry info
        st.markdown("#### 📋 Format Registry")
        with st.expander("Available Formats"):
            from src.core.format_registry import format_registry
            formats = format_registry.get_registered_formats()
            for fmt in formats:
                st.text(f"• {fmt['name']}: {fmt['description']}")
        
        # System tools
        st.markdown("#### ⚙️ System Tools")
        if st.button("🔄 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
        
        if st.button("🧹 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session reset!")
            st.rerun()
    
    def _render_kpi_analytics(self, df: pd.DataFrame, format_name: str):
        """Render KPI analytics for developer mode."""
        from src.core.kpi_registry import kpi_registry
        
        # Get calculator info
        calc_info = kpi_registry.get_calculator_info(format_name)
        if calc_info:
            st.json(calc_info)
        
        # Key metrics analysis
        key_metrics = kpi_registry.get_key_metrics(format_name)
        if key_metrics:
            st.write("**Key Metrics:**")
            for metric in key_metrics:
                st.text(f"• {metric}")
    
    def _render_kpi_debug(self, df: pd.DataFrame, format_name: str, kpi_summary: str):
        """Render KPI debug information."""
        from src.core.kpi_registry import kpi_registry
        
        st.write("**Debug Information:**")
        st.text(f"Format: {format_name}")
        st.text(f"DataFrame shape: {df.shape}")
        st.text(f"Summary length: {len(kpi_summary)} characters")
        
        # Calculation issues
        issues = kpi_registry.get_calculation_issues(format_name)
        if issues:
            st.write("**Calculation Issues:**")
            for issue in issues:
                st.text(f"• {issue}")
        else:
            st.success("✅ No calculation issues")
    
    def _render_enhanced_ai_analysis(self, df: pd.DataFrame, kpi_summary: str, config: Dict[str, Any]):
        """Render AI analysis with developer enhancements."""
        from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options
        
        st.markdown("#### 🤖 AI Analysis")
        
        # Enhanced AI analysis with custom parameters
        processed_output = display_ai_analysis_section(
            df, 
            kpi_summary, 
            config['api_key'], 
            config['property_name'], 
            config['property_address']
        )
        
        if processed_output:
            # Enhanced results display
            st.markdown("#### 📄 Analysis Report")
            display_analysis_results(processed_output)
            
            # Developer export options
            st.markdown("#### 💾 Export Options")
            display_export_options(processed_output, config['property_name'])
    
    def get_layout_config(self) -> Dict[str, Any]:
        """
        Get developer mode layout configuration.
        
        Returns:
            Dict with layout settings for developer mode
        """
        return {
            "columns": [1, 2, 1],  # Three-column layout
            "sidebar_width": "wide",
            "show_debug": True,
            "show_raw_data": True,
            "show_advanced_settings": True,
            "compact_mode": False
        }
    
    def should_show_feature(self, feature_name: str) -> bool:
        """
        Developer mode shows all features.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: Always True for developer mode
        """
        return True  # Developer mode shows everything
    
    def display_mode_header(self):
        """Display developer mode header with additional info."""
        st.info("🛠️ **Developer Mode:** Advanced tools and debugging features enabled")
    
    def _set_default_session_state(self):
        """Set default session state for developer mode."""
        if "developer_debug_enabled" not in st.session_state:
            st.session_state.developer_debug_enabled = False
        if "developer_show_raw_data" not in st.session_state:
            st.session_state.developer_show_raw_data = True
        if "developer_performance_monitoring" not in st.session_state:
            st.session_state.developer_performance_monitoring = True
