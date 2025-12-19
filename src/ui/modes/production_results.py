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
from src.ui.ai_analysis import get_existing_analysis_results, run_ai_analysis_responses
from src.utils.format_detection import get_stored_format
from src.core.local_analysis import PropertyAnalyzer


class ProductionResults:
    """Production mode results display with side-by-side capabilities."""

    @staticmethod
    def format_response_for_streamlit(raw_response: str) -> str:
        """
        Enhanced formatter for Streamlit HTML rendering with proper handling of:
        - Currencies ($, £, €, etc.)
        - Percentages (%)
        - Mathematical expressions (÷, /, vs, etc.)
        - Bold/italic markdown formatting
        - Metric lists and structured content
        """
        import re
        
        # Convert markdown formatting to HTML
        def convert_markdown_to_html(text):
            # Handle bold text (**text** or __text__)
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
            
            # Handle italic text (*text* or _text_)
            text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
            text = re.sub(r'(?<!_)_(?!_)([^_]+?)_(?!_)', r'<i>\1</i>', text)
            
            return text
        
        # Process mathematical expressions and comparisons
        def format_math_expressions(text):
            # Format division operations (÷ or /)
            text = re.sub(r'(\$?[\d,.-]+)\s*([÷/])\s*(\$?[\d,.-]+)', r'<code>\1 \2 \3</code>', text)
            
            # Format "vs" comparisons
            text = re.sub(r'(\$?[\d,.-]+%?)\s+vs\s+(\$?[\d,.-]+%?)', r'\1 <em>vs</em> \2', text)
            
            # Format parenthetical calculations
            text = re.sub(r'\(([^)]*÷[^)]*)\)', r'<i>(\1)</i>', text)
            text = re.sub(r'\(([^)]*vs[^)]*)\)', r'<i>(\1)</i>', text)
            
            return text
        
        # Process each line with better bullet point and colon handling
        def process_line(line_text):
            stripped = line_text.strip()
            
            # Handle markdown headers
            if stripped.startswith('#'):
                level = len(stripped) - len(stripped.lstrip('#'))
                header_text = stripped.lstrip('# ').strip()
                return f'<h{min(level, 6)}>{convert_markdown_to_html(header_text)}</h{min(level, 6)}>'
            
            # Handle bullet points (-, •, or leading dash)
            bullet_match = re.match(r'^[-•]\s*(.+)$', stripped)
            if bullet_match:
                content = bullet_match.group(1).strip()
                
                # Check if it's a metric line (contains colon)
                colon_match = re.match(r'^(.+?):\s*(.+)$', content)
                if colon_match:
                    metric_name = colon_match.group(1).strip()
                    metric_value = colon_match.group(2).strip()
                    
                    # Clean up metric name - handle incomplete bold formatting
                    # Remove any standalone ** at the end
                    metric_name = re.sub(r'\*\*\s*$', '', metric_name)
                    # Convert complete bold formatting
                    metric_name = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', metric_name)
                    # Handle incomplete bold at start (remove leading **)
                    metric_name = re.sub(r'^\*\*', '', metric_name)
                    
                    # Clean up metric value - remove leading **
                    metric_value = re.sub(r'^\*\*\s*', '', metric_value)
                    # Format the value
                    metric_value = convert_markdown_to_html(metric_value)
                    metric_value = format_math_expressions(metric_value)
                    
                    return f'<li><b>{metric_name}:</b> {metric_value}</li>'
                else:
                    # Regular bullet point
                    formatted_content = convert_markdown_to_html(content)
                    formatted_content = format_math_expressions(formatted_content)
                    return f'<li>{formatted_content}</li>'
            
            # Handle regular colon lines (not bullets)
            colon_match = re.match(r'^(.+?):\s*(.+)$', stripped)
            if colon_match:
                metric_name = colon_match.group(1).strip()
                metric_value = colon_match.group(2).strip()
                
                # Clean up metric name - handle incomplete bold formatting
                metric_name = re.sub(r'\*\*\s*$', '', metric_name)
                metric_name = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', metric_name)
                metric_name = re.sub(r'^\*\*', '', metric_name)
                
                # Clean up metric value - remove leading **
                metric_value = re.sub(r'^\*\*\s*', '', metric_value)
                # Format the value
                metric_value = convert_markdown_to_html(metric_value)
                metric_value = format_math_expressions(metric_value)
                
                return f'<p><b>{metric_name}:</b> {metric_value}</p>'
            
            # Regular paragraph
            if stripped:
                formatted_line = convert_markdown_to_html(stripped)
                formatted_line = format_math_expressions(formatted_line)
                return f'<p>{formatted_line}</p>'
            
            return '<br>'
        
        # Split into lines and process
        lines = raw_response.strip().splitlines()
        html_content = []
        in_list = False
        current_list_items = []
        
        for line in lines:
            processed = process_line(line)
            
            if processed == '<br>':
                # Empty line - close any open list
                if in_list and current_list_items:
                    html_content.append('<ul>' + '\n'.join(current_list_items) + '</ul>')
                    current_list_items = []
                    in_list = False
                html_content.append('<br>')
            elif processed.startswith('<li>'):
                # List item
                current_list_items.append(processed)
                in_list = True
            else:
                # Non-list item - close any open list first
                if in_list and current_list_items:
                    html_content.append('<ul>' + '\n'.join(current_list_items) + '</ul>')
                    current_list_items = []
                    in_list = False
                html_content.append(processed)
        
        # Close any remaining list
        if in_list and current_list_items:
            html_content.append('<ul>' + '\n'.join(current_list_items) + '</ul>')
        
        # Join all content
        final_html = '\n'.join(html_content)
        
        # If no formatting was applied, use a simple pre-formatted fallback
        if not final_html or final_html.strip() == '':
            return f"<div style='white-space: pre-wrap; font-family: inherit; line-height: 1.6;'>{convert_markdown_to_html(format_math_expressions(raw_response))}</div>"
        
        return final_html
    
    def render(self, uploaded_file: Optional[Any], config: Dict[str, Any]):
        """
        Render analysis results section - production focused.
        
        Args:
            uploaded_file: Uploaded file object
            config: Configuration from sidebar
        """
        # Check if we have processed data
        # Check if we have processed monthly and YTD data
        if 'processed_monthly_df' not in st.session_state or 'processed_ytd_df' not in st.session_state:
            st.info("👆 Upload a T12 file to begin analysis")
            return
        monthly_df = st.session_state['processed_monthly_df']
        ytd_df = st.session_state['processed_ytd_df']
        api_key = config.get('api_key', '')
        property_name = config.get('property_name', '')
        property_address = config.get('property_address', '')
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
            return

        # Property selector (from processed data)
        try:
            props_series = pd.concat([
                monthly_df.get('Property', pd.Series(dtype=str)),
                ytd_df.get('Property', pd.Series(dtype=str))
            ], ignore_index=True)
            properties = sorted({str(p).strip() for p in props_series.dropna().unique() if str(p).strip()})
        except Exception:
            properties = []

        selected_property_default = st.session_state.get('selected_property')
        if properties:
            if selected_property_default not in properties:
                selected_property_default = properties[0]
            selected_property = st.selectbox(
                "Select property to analyze",
                properties,
                index=properties.index(selected_property_default) if selected_property_default in properties else 0,
                help="Only rows matching this property will be analyzed (both Monthly and YTD).",
                key="selected_property_select"
            )
            st.session_state['selected_property'] = selected_property
            # If the selected property changed since the last analysis, clear cached output
            if st.session_state.get('last_analyzed_property') != selected_property:
                st.session_state.pop('processed_analysis_output', None)
        else:
            selected_property = None
            st.info("No Property column found; analysis will use all rows.")
            
        # Preview Data Package (Structured Results from Python Analysis)
        if selected_property:
            with st.expander(f"📦 Preview Data Package: {selected_property}", expanded=False):
                st.markdown("### 📊 Python Analysis Preview")
                st.info("This is the pre-computed data package that will be sent to the LLM. You can verify budget variances and 3-month averages here.")
                
                # Compute on the fly for preview
                analyzer = PropertyAnalyzer(monthly_df, ytd_df)
                preview_data = analyzer.analyze_property(selected_property)
                
                # Store in session state so run_ai_analysis_responses can reuse it if needed
                st.session_state['last_structured_data'] = preview_data
                
                st.json(preview_data)
        # Add Upload to LLM button
        show_analyze = st.button("🚀 Upload to LLM & Analyze", type="primary", use_container_width=True)
        if show_analyze:
            ProductionResults._render_ai_analysis(monthly_df, ytd_df, config, selected_property)
    
    @staticmethod
    def _render_ai_analysis(monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, config: Dict[str, Any], selected_property: Optional[str] = None):
        """Render AI analysis with side-by-side option."""
        # Check for existing analysis results first
        existing_output = get_existing_analysis_results()

        if existing_output:
            # Display existing results
            st.markdown("## 📊 Analysis Report")
            ProductionResults._display_analysis_with_options(existing_output, config)
            ProductionResults._display_regenerate_option()
            return

        # No existing results - trigger analysis immediately
        detected_format = get_stored_format()

        # Build model configuration
        model_config = {
            "model_selection": config.get('model_selection', 'gpt-4o'),
            "temperature": config.get('temperature', 0.2),
            "max_tokens": config.get('max_tokens', 2500)
        }

        # Use the NEW recommended Responses API flow
        from src.ui.ai_analysis import run_ai_analysis_responses
        property_label = selected_property or config.get('property_name', '')
        with st.spinner('Computing local metrics and generating AI report…'):
            processed_output = run_ai_analysis_responses(
                monthly_df,
                ytd_df,
                config['api_key'],
                property_label,
                config.get('property_address', ''),
                detected_format,
                model_config,
                selected_property=selected_property
            )

        if processed_output:
            st.markdown("---")
            st.markdown("## 📊 Analysis Report")
            # Persist for subsequent reruns so the UI shows existing results
            st.session_state['processed_analysis_output'] = processed_output
            st.session_state['last_analyzed_property'] = selected_property
            ProductionResults._display_analysis_with_options(processed_output, config)
    
    @staticmethod
    def _display_analysis_with_options(output: Dict[str, Any], config: Dict[str, Any]):
        """Display raw response. Also show debug data if available."""
        # Main report content
        ProductionResults._display_raw_response_as_main_report(output)
        
        # Add a debug view at the bottom for verification
        if 'last_structured_data' in st.session_state:
            with st.expander("🔍 Debug: View Full JSON sent to LLM (Python Analysis Output)", expanded=False):
                st.markdown("### 📊 Local Python Analysis Verification")
                st.info("This is the exact structured data pre-computed by Python before being sent to the AI. Use this to verify budget variances and rolling averages.")
                st.json(st.session_state['last_structured_data'])
    
    @staticmethod
    def _display_raw_response_as_main_report(output: Dict[str, Any]):
        """Display the raw AI response as the main report content, using enhanced HTML formatting."""
        if "raw_response" in output:
            raw_response = output["raw_response"]
            
            # Add a refresh formatting button
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🎨 Refresh Formatting", help="Re-apply formatting to the current response"):
                    st.rerun()
            
            formatted_html_response = ProductionResults.format_response_for_streamlit(raw_response)
            
            with st.container():
                st.markdown(formatted_html_response, unsafe_allow_html=True)
            
            st.caption(f"Response length: {len(raw_response):,} characters")
            
            # Download options
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="💾 Download Raw Response",
                    data=raw_response,
                    file_name="raw_ai_response.txt",
                    mime="text/plain",
                    help="Download the original raw AI response"
                )
            with col2:
                st.download_button(
                    label="📄 Download Formatted HTML",
                    data=formatted_html_response,
                    file_name="formatted_analysis.html",
                    mime="text/html",
                    help="Download the formatted HTML version"
                )
        else:
            st.warning("No raw response available")
    
    @staticmethod
    def _display_regenerate_option():
        """Display option to regenerate analysis."""
        st.markdown("---")
        if st.button("🔄 Generate New Analysis", type="secondary", use_container_width=True):
            from src.ui.ai_analysis import clear_analysis_results
            clear_analysis_results()
            st.rerun()
