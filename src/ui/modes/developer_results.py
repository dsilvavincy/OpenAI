"""
Developer Results Section - Enhanced analysis results with debugging
"""
import streamlit as st
import pandas as pd
import time
from typing import Optional, Dict, Any

class DeveloperResultsSection:
    """Enhanced results section with developer insights."""
    
    def render(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """Render enhanced results section with developer insights."""
        st.markdown("### 📈 Analysis Results")
        
        if 'processed_df' not in st.session_state:
            st.info("👆 Upload a T12 file to begin analysis")
            return
        
        df = st.session_state['processed_df']
        api_key = config.get('api_key', '')
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
            return
        
        try:
            # Use new scalable system with performance monitoring
            from src.core.kpi_registry import kpi_registry
            
            # Fix format detection: handle None properly
            force_format = config.get('force_format')
            if force_format and force_format != "None":
                format_name = force_format
            else:
                format_name = "T12_Monthly_Financial"  # Use default when "None" selected
            
            st.caption(f"🔍 Using format: {format_name}")
            
            # KPI Generation with timing
            start_time = time.time()
            with st.spinner("📊 Generating KPI analysis..."):
                kpi_summary = kpi_registry.calculate_kpis(df, format_name)
            kpi_time = time.time() - start_time
            
            # Show performance metrics if enabled
            if config.get('show_performance', False):
                st.metric("KPI Generation Time", f"{kpi_time:.2f}s")
            
            # Enhanced KPI display in a collapsed expander
            with st.expander("📋 Financial Summary", expanded=False):
                tabs = st.tabs(["📄 Summary", "📊 Analytics", "🔧 Debug"])
                with tabs[0]:
                    st.text_area("KPI Summary", kpi_summary, height=400, label_visibility="collapsed")
                with tabs[1]:
                    self._render_kpi_analytics(df, format_name)
                with tabs[2]:
                    if config.get('debug_mode', False):
                        self._render_kpi_debug(df, format_name, kpi_summary)

            # Add vertical space to ensure separation
            st.markdown("<div style='margin-top: 2em'></div>", unsafe_allow_html=True)
            # AI-Powered Analysis section below Financial Summary (no redundant header)
            self._render_enhanced_ai_analysis(df, kpi_summary, config)
            
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
            if config.get('debug_mode', False):
                st.exception(e)
    
    def _render_kpi_analytics(self, df: pd.DataFrame, format_name: str):
        """Render KPI analytics for developer mode."""
        from src.core.kpi_registry import kpi_registry
        
        # Get calculator info
        calc_info = kpi_registry.get_calculator_info(format_name)
        if calc_info:
            st.json(calc_info)
        
        # Key metrics analysis
        key_metrics = kpi_registry.get_key_metrics(format_name)
        if key_metrics:
            st.write("**Key Metrics:**")
            for metric in key_metrics:
                st.text(f"• {metric}")
    
    def _render_kpi_debug(self, df: pd.DataFrame, format_name: str, kpi_summary: str):
        """Render KPI debug information."""
        from src.core.kpi_registry import kpi_registry
        
        st.write("**Debug Information:**")
        st.text(f"Format: {format_name}")
        st.text(f"DataFrame shape: {df.shape}")
        st.text(f"Summary length: {len(kpi_summary)} characters")
        
        # Calculation issues
        issues = kpi_registry.get_calculation_issues(format_name)
        if issues:
            st.write("**Calculation Issues:**")
            for issue in issues:
                st.text(f"• {issue}")
        else:
            st.success("✅ No calculation issues")
    
    def _render_enhanced_ai_analysis(self, df: pd.DataFrame, kpi_summary: str, config: Dict[str, Any]):
        """Render AI analysis with developer enhancements."""
        from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options
        
        # Enhanced AI analysis with custom parameters (removed redundant header)
        processed_output = display_ai_analysis_section(
            df, 
            kpi_summary, 
            config['api_key'], 
            config['property_name'], 
            config['property_address']
        )
        if processed_output:
            # Enhanced results display
            st.markdown("#### 📄 Analysis Report")
            display_analysis_results(processed_output)
            # Developer export options
            st.markdown("#### 💾 Export Options")
            display_export_options(processed_output, config['property_name'])
