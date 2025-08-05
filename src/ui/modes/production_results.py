"""
Production Results - Clean analysis display with side-by-side options

Handles analysis generation and display with options for:
- Structured view only (default)
- Side-by-side: Structured + Raw Response
- Clean export options
"""
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any


class ProductionResults:
    """Production mode results display with side-by-side capabilities."""
    
    def render(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """
        Render analysis results section - production focused.
        
        Args:
            uploaded_file: Uploaded file object
            config: Configuration from sidebar
        """
        # Check if we have processed data
        if 'processed_df' not in st.session_state:
            st.info("👆 Upload a T12 file to begin analysis")
            return
        
        df = st.session_state['processed_df']
        api_key = config.get('api_key', '')
        property_name = config.get('property_name', '')
        property_address = config.get('property_address', '')
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
            return
        
        try:
            # Use new scalable KPI system
            from src.core.format_registry import format_registry
            from src.core.kpi_registry import kpi_registry
            
            # Get format processor info (we already processed the file)
            format_name = "T12_Monthly_Financial"
            
            # Generate KPI Summary (only if not cached)
            if 'kpi_summary' not in st.session_state:
                with st.spinner("📊 Generating KPI analysis..."):
                    kpi_summary = kpi_registry.calculate_kpis(df, format_name)
                    st.session_state['kpi_summary'] = kpi_summary
            else:
                kpi_summary = st.session_state['kpi_summary']
            
            # Main analysis section
            self._render_ai_analysis(df, kpi_summary, config)
            
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
            st.info("💡 Please check your data and API key, then try again")
    
    def _render_ai_analysis(self, df: pd.DataFrame, kpi_summary: str, config: Dict[str, Any]):
        """Render AI analysis with side-by-side option."""
        from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options, get_existing_analysis_results
        from src.utils.format_detection import get_stored_format
        
        # Check for existing analysis results first
        existing_output = get_existing_analysis_results()
        
        if existing_output:
            # Display existing results
            st.markdown("## 📊 Analysis Report")
            self._display_analysis_with_options(existing_output, config)
            self._display_regenerate_option()
            return
        
        # No existing results - show analysis generation interface
        detected_format = get_stored_format()
        
        # Build model configuration
        model_config = {
            "model_selection": config.get('model_selection', 'gpt-4o'),
            "temperature": config.get('temperature', 0.2),
            "max_tokens": config.get('max_tokens', 2500)
        }
        
        # Generate new analysis
        processed_output = display_ai_analysis_section(
            df, 
            kpi_summary, 
            config['api_key'], 
            config['property_name'], 
            config['property_address'],
            detected_format,
            model_config
        )
        
        if processed_output:
            st.markdown("---")
            st.markdown("## 📊 Analysis Report")
            self._display_analysis_with_options(processed_output, config)
    
    def _display_analysis_with_options(self, output: Dict[str, Any], config: Dict[str, Any]):
        """Display only the raw response as the main content."""
        # Always display just the raw response
        self._display_raw_response_as_main_report(output)
    
    def _display_raw_response_as_main_report(self, output: Dict[str, Any]):
        """Display the raw AI response as the main report content."""
        if "raw_response" in output:
            raw_response = output["raw_response"]
            
            # Show a clean, full-width display of the raw response
            with st.container():
                st.markdown(raw_response)
            
            # Optional: Show character count for reference
            st.caption(f"Response length: {len(raw_response):,} characters")
            
            # Download option for raw response
            st.download_button(
                label="💾 Download Raw Response",
                data=raw_response,
                file_name="raw_ai_response.txt",
                mime="text/plain",
                help="Download the complete raw AI response"
            )
        else:
            st.warning("No raw response available")
    
    def _display_regenerate_option(self):
        """Display option to regenerate analysis."""
        st.markdown("---")
        if st.button("🔄 Generate New Analysis", type="secondary", use_container_width=True):
            from src.ui.ai_analysis import clear_analysis_results
            clear_analysis_results()
            st.rerun()
