"""
Production Sidebar - Clean, minimal sidebar for production mode

Handles configuration options with focus on essentials:
- API key input with validation
- Property details
- Display options (Structured vs Raw Response side-by-side)
- Progress tracking
"""
import streamlit as st
import os
from typing import Dict, Any


class ProductionSidebar:
    """Production mode sidebar with essential configuration options."""
    
    def render(self, api_key: str, property_name: str, property_address: str) -> Dict[str, Any]:
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
        
        # Advanced AI Settings (collapsible)
        with st.expander("🤖 AI Model Settings", expanded=False):
            model_selection = st.selectbox(
                "OpenAI Model",
                ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                index=0,  # Default to gpt-4o (best)
                help="gpt-4o: Latest & most capable | gpt-4-turbo: Fast & high quality | gpt-4: Standard | gpt-3.5-turbo: Fastest & cheapest"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider(
                    "Temperature", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=0.2,  # Lower for more consistent analysis
                    step=0.1,
                    help="Lower = more consistent, Higher = more creative"
                )
            
            with col2:
                # No token limit in production mode - allow unlimited response length
                st.info("🚀 Unlimited Tokens - Complete detailed analysis without restrictions")
            
            st.info(f"💡 **Current:** {model_selection} | Temp: {temperature} | Unlimited Tokens")
        
        # Progress tracking (compact)
        st.markdown("### 📊 Progress")
        self._display_progress_tracking()
        
        return {
            "api_key": updated_api_key,
            "property_name": updated_property_name,
            "property_address": updated_property_address,
            "model_selection": model_selection,
            "temperature": temperature
            # No max_tokens - allowing unlimited response length
        }
    
    def _display_progress_tracking(self):
        """Display compact progress tracking for production mode."""
        # Simple progress indicators
        progress_items = []
        
        if 'uploaded_file' in st.session_state:
            progress_items.append("✅ File uploaded")
        else:
            progress_items.append("⏳ Upload file")
        
        if 'processed_df' in st.session_state:
            progress_items.append("✅ Data processed")
        else:
            progress_items.append("⏳ Process data")
        
        if 'analysis_results' in st.session_state:
            progress_items.append("✅ Analysis complete")
        else:
            progress_items.append("⏳ Generate analysis")
        
        # Display compact progress
        for item in progress_items:
            st.markdown(f"- {item}")
