"""
Production Mode Core - Main orchestration for production UI

This module handles the core logic and workflow orchestration for production mode,
delegating specific functionality to specialized components.
"""
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from .base_mode import BaseUIMode


class ProductionModeCore(BaseUIMode):
    """
    Core production mode handler that orchestrates the clean, professional workflow.
    
    Delegates specific functionality to:
    - ProductionSidebar: Sidebar configuration
    - ProductionUpload: File upload handling  
    - ProductionResults: Analysis display with side-by-side views
    """
    
    def __init__(self):
        super().__init__(
            mode_name="production",
            mode_description="Clean, professional interface focused on core analysis workflow"
        )
    
    def render_sidebar(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
        """Delegate sidebar rendering to ProductionSidebar."""
        from .production_sidebar import ProductionSidebar
        sidebar = ProductionSidebar()
        return sidebar.render(api_key, property_name, property_address)
    
    def render_main_content(self, uploaded_file: Optional[Any], config: Dict[str, Any]) -> None:
        """
        Render main content area with adaptive layout based on data state.
        
        Args:
            uploaded_file: Uploaded file object (if any)
            config: Configuration dictionary from sidebar
        """
        # Inject Custom CSS for Branding
        from src.ui.theme import COLOR_NAVY, COLOR_TEAL, COLOR_ORANGE, COLOR_SAGE, COLOR_CREAM
        
        st.markdown(f"""
        <style>
            /* Header */
            h1, h2, h3 {{
                color: {COLOR_NAVY} !important; 
            }}
            /* Streamlit Buttons */
            .stButton > button {{
                background-color: {COLOR_NAVY} !important;
                color: #ffffff !important;
                border: none !important;
            }}
            .stButton > button:hover {{
                background-color: {COLOR_TEAL} !important;
            }}
            /* Sidebar background fallback if needed, though Streamlit controls this mostly via config */
            
            /* Metric / Important values */
            [data-testid="stMetricValue"] {{
                color: {COLOR_ORANGE} !important;
            }}
            
            /* Custom separators */
            hr {{
                border-color: {COLOR_SAGE} !important;
            }}
        </style>
        """, unsafe_allow_html=True)

        # Display Branding Logo + Header in 2-Column Grid for better alignment
        import os
        logo_path = os.path.join("src", "ui", "assets", "logo_primary.jpg")
        
        # Use a container for the header to control spacing
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if os.path.exists(logo_path):
                    st.image(logo_path, use_container_width=True)
                else:
                    st.write("Logo not found")
            
            with col2:
                # Add some vertical padding to align text with logo center
                st.markdown('<div style="padding-top: 10px;"></div>', unsafe_allow_html=True)
                st.title("Property Analysis Dashboard")
                st.markdown("AI-powered property performance analysis")
        
        # Check if we have processed monthly and YTD data to determine layout
        if (
            'processed_monthly_df' in st.session_state and st.session_state['processed_monthly_df'] is not None and
            'processed_ytd_df' in st.session_state and st.session_state['processed_ytd_df'] is not None
        ):
            # Results-first layout: show results prominently, upload section minimized
            self._render_results_first_layout(uploaded_file, config)
        else:
            # Upload-first layout: show upload section prominently when no data
            self._render_upload_first_layout(uploaded_file, config)
    
    def _render_upload_first_layout(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render layout when no data is processed - focus on upload."""
        
        st.markdown("---") # Visual separator
        
        # Center the upload section
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            from .production_upload import ProductionUpload
            upload_handler = ProductionUpload()
            upload_handler.render(uploaded_file, config)
    
    def _render_results_first_layout(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render layout when data is processed - focus on results."""
        # Compact file status at top
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                if 'uploaded_file' in st.session_state:
                    file_name = st.session_state['uploaded_file'].name
                    monthly_df = st.session_state.get('processed_monthly_df')
                    ytd_df = st.session_state.get('processed_ytd_df')
                    msg = f"✅ **{file_name}**"
                    if monthly_df is not None:
                        msg += f" - {monthly_df.shape[0]} monthly rows, {monthly_df['Metric'].nunique()} metrics"
                    if ytd_df is not None:
                        msg += f" | {ytd_df.shape[0]} YTD rows"
                    st.success(msg)
            with col2:
                if st.button("🔄 Upload New File", help="Upload a different T12 file"):
                    # Clear session state to return to upload mode
                    keys_to_clear = [
                        'processed_df', 
                        'uploaded_file', 
                        'current_uploaded_file',
                        'processed_monthly_df',
                        'processed_ytd_df',
                        'processed_analysis_output',
                        'last_analyzed_property',
                        'selected_property',
                        'production_file_uploader'
                    ]
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        st.markdown("---")
        
        # Results take up main content area
        from .production_results import ProductionResults
        results_handler = ProductionResults()
        results_handler.render(uploaded_file, config)
    
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
            "show_raw_response": True,  # Available in production
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
