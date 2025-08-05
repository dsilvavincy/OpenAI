"""
Debug utility to check API key loading
"""
import os
import streamlit as st

def debug_api_key():
    """Debug function to check API key loading sources."""
    
    # Check environment variable
    env_key = os.getenv("OPENAI_API_KEY", "")
    
    # Check session state
    session_key = st.session_state.get('api_key', '')
    
    print(f"[DEBUG] Environment API key: {'*' * min(len(env_key), 10) if env_key else 'None'}")
    print(f"[DEBUG] Session state API key: {'*' * min(len(session_key), 10) if session_key else 'None'}")
    
    with st.expander("🔍 Debug API Key Loading"):
        st.write("**Environment Variable:**")
        if env_key:
            st.success(f"✅ Found: sk-...{env_key[-8:] if len(env_key) > 8 else env_key}")
        else:
            st.error("❌ Not found in environment")
        
        st.write("**Session State:**")
        if session_key:
            st.success(f"✅ Found: sk-...{session_key[-8:] if len(session_key) > 8 else session_key}")
        else:
            st.error("❌ Not found in session state")
        
        st.write("**Final API Key (Combined):**")
        final_key = session_key or env_key
        if final_key:
            st.success(f"✅ Using: sk-...{final_key[-8:] if len(final_key) > 8 else final_key}")
        else:
            st.error("❌ No API key available")

if __name__ == "__main__":
    debug_api_key()
