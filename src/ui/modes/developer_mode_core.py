"""
Developer Mode Core - Main class with essential functionality
"""
import streamlit as st
from typing import Optional, Dict, Any
from .base_mode import BaseUIMode
from .developer_sidebar import DeveloperSidebar
from .developer_upload import DeveloperUploadSection
from .developer_results import DeveloperResultsSection
from .developer_tools import DeveloperToolsPanel

class DeveloperMode(BaseUIMode):
    """Developer UI Mode with advanced features and debugging tools."""
    
    def __init__(self):
        super().__init__(
            mode_name="developer",
            mode_description="Advanced interface with debugging tools, raw data access, and detailed settings"
        )
        
        # Initialize components
        self.sidebar = DeveloperSidebar()
        self.upload_section = DeveloperUploadSection()
        self.results_section = DeveloperResultsSection()
        self.tools_panel = DeveloperToolsPanel()
    
    def render_sidebar(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
        """Render comprehensive sidebar with advanced developer tools."""
        return self.sidebar.render(api_key, property_name, property_address)
    
    def render_main_content(self, uploaded_file: Optional[Any], config: Dict[str, Any]) -> None:
        """Render comprehensive main content with developer tools."""
        # Display Branding Logo
        import os
        logo_path = os.path.join("src", "ui", "assets", "logo_primary.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=250)
            st.markdown("<br>", unsafe_allow_html=True) # Subtle spacer

        st.title("🏢 Property Analysis Dashboard (Developer Mode)")
        st.markdown("Advanced interface with debugging tools, raw data access, and detailed controls")
        
        # Show debug info if enabled
        if config.get('debug_mode', False):
            with st.expander("🐛 Debug Information", expanded=False):
                st.json(config)
        
        # Three-column layout for developer mode
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            self.upload_section.render(uploaded_file, config)
        
        with col2:
            self.results_section.render(uploaded_file, config)
        
        with col3:
            self.tools_panel.render(config)
    
    def get_layout_config(self) -> Dict[str, Any]:
        """Get developer mode layout configuration."""
        return {
            "columns": [1, 2, 1],  # Three-column layout
            "sidebar_width": "wide",
            "show_debug": True,
            "show_raw_data": True,
            "show_advanced_settings": True,
            "compact_mode": False
        }
    
    def should_show_feature(self, feature_name: str) -> bool:
        """Developer mode shows all features."""
        return True
    
    def display_mode_header(self):
        """Display developer mode header with additional info."""
        st.info("🛠️ **Developer Mode:** Advanced tools and debugging features enabled")
