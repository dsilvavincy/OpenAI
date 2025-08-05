"""
Base UI Mode - Abstract base class for all UI modes

This provides the interface that all UI modes must implement
to ensure consistent behavior across different modes.
"""
from abc import ABC, abstractmethod
import streamlit as st
from typing import Optional, Dict, Any
import pandas as pd

class BaseUIMode(ABC):
    """
    Abstract base class for all UI modes.
    
    Each UI mode must implement:
    - Mode-specific layout and components
    - Sidebar configuration
    - Main content area rendering
    - User preference handling
    """
    
    def __init__(self, mode_name: str, mode_description: str):
        """
        Initialize the base UI mode.
        
        Args:
            mode_name: Unique name for this mode (e.g., "production", "developer")
            mode_description: Human-readable description of this mode
        """
        self.mode_name = mode_name
        self.mode_description = mode_description
    
    @abstractmethod
    def render_sidebar(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
        """
        Render the sidebar for this mode.
        
        Args:
            api_key: Current API key value
            property_name: Current property name
            property_address: Current property address
            
        Returns:
            Dict with updated configuration values
        """
        pass
    
    @abstractmethod
    def render_main_content(self, uploaded_file: Optional[Any], config: Dict[str, Any]) -> None:
        """
        Render the main content area for this mode.
        
        Args:
            uploaded_file: Uploaded file object (if any)
            config: Configuration dictionary from sidebar
        """
        pass
    
    @abstractmethod
    def get_layout_config(self) -> Dict[str, Any]:
        """
        Get layout configuration for this mode.
        
        Returns:
            Dict with layout settings (columns, spacing, etc.)
        """
        pass
    
    def get_mode_info(self) -> Dict[str, Any]:
        """
        Get information about this UI mode.
        
        Returns:
            Dict with mode metadata
        """
        return {
            "name": self.mode_name,
            "description": self.mode_description,
            "class": self.__class__.__name__
        }
    
    def initialize_session_state(self):
        """Initialize mode-specific session state variables."""
        if f"{self.mode_name}_initialized" not in st.session_state:
            st.session_state[f"{self.mode_name}_initialized"] = True
            self._set_default_session_state()
    
    def _set_default_session_state(self):
        """Set default session state values. Override in subclasses."""
        pass
    
    def save_user_preferences(self, preferences: Dict[str, Any]):
        """
        Save user preferences for this mode.
        
        Args:
            preferences: Dictionary of user preferences
        """
        st.session_state[f"{self.mode_name}_preferences"] = preferences
    
    def load_user_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences for this mode.
        
        Returns:
            Dict with user preferences
        """
        return st.session_state.get(f"{self.mode_name}_preferences", {})
    
    def display_mode_header(self):
        """Display mode-specific header information."""
        pass  # Optional - can be overridden by subclasses
    
    def display_mode_footer(self):
        """Display mode-specific footer information.""" 
        pass  # Optional - can be overridden by subclasses
    
    def handle_file_upload(self, uploaded_file: Any) -> Optional[pd.DataFrame]:
        """
        Handle file upload processing. Can be overridden for mode-specific handling.
        
        Args:
            uploaded_file: Uploaded file object
            
        Returns:
            Processed DataFrame or None
        """
        # Default implementation - can be overridden
        from src.ui.validation import validate_uploaded_file
        from src.ui.data_analysis import display_file_processing_section
        
        if uploaded_file is not None:
            # File validation
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
            
            # Process the file
            return display_file_processing_section(uploaded_file)
        
        return None
    
    def display_progress_tracking(self):
        """Display progress tracking. Can be mode-specific."""
        from src.ui.progress import display_progress
        display_progress()
    
    def get_column_layout(self) -> tuple:
        """
        Get column layout for this mode.
        
        Returns:
            Tuple of column ratios
        """
        layout_config = self.get_layout_config()
        return layout_config.get("columns", [1, 2])
    
    def should_show_feature(self, feature_name: str) -> bool:
        """
        Determine if a feature should be shown in this mode.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: True if feature should be shown
        """
        # Default implementation - can be overridden
        return True
