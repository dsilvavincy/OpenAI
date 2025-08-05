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
        
        # Enhanced Analysis Validation
        st.markdown("#### 🔍 Enhanced Analysis Validation")
        self._render_enhanced_analysis_validation()
        
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
    
    def _render_enhanced_analysis_validation(self):
        """Render Enhanced Analysis validation tools."""
        st.info("🔍 **Validation Tools**: Verify that Enhanced Analysis is using raw data")
        
        # Last analysis results checker
        if 'last_enhanced_analysis_result' in st.session_state:
            result = st.session_state['last_enhanced_analysis_result']
            
            # Check for evidence of raw data usage
            validation_checks = self._validate_enhanced_analysis(result)
            
            st.write("**Validation Results:**")
            for check, status in validation_checks.items():
                icon = "✅" if status else "❌"
                st.write(f"{icon} {check}")
            
            # Overall validation score
            passed_checks = sum(validation_checks.values())
            total_checks = len(validation_checks)
            score = (passed_checks / total_checks) * 100
            
            if score >= 80:
                st.success(f"🎯 **Validation Score: {score:.0f}%** - Enhanced Analysis is working properly!")
            elif score >= 60:
                st.warning(f"⚠️ **Validation Score: {score:.0f}%** - Some issues detected")
            else:
                st.error(f"❌ **Validation Score: {score:.0f}%** - Enhanced Analysis may not be using raw data")
                
            # Raw response inspector
            with st.expander("🔍 Raw Response Inspector"):
                st.text_area("Last Enhanced Analysis Response", result, height=300)
        else:
            st.info("💡 Run an Enhanced Analysis first to see validation results")
            
        # Manual validation tools
        with st.expander("🧪 Manual Validation Tools"):
            st.markdown("**Check for these indicators in Enhanced Analysis output:**")
            st.markdown("- 📊 Detailed trend tables with month-over-month percentages")
            st.markdown("- 🔍 Validation of specific numbers from your KPI summary")
            st.markdown("- 📈 Strategic insights based on raw data patterns")
            st.markdown("- 🎯 Actionable recommendations for management")
            st.markdown("- 💡 Analysis that goes beyond your local summary")
    
    def _validate_enhanced_analysis(self, analysis_result: str) -> dict:
        """
        Validate that Enhanced Analysis actually used raw data.
        
        Returns:
            dict: Validation check results
        """
        if not analysis_result:
            return {}
            
        result_lower = analysis_result.lower()
        
        validation_checks = {
            "Shows detailed trend analysis": any(
                indicator in result_lower for indicator in 
                ["trend", "month-over-month", "percentage", "change", "%", "increase", "decrease", "table"]
            ),
            "Uses raw data analysis": any(
                indicator in result_lower for indicator in 
                ["csv", "raw data", "examining", "loading", "structure", "data analysis"]
            ),
            "Validates specific numbers": any(
                indicator in result_lower for indicator in 
                ["validation", "calculated", "verified", "matches", "differs", "aligning", "corroborating"]
            ),
            "Contains strategic insights": any(
                indicator in result_lower for indicator in 
                ["strategic questions", "recommendations", "actionable", "management", "investment"]
            ),
            "Contains data analysis insights": any(
                indicator in result_lower for indicator in 
                ["analysis", "pattern", "concerning", "improvement", "recommendation"]
            ),
            "Shows raw data examination": any(
                indicator in result_lower for indicator in 
                ["csv", "data", "examining", "loading", "structure"]
            )
        }
        
        return validation_checks
