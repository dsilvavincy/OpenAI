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
        """Render enhanced results section with organized collapsible developer insights."""
        from src.ui.shared_file_manager import SharedFileManager
        
        st.markdown("### 📈 Analysis & Results")
        
        # Sync any legacy data first
        SharedFileManager.sync_legacy_session_state()
        
        df = SharedFileManager.get_processed_df()
        if df is None:
            st.info("👆 Upload a T12 file to begin analysis")
            return
        
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
            
            # Show format info if debug enabled
            if config.get('debug_mode', False):
                st.caption(f"🔍 Using format: {format_name}")
            
            # KPI Generation with performance tracking
            start_time = time.time()
            with st.spinner("📊 Generating KPI analysis..."):
                kpi_summary = kpi_registry.calculate_kpis(df, format_name)
            kpi_time = time.time() - start_time
            
            # Performance Metrics (collapsible)
            if config.get('show_performance', False):
                with st.expander("⚡ Performance Metrics", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("KPI Generation Time", f"{kpi_time:.2f}s")
                    with col2:
                        st.metric("Data Points", df.shape[0])
                    with col3:
                        st.metric("Summary Length", f"{len(kpi_summary)} chars")
            
            # Main analysis section
            self._render_enhanced_ai_analysis(df, kpi_summary, config)
            
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
            if config.get('debug_mode', False):
                st.exception(e)
            else:
                st.info("💡 Enable Debug Mode in sidebar for detailed error information")
    
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
        """Render AI analysis with developer enhancements and collapsible debug options."""
        from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options
        
        # Debug Information (collapsible)
        if config.get('debug_mode', False) or config.get('show_api_logs', False):
            with st.expander("🐛 AI Analysis Debug Info", expanded=False):
                st.write("**Request Configuration:**")
                debug_info = {
                    "API Key": "sk-..." + config['api_key'][-8:] if config.get('api_key') else "Not set",
                    "Model": config.get('model_selection', 'gpt-4-turbo'),
                    "Temperature": config.get('temperature', 0.7),
                    "Max Tokens": config.get('max_tokens', 2000),
                    "Bypass Validation": config.get('bypass_validation', False)
                }
                st.json(debug_info)
                
                if config.get('show_api_logs', False):
                    st.write("**API Call Logs will appear here during analysis**")
        
        # KPI Debug Information (collapsible, only in debug mode)
        if config.get('debug_mode', False):
            # Get format name for debug
            force_format = config.get('force_format')
            if force_format and force_format != "None":
                debug_format_name = force_format
            else:
                debug_format_name = "T12_Monthly_Financial"
                
            with st.expander("📊 KPI Analytics & Debug", expanded=False):
                tabs = st.tabs(["📊 Analytics", "🔧 Debug Info"])
                
                with tabs[0]:
                    self._render_kpi_analytics(df, debug_format_name)
                
                with tabs[1]:
                    self._render_kpi_debug(df, debug_format_name, kpi_summary)
        
        # AI Analysis with enhanced developer options
        from src.ui.ai_analysis import display_ai_analysis_section, display_analysis_results, display_export_options, get_existing_analysis_results
        
        # Check for existing results first
        existing_output = get_existing_analysis_results()
        
        if existing_output:
            # Display existing results immediately
            st.markdown("### 📊 Analysis Report")
            display_analysis_results(existing_output, display_mode="both")
            
            # Developer Analysis Insights (collapsible)
            if config.get('debug_mode', False):
                with st.expander("🔬 Analysis Quality Metrics", expanded=False):
                    quality_metrics = existing_output.get('quality_metrics', {})
                    if quality_metrics:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Score", f"{quality_metrics.get('overall_score', 0)}/100")
                        with col2:
                            st.metric("Quality Level", quality_metrics.get('quality_level', 'Unknown'))
                        with col3:
                            st.metric("Response Length", len(str(existing_output.get('analysis', ''))))
            
            # Advanced Export Options (collapsible)
            with st.expander("💾 Export Options & Templates", expanded=False):
                display_export_options(existing_output, config['property_name'])
                
                # Developer export options
                if config.get('save_responses', False):
                    st.markdown("**Developer Options:**")
                    if st.button("💾 Save Raw Analysis Data"):
                        # Save processed_output to session state or file
                        st.session_state['last_analysis_data'] = existing_output
                        st.success("✅ Analysis data saved to session state")
                
                if config.get('enable_ab_testing', False):
                    st.markdown("**A/B Testing:**")
                    if st.button("🔄 Generate Alternative Analysis"):
                        st.info("🚧 A/B testing feature coming soon")
            
            # Show regenerate option
            st.markdown("---")
            if st.button("🔄 Generate New Analysis", type="secondary", use_container_width=True):
                from src.ui.ai_analysis import clear_analysis_results
                clear_analysis_results()
                st.rerun()
        else:
            # No existing results, show analysis interface
            processed_output = display_ai_analysis_section(
                df, 
                kpi_summary, 
                config['api_key'], 
                config['property_name'], 
                config['property_address']
            )
            
            if processed_output:
                # Analysis Results
                st.markdown("### 📊 Analysis Report")
                display_analysis_results(processed_output, display_mode="both")
                
                # Developer Analysis Insights (collapsible)
                if config.get('debug_mode', False):
                    with st.expander("🔬 Analysis Quality Metrics", expanded=False):
                        quality_metrics = processed_output.get('quality_metrics', {})
                        if quality_metrics:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Overall Score", f"{quality_metrics.get('overall_score', 0)}/100")
                            with col2:
                                st.metric("Quality Level", quality_metrics.get('quality_level', 'Unknown'))
                            with col3:
                                st.metric("Response Length", len(str(processed_output.get('analysis', ''))))
                
                # Advanced Export Options (collapsible)
                with st.expander("💾 Export Options & Templates", expanded=False):
                    display_export_options(processed_output, config['property_name'])
                    
                    # Developer export options
                    if config.get('save_responses', False):
                        st.markdown("**Developer Options:**")
                        if st.button("💾 Save Raw Analysis Data"):
                            # Save processed_output to session state or file
                            st.session_state['last_analysis_data'] = processed_output
                            st.success("✅ Analysis data saved to session state")
        
        # Custom Prompt Testing (if enabled)
        if config.get('enable_prompt_testing', False):
            with st.expander("🧪 Custom Prompt Testing", expanded=False):
                custom_prompt = st.text_area(
                    "Custom System Prompt",
                    height=200,
                    placeholder="Enter a custom system prompt to test..."
                )
                if st.button("🚀 Test Custom Prompt") and custom_prompt:
                    st.info("🚧 Custom prompt testing feature coming soon")
