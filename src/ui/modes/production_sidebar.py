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
import time
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
        # Display Branding Logo
        logo_path = os.path.join("src", "ui", "assets", "logo_secondary.jpg")
        if os.path.exists(logo_path):
            st.sidebar.image(logo_path, use_container_width=True)
            st.sidebar.markdown("---")
        
        st.markdown("### ⚙️ Configuration")
        
        # API Key input (streamlined)
        # Priority: session state → environment → current value
        # Custom CSS to hide the password visibility toggle (the eye icon)
        st.markdown("""
            <style>
            button[aria-label="Show password"] { display: none !important; }
            div[data-testid="stTextInput"] button { display: none !important; }
            </style>
        """, unsafe_allow_html=True)

        # Initialize API key in session state if not present
        if 'api_key_input' not in st.session_state:
            saved_key = self._get_saved_api_key()
            st.session_state['api_key_input'] = saved_key or st.session_state.get('api_key', '') or os.getenv("OPENAI_API_KEY", '') or api_key
        
        # Ensure 'api_key' in session state matches the input for other components
        st.session_state['api_key'] = st.session_state['api_key_input']

        updated_api_key = st.text_input(
            "OpenAI API Key", 
            value=st.session_state['api_key_input'],
            type="password",
            help="Your OpenAI API key (Masked for security. Clear and paste to update.)",
            key="api_key_field"
        )
        st.session_state['api_key_input'] = updated_api_key
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if updated_api_key:
                if st.button("🗑️ Clear Key", use_container_width=True):
                    st.session_state['api_key_input'] = ""
                    st.session_state['api_key'] = ""
                    st.rerun()

        # Check if this key matches the stored default
        saved_key = self._get_saved_api_key().strip()
        current_input = updated_api_key.strip()
        is_already_saved = (current_input == saved_key) if current_input else False

        # Simple validation feedback
        if updated_api_key:
            if updated_api_key.startswith('sk-') and len(updated_api_key) > 20:
                if is_already_saved:
                    # Key matches the stored default
                    st.success("✅ Valid Key (Default Saved)")
                else:
                    # Key is valid but different from stored default
                    st.info("🔑 New API Key detected")
                    if st.button("💾 Save as Default", help="Save this new key as your default", use_container_width=True):
                        try:
                            self._save_api_key_to_env(updated_api_key)
                            st.success("✨ Key saved! It will load automatically next time.")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to save: {str(e)}")
            else:
                st.error("❌ Invalid API key format")
        
        st.markdown("---")
        
        # Property information (streamlined)
        
        st.markdown("---")
        
        # Advanced AI Settings (collapsible)
        with st.expander("🤖 AI Model Settings", expanded=False):
            model_selection = st.selectbox(
                "OpenAI Model",
                ["gpt-4o", "gpt-4.5-preview", "o1-preview", "o1-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                index=0,  # Default to gpt-4o
                help="gpt-4o: Best Overall | gpt-4.5/o1: High Intelligence (Preview) | gpt-4-turbo: Fast"
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
        
        if 'processed_monthly_df' in st.session_state:
            progress_items.append("✅ Data processed")
        else:
            progress_items.append("⏳ Process data")
        
        if 'processed_analysis_output' in st.session_state:
            progress_items.append("✅ Analysis complete")
        else:
            progress_items.append("⏳ Generate analysis")
        
        # Display compact progress
        for item in progress_items:
            st.markdown(f"- {item}")

    def _get_saved_api_key(self) -> str:
        """Get the API key currently saved in the .env file."""
        try:
            from pathlib import Path
            env_path = Path.cwd() / '.env'
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith('OPENAI_API_KEY='):
                            val = line.split('=', 1)[1].strip()
                            # Remove surrounding quotes if present
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                val = val[1:-1]
                            return val.strip()
        except Exception:
            pass
        return ""

    def _save_api_key_to_env(self, api_key: str):
        """Save the API key to the .env file permanently."""
        from pathlib import Path
        env_path = Path.cwd() / '.env'
        
        # Read existing file if it exists
        lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        # Update or add the key
        key_found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith('OPENAI_API_KEY='):
                new_lines.append(f'OPENAI_API_KEY={api_key}\n')
                key_found = True
            else:
                new_lines.append(line)
        
        if not key_found:
            new_lines.append(f'OPENAI_API_KEY={api_key}\n')
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
        # Update session state and environment immediately
        st.session_state['api_key'] = api_key
        st.session_state['api_key_input'] = api_key
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Force reload of environment if using dotenv elsewhere
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
        except Exception:
            pass
