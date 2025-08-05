"""
Production Mode - Clean, minimal UI focused on core workflow

Production mode provides:
- Streamlined upload → process → analyze → export workflow  
- Clean, professional interface
- Essential controls only
- Maximized space for results
- Minimal distractions
"""
import streamlit as st
import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_mode import BaseUIMode

class ProductionMode(BaseUIMode):
    """
    Production UI Mode for clean, professional user experience.
    
    Features:
    - Minimal sidebar with essential controls
    - Clean main content layout
    - Focus on results and export
    - Professional appearance
    """
    
    def __init__(self):
        super().__init__(
            mode_name="production",
            mode_description="Clean, professional interface focused on core analysis workflow"
        )
    
    def render_sidebar(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
        """
        Render clean, minimal sidebar for production use.
        
        Args:
            api_key: Current API key value
            property_name: Current property name
            property_address: Current property address
            
        Returns:
            Dict with updated configuration values
        """
        st.markdown("### ⚙️ Configuration")
        
        # API Key input (streamlined)
        # Priority: session state → environment → current value
        current_api_key = st.session_state.get('api_key', '') or os.getenv("OPENAI_API_KEY", '') or api_key
        
        updated_api_key = st.text_input(
            "OpenAI API Key", 
            value=current_api_key,
            type="password",
            help="Your OpenAI API key for AI analysis (auto-loaded from .env)"
        )
        
        # Simple validation feedback
        if updated_api_key:
            if updated_api_key.startswith('sk-') and len(updated_api_key) > 20:
                st.success("✅ API key validated")
            else:
                st.error("❌ Invalid API key format")
        
        st.markdown("---")
        
        # Property information (streamlined)
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
        
        st.markdown("---")
        
        # Progress tracking (compact)
        st.markdown("### 📊 Progress")
        self.display_progress_tracking()
        
        return {
            "api_key": updated_api_key,
            "property_name": updated_property_name,
            "property_address": updated_property_address
        }
    
    def render_main_content(self, uploaded_file: Optional[Any], config: Dict[str, Any]) -> None:
        """
        Render clean main content area focused on workflow.
        
        Args:
            uploaded_file: Uploaded file object (if any)
            config: Configuration dictionary from sidebar
        """
        # Clean, minimal header
        st.title("🏢 Property Analysis Dashboard")
        
        # Check if we have processed data to determine layout
        if 'processed_df' in st.session_state and st.session_state['processed_df'] is not None:
            # Results-first layout: show results prominently, upload section minimized
            self._render_results_first_layout(uploaded_file, config)
        else:
            # Upload-first layout: show upload section prominently when no data
            self._render_upload_first_layout(uploaded_file, config)
    
    def _render_upload_first_layout(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render layout when no data is processed - focus on upload."""
        st.markdown("Upload your T12 Excel file for AI-powered property performance analysis")
        
        # Center the upload section
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            self._render_upload_section(uploaded_file, config)
    
    def _render_results_first_layout(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render layout when data is processed - focus on results."""
        # Compact file status at top
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                if 'uploaded_file' in st.session_state:
                    file_name = st.session_state['uploaded_file'].name
                    df = st.session_state['processed_df']
                    st.success(f"✅ **{file_name}** - {df.shape[0]} rows, {df['Metric'].nunique()} metrics")
            with col2:
                if st.button("🔄 Upload New File", help="Upload a different T12 file"):
                    # Clear session state to return to upload mode
                    for key in ['processed_df', 'uploaded_file', 'current_uploaded_file']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        st.markdown("---")
        
        # Results take up main content area
        self._render_results_section(uploaded_file, config)

    def _render_upload_section(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render the file upload section - streamlined for production."""
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
                df = self.handle_file_upload(uploaded_file)
                
                if df is not None:
                    # Store in session state
                    st.session_state['processed_df'] = df
                    st.session_state['uploaded_file'] = uploaded_file
                    st.success("✅ File processed successfully!")
                    st.rerun()  # Refresh to show results layout
    
    def _render_results_section(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render the analysis results section - production focused."""
        # Check if we have processed data
        if 'processed_df' not in st.session_state:
            st.info("👆 Upload a T12 file to begin analysis")
            return
        
        df = st.session_state['processed_df']
        api_key = config.get('api_key', '')
        property_name = config.get('property_name', '')
        property_address = config.get('property_address', '')
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
            return
        
        try:
            # Use new scalable KPI system
            from src.core.format_registry import format_registry, process_file
            from src.core.kpi_registry import kpi_registry
            
            # Get format processor info (we already processed the file)
            format_name = "T12_Monthly_Financial"
            
            # Generate KPI Summary (only if not cached)
            if 'kpi_summary' not in st.session_state:
                with st.spinner("📊 Generating KPI analysis..."):
                    kpi_summary = kpi_registry.calculate_kpis(df, format_name)
                    st.session_state['kpi_summary'] = kpi_summary
            else:
                kpi_summary = st.session_state['kpi_summary']
            
            # Main analysis section
            self._render_ai_analysis(df, kpi_summary, config)
            
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
            st.info("💡 Please check your data and API key, then try again")
    
    def _render_ai_analysis(self, df: pd.DataFrame, kpi_summary: str, config: Dict[str, Any]):
        """Render AI analysis section - production focused."""
        from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options, get_existing_analysis_results
        from src.utils.format_detection import get_stored_format
        
        # Check for existing analysis results first
        existing_output = get_existing_analysis_results()
        
        if existing_output:
            # Display existing results immediately - production view
            st.markdown("## 📊 Analysis Report")
            display_analysis_results(existing_output)
            
            # Export section
            st.markdown("---")
            st.markdown("## 💾 Export Report")
            st.markdown("Download your analysis in multiple professional formats:")
            display_export_options(existing_output, config['property_name'], export_type="full")
            
            # Option to regenerate analysis
            st.markdown("---")
            if st.button("🔄 Generate New Analysis", type="secondary", use_container_width=True):
                from src.ui.ai_analysis import clear_analysis_results
                clear_analysis_results()
                st.rerun()
            return
        
        # No existing results - show analysis generation interface
        # Get the detected format for this analysis
        detected_format = get_stored_format()
        
        # Streamlined AI analysis interface with format-specific prompts
        processed_output = display_ai_analysis_section(
            df, 
            kpi_summary, 
            config['api_key'], 
            config['property_name'], 
            config['property_address'],
            detected_format
        )
        
        if processed_output:
            # Results take center stage
            st.markdown("---")
            st.markdown("## � Analysis Report")
            display_analysis_results(processed_output)
            
            # Prominent export section at bottom
            st.markdown("---")
            st.markdown("## 💾 Export Report")
            st.markdown("Download your analysis in multiple professional formats:")
            display_export_options(processed_output, config['property_name'], export_type="full")
    
    def get_layout_config(self) -> Dict[str, Any]:
        """
        Get production mode layout configuration.
        
        Returns:
            Dict with layout settings optimized for production
        """
        return {
            "columns": [1, 2.5],  # More space for results
            "sidebar_width": "narrow",
            "show_debug": False,
            "show_raw_data": False,
            "show_advanced_settings": False,
            "compact_mode": True
        }
    
    def should_show_feature(self, feature_name: str) -> bool:
        """
        Production mode feature visibility rules.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: True if feature should be shown in production mode
        """
        # Hide debug and advanced features in production mode
        hidden_features = [
            "debug_console",
            "raw_data_viewer", 
            "prompt_testing",
            "advanced_settings",
            "format_manager",
            "performance_metrics"
        ]
        
        return feature_name not in hidden_features
    
    def display_mode_header(self):
        """Display production mode header."""
        # Clean, minimal header - already handled in render_main_content
        pass
    
    def _set_default_session_state(self):
        """Set default session state for production mode."""
        # Minimal session state for production
        if "production_theme" not in st.session_state:
            st.session_state.production_theme = "clean"
        if "production_auto_export" not in st.session_state:
            st.session_state.production_auto_export = False
