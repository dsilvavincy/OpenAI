"""
Developer Sidebar - Advanced sidebar with debugging tools and settings
"""
import streamlit as st
import os
from typing import Dict, Any

class DeveloperSidebar:
    """Advanced sidebar component for developer mode."""
    
    def render(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
        """Render comprehensive sidebar with advanced developer tools."""
        st.markdown("### ⚙️ Configuration")
        
        # API Key with auto-loading
        current_api_key = st.session_state.get('api_key', '') or os.getenv("OPENAI_API_KEY", '') or api_key
        updated_api_key = st.text_input(
            "OpenAI API Key", 
            value=current_api_key,
            type="password",
            help="Your OpenAI API key for AI analysis (auto-loaded from .env)"
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
        
        # API validation feedback
        if updated_api_key:
            if updated_api_key.startswith('sk-') and len(updated_api_key) > 20:
                st.success("✅ API key format valid")
                st.caption(f"Key: sk-...{updated_api_key[-8:]}")
            else:
                st.error("❌ Invalid API key format")
                st.caption("Expected format: sk-...")
        
        st.markdown("---")
        
        # Property information
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
