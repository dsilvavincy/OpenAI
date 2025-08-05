"""
Production Mode - Clean, minimal UI focused on core workflow

Production mode provides:
- Streamlined upload → process → analyze → export workflow  
- Clean, professional interface
- Essential controls only
- Maximized space for results
- Minimal distractions

This file serves as the entry point and delegates functionality to specialized components:
- ProductionModeCore: Main orchestration
- ProductionSidebar: Sidebar configuration
- ProductionUpload: File upload handling
- ProductionResults: Analysis display with side-by-side views
"""

# Import the core production mode implementation
from .production_mode_core import ProductionModeCore

# Create an alias for backward compatibility
ProductionMode = ProductionModeCore
