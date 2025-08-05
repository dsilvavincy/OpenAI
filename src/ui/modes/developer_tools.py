"""
Developer Tools Panel - Advanced debugging and development tools
"""
import streamlit as st
from typing import Dict, Any

class DeveloperToolsPanel:
    """Developer tools panel with advanced debugging features."""
    
    def render(self, config: Dict[str, Any]):
        """Render developer tools panel."""
        st.markdown("### 🛠️ Developer Tools")
        
        # Prompt testing tools
        if 'processed_df' in st.session_state:
            df = st.session_state['processed_df']
            
            try:
                from src.core.kpi_registry import kpi_registry
                # Fix format detection for prompt testing too
                force_format = config.get('force_format')
                if force_format and force_format != "None":
                    format_name = force_format
                else:
                    format_name = "T12_Monthly_Financial"  # Use default when "None" selected
                    
                kpi_summary = kpi_registry.calculate_kpis(df, format_name)
                
                st.markdown("#### 🧪 Prompt Testing & AI Debugging")
                st.info("💡 **View OpenAI Prompts:** See the exact prompts sent to OpenAI for both Standard and Enhanced Analysis modes.")
                
                from src.ui.data_analysis import display_prompt_testing_section
                display_prompt_testing_section(kpi_summary, df)
                
            except Exception as e:
                st.error(f"Error loading prompt testing: {str(e)}")
        else:
            # Show message when no data is uploaded
            st.markdown("#### 🧪 Prompt Testing & AI Debugging")
            st.info("💡 **Upload a T12 file** to see the exact prompts sent to OpenAI for analysis.")
        
        # Format registry info
        st.markdown("#### 📋 Format Registry")
        self._render_format_registry()
        
        # System tools
        st.markdown("#### ⚙️ System Tools")
        self._render_system_tools()
        
        # Performance monitoring
        if config.get('show_performance', False):
            st.markdown("#### 📊 Performance Monitor")
            self._render_performance_monitor()
    
    def _render_format_registry(self):
        """Render format registry information."""
        with st.expander("Available Formats"):
            try:
                from src.core.format_registry import format_registry
                formats = format_registry.get_registered_formats()
                for fmt in formats:
                    st.text(f"• {fmt['name']}: {fmt['description']}")
            except Exception as e:
                st.error(f"Error loading format registry: {str(e)}")
    
    def _render_system_tools(self):
        """Render system tools."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Clear Cache"):
                st.cache_data.clear()
                st.success("Cache cleared!")
        
        with col2:
            if st.button("🧹 Reset Session"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("Session reset!")
                st.rerun()
    
    def _render_performance_monitor(self):
        """Render performance monitoring tools."""
        # Session state size
        session_size = len(st.session_state.keys())
        st.metric("Session State Keys", session_size)
        
        # Memory usage (if available)
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            st.metric("Memory Usage", f"{memory_mb:.1f} MB")
        except ImportError:
            st.caption("Install psutil for memory monitoring")
        
        # Show session state contents
        with st.expander("Session State Inspector"):
            for key, value in st.session_state.items():
                if key.startswith(('processed_', 'uploaded_')):
                    st.text(f"{key}: {type(value).__name__}")
                else:
                    st.text(f"{key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
