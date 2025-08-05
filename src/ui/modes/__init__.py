"""
UI Modes Package - Dual-Mode Interface System

This package provides a scalable dual-mode UI system for the T12 Property Analysis Tool:

- **Production Mode**: Clean, minimal interface focused on core workflow
- **Developer Mode**: Advanced interface with debugging tools and detailed controls

Architecture:
- BaseUIMode: Abstract base class defining the interface contract
- ProductionMode: Simplified UI for end-users
- DeveloperMode: Advanced UI for developers and power users
- UIModeManager: Manages mode switching and preferences

Key Features:
- Seamless mode switching
- User preference persistence
- Mode-specific layouts and features
- Extensible architecture for future modes
"""

from .mode_manager import UIModeManager, render_current_mode, get_current_mode, should_show_feature, get_layout_config
from .base_mode import BaseUIMode
from .production_mode import ProductionMode
from .developer_mode import DeveloperMode

__all__ = [
    'UIModeManager',
    'render_current_mode',
    'get_current_mode', 
    'should_show_feature',
    'get_layout_config',
    'BaseUIMode',
    'ProductionMode',
    'DeveloperMode'
]

# Version info
__version__ = "1.0.0"
