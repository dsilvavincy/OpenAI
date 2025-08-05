"""
UI Mode Manager - Manages switching between different UI modes

Provides:
- Mode registration and switching
- User preference persistence
- Mode-specific configuration
- Seamless transitions between modes
"""
import streamlit as st
from typing import Dict, Any, Optional
from .base_mode import BaseUIMode
from .production_mode import ProductionMode
from .developer_mode import DeveloperMode

class UIModeManager:
    """
    Manager for handling UI mode switching and configuration.
    
    Features:
    - Mode registration and management
    - User preference persistence
    - Smooth mode transitions
    - Configuration management
    """
    
    def __init__(self):
        """Initialize the UI mode manager with built-in modes."""
        self._modes: Dict[str, BaseUIMode] = {}
        self._register_built_in_modes()
    
    def _register_built_in_modes(self):
        """Register all built-in UI modes."""
        self.register_mode(ProductionMode())
        self.register_mode(DeveloperMode())
    
    def register_mode(self, mode: BaseUIMode):
        """
        Register a new UI mode.
        
        Args:
            mode: UI mode instance
        """
        if not isinstance(mode, BaseUIMode):
            raise ValueError("Mode must inherit from BaseUIMode")
        
        self._modes[mode.mode_name] = mode
        print(f"Registered UI mode: {mode.mode_name}")
    
    def get_available_modes(self) -> Dict[str, str]:
        """
        Get available modes and their descriptions.
        
        Returns:
            Dict mapping mode names to descriptions
        """
        return {name: mode.mode_description for name, mode in self._modes.items()}
    
    def get_current_mode(self) -> str:
        """
        Get the currently active mode name.
        
        Returns:
            str: Current mode name
        """
        return st.session_state.get('ui_mode', 'production')
    
    def set_current_mode(self, mode_name: str):
        """
        Set the current UI mode.
        
        Args:
            mode_name: Name of the mode to activate
        """
        if mode_name not in self._modes:
            available = list(self._modes.keys())
            raise ValueError(f"Unknown mode: {mode_name}. Available: {available}")
        
        st.session_state['ui_mode'] = mode_name
        print(f"Switched to UI mode: {mode_name}")
    
    def render_mode_selector(self) -> str:
        """
        Render the mode selection UI element.
        
        Returns:
            str: Selected mode name
        """
        available_modes = self.get_available_modes()
        mode_options = {
            "🏭 Production": "production",
            "🛠️ Developer": "developer"
        }
        
        current_mode = self.get_current_mode()
        current_label = next(
            (label for label, mode in mode_options.items() if mode == current_mode),
            "🏭 Production"
        )
        
        selected_label = st.selectbox(
            "Interface Mode",
            options=list(mode_options.keys()),
            index=list(mode_options.values()).index(current_mode),
            help="Choose between Production (clean) or Developer (advanced) interface"
        )
        
        selected_mode = mode_options[selected_label]
        
        # Update mode if changed
        if selected_mode != current_mode:
            self.set_current_mode(selected_mode)
            st.rerun()  # Refresh to apply new mode
        
        return selected_mode
    
    def render_current_mode(self, uploaded_file: Optional[Any] = None) -> None:
        """
        Render the currently active UI mode.
        
        Args:
            uploaded_file: Optional uploaded file object
        """
        current_mode_name = self.get_current_mode()
        mode = self._modes.get(current_mode_name)
        
        if not mode:
            st.error(f"Unknown UI mode: {current_mode_name}")
            return
        
        # Initialize mode if needed
        mode.initialize_session_state()
        
        # Display mode header if available
        mode.display_mode_header()
        
        # Render sidebar and get configuration
        with st.sidebar:
            # Mode selector at top of sidebar
            st.markdown("### 🔧 Interface Mode")
            selected_mode = self.render_mode_selector()
            
            st.markdown("---")
            
            # Mode-specific sidebar
            config = mode.render_sidebar(
                api_key=st.session_state.get('api_key', ''),
                property_name=st.session_state.get('property_name', ''),
                property_address=st.session_state.get('property_address', '')
            )
            
            # Save configuration to session state
            self._save_config_to_session(config)
        
        # Render main content
        mode.render_main_content(uploaded_file, config)
        
        # Display mode footer if available
        mode.display_mode_footer()
    
    def _save_config_to_session(self, config: Dict[str, Any]):
        """
        Save configuration to session state.
        
        Args:
            config: Configuration dictionary to save
        """
        for key, value in config.items():
            st.session_state[key] = value
    
    def get_mode_info(self, mode_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific mode.
        
        Args:
            mode_name: Name of the mode
            
        Returns:
            Dict with mode information, or None if not found
        """
        mode = self._modes.get(mode_name)
        return mode.get_mode_info() if mode else None
    
    def should_show_feature(self, feature_name: str) -> bool:
        """
        Check if a feature should be shown in the current mode.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: True if feature should be shown
        """
        current_mode_name = self.get_current_mode()
        mode = self._modes.get(current_mode_name)
        
        return mode.should_show_feature(feature_name) if mode else True
    
    def get_layout_config(self) -> Dict[str, Any]:
        """
        Get layout configuration for the current mode.
        
        Returns:
            Dict with layout configuration
        """
        current_mode_name = self.get_current_mode()
        mode = self._modes.get(current_mode_name)
        
        return mode.get_layout_config() if mode else {}
    
    def handle_mode_transition(self, from_mode: str, to_mode: str):
        """
        Handle transitions between modes.
        
        Args:
            from_mode: Previous mode name
            to_mode: New mode name
        """
        # Save preferences from previous mode
        if from_mode in self._modes:
            prev_mode = self._modes[from_mode]
            preferences = {
                key: value for key, value in st.session_state.items()
                if key.startswith(f"{from_mode}_")
            }
            prev_mode.save_user_preferences(preferences)
        
        # Load preferences for new mode
        if to_mode in self._modes:
            new_mode = self._modes[to_mode]
            preferences = new_mode.load_user_preferences()
            st.session_state.update(preferences)
    
    def reset_all_modes(self):
        """Reset all mode configurations and preferences."""
        # Clear mode-specific session state
        keys_to_remove = [
            key for key in st.session_state.keys()
            if any(key.startswith(f"{mode_name}_") for mode_name in self._modes.keys())
        ]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        # Reset to production mode
        st.session_state['ui_mode'] = 'production'

# Global UI mode manager instance
ui_mode_manager = UIModeManager()

# Convenience functions for easy access
def get_current_mode() -> str:
    """Get current UI mode using global manager."""
    return ui_mode_manager.get_current_mode()

def render_current_mode(uploaded_file: Optional[Any] = None) -> None:
    """Render current UI mode using global manager."""
    return ui_mode_manager.render_current_mode(uploaded_file)

def should_show_feature(feature_name: str) -> bool:
    """Check if feature should be shown using global manager."""
    return ui_mode_manager.should_show_feature(feature_name)

def get_layout_config() -> Dict[str, Any]:
    """Get layout config using global manager."""
    return ui_mode_manager.get_layout_config()
