"""
Production Results - Clean analysis display with side-by-side options

Handles analysis generation and display with options for:
- Structured view only (default)
- Side-by-side: Structured + Raw Response
- Clean export options
"""
import streamlit as st
import pandas as pd
import json
import re
import logging
import datetime
from typing import Optional, Dict, Any
from src.ui.ai_analysis import get_existing_analysis_results, run_ai_analysis_responses
from src.utils.format_detection import get_stored_format
from src.core.local_analysis import PropertyAnalyzer

logger = logging.getLogger(__name__)


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
            try:
                # 1. Compute Analysis Data (Structure)
                analyzer = PropertyAnalyzer(monthly_df, ytd_df)
                preview_data = analyzer.analyze_property(selected_property)
                
                # Store in session state for reuse
                st.session_state['last_structured_data'] = preview_data

                # 2. Display Visual Reports (Top Level)
                st.markdown("### 📋 Automated Data Report")
                
                # Get Report Period from Analysis Result
                report_period_str = preview_data.get("report_period", "Unknown Period")
                
                st.markdown(f"**Report Period:** {report_period_str}")
                ProductionResults._render_visual_tables(preview_data, selected_property)

                # 3. Collaborative Debug View (Hidden for Production)
                # with st.expander(f"🛠️ DEBUG: Analysis Data Trace - {selected_property}", expanded=False):
                #     st.write("### Analysis Debug Info")
                #     st.json(preview_data.get('debug', {}))
                #     st.write("### Calculated KPI Data")
                #     st.json(preview_data.get('kpi', {}))
                #     st.write("### MoM Data Trace")
                #     st.json(preview_data.get('mom_changes', {}))
                #     
                # with st.expander("📦 LLM Payload Preview (Structured JSON)", expanded=False):
                #     # Show ONLY what is sent to LLM for variances
                #     minimal_payload = {
                #         "property_name": preview_data.get("property_name"),
                #         "report_period": preview_data.get("report_period"),
                #         "budget_variances": preview_data.get("budget_variances", {}),
                #         "trailing_anomalies": preview_data.get("trailing_anomalies", {})
                #     }
                #     st.json(minimal_payload)

            except Exception as e:
                st.error(f"❌ Error generating report preview: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        # Add Upload to LLM button ONLY if no analysis exists
        # Check if we already have results in session state to avoid double buttons
        existing_results = get_existing_analysis_results()
        if not existing_results:
            show_analyze = st.button("🚀 Run AI Analysis on this Data", type="primary", use_container_width=True)
            if show_analyze:
                ProductionResults._render_ai_analysis(monthly_df, ytd_df, config, selected_property)
        else:
            # If results exist, just render them directly
            ProductionResults._render_ai_analysis(monthly_df, ytd_df, config, selected_property)

    @staticmethod
    def _render_visual_tables(analysis_result: Dict[str, Any], selected_property: str):
        """Unified helper to render the HTML tables (KPI, Financial, Portfolio)."""
        from src.core.report_generator import ReportGenerator
        import pandas as pd
        
        report_gen = ReportGenerator()
        
        # Helper to safely persist DFs for export
        export_cache = {}

        # 0. Portfolio Snapshot (from Internal Sheet)
        st.markdown("#### Portfolio Snapshot")
        snapshot_html = ""
        
        # Try to get the raw T12 Summary Data for Export
        if "processed_data" in st.session_state:
             proc_data = st.session_state["processed_data"]
             
             # 1. Try to get Pre-Extracted DF (Inserted by production_upload.py)
             if selected_property in proc_data and "portfolio_snapshot_df" in proc_data[selected_property]:
                 export_cache['portfolio_snapshot'] = proc_data[selected_property]["portfolio_snapshot_df"]
             
             # 2. Get HTML (existing logic)
             if selected_property in proc_data:
                snapshot_html = proc_data[selected_property].get("portfolio_snapshot_html", "")
                export_cache['portfolio_html'] = snapshot_html

        if snapshot_html:
            st.markdown(snapshot_html, unsafe_allow_html=True)
        else:
            st.caption("ℹ️ Portfolio snapshot not available for this workbook.")

        # 1. KPI Snapshot Table (Merged Monthly + YTD)
        st.markdown("#### KPI Snapshot")
        # Extract MoM changes from result
        mom_changes = analysis_result.get('mom_changes', {})
        monthly_kpi = analysis_result.get('kpi', {})
        ytd_kpi = analysis_result.get('ytd_kpi', {})
        
        # Generate Export DF (Replicating ReportGenerator.generate_combined_kpi_table logic)
        # We must build the exact same rows
        kpi_rows = []
        
        # A. Key Metrics List (from ReportGenerator)
        metrics = [
            ("Total Income", "net_eff_gross_income"),
            ("Total Expenses", "total_expense"),
            ("Net Operating Income", "ebitda_noi")
        ]
        
        for label, key in metrics:
            val_mo = monthly_kpi.get(key, 0)
            val_ytd = ytd_kpi.get(key, 0)
            kpi_rows.append({
                "Metric": label,
                "Current Month": f"${val_mo:,.0f}",
                "YTD (Cumulative)": f"${val_ytd:,.0f}"
            })
            
        # B. Expense Ratio
        inc_mo = monthly_kpi.get("net_eff_gross_income", 0)
        exp_mo = monthly_kpi.get("total_expense", 0)
        ratio_mo = (exp_mo / inc_mo) if inc_mo and inc_mo != 0 else 0
        
        inc_ytd = ytd_kpi.get("net_eff_gross_income", 0)
        exp_ytd = ytd_kpi.get("total_expense", 0)
        ratio_ytd = (exp_ytd / inc_ytd) if inc_ytd and inc_ytd != 0 else 0
        
        kpi_rows.append({
            "Metric": "Expense Ratio",
            "Current Month": f"{ratio_mo:.1%}",
            "YTD (Cumulative)": f"{ratio_ytd:.1%}"
        })
        
        # C. MoM Changes
        # Income
        inc_data = mom_changes.get('net_eff_gross_income', {})
        inc_pct = inc_data.get('change_pct', 0)
        inc_abs = inc_data.get('change_abs', 0)
        kpi_rows.append({
            "Metric": "MoM Income Change",
            "Current Month": f"{inc_pct:+.1f}% (${inc_abs:,.0f})",
            "YTD (Cumulative)": "-"
        })
        
        # Expense
        exp_data = mom_changes.get('total_expense', {})
        exp_pct = exp_data.get('change_pct', 0)
        exp_abs = exp_data.get('change_abs', 0)
        kpi_rows.append({
            "Metric": "MoM Expense Change",
            "Current Month": f"{exp_pct:+.1f}% (${exp_abs:,.0f})",
            "YTD (Cumulative)": "-"
        })
        
        export_cache['kpi_data'] = pd.DataFrame(kpi_rows)

        kpi_html = report_gen.generate_combined_kpi_table(
            monthly_kpi=monthly_kpi,
            ytd_kpi=ytd_kpi,
            mom_changes=mom_changes
        )
        st.markdown(kpi_html, unsafe_allow_html=True)
        
        # 2. Financial Data Section
        st.markdown("#### Monthly Financial Data")
        if 'monthly_data' in analysis_result:
            m_df = pd.DataFrame(analysis_result['monthly_data'])
            if not m_df.empty:
                if 'Metric' in m_df.columns and 'Period' in m_df.columns and 'Value' in m_df.columns:
                    # Use pivot_table with aggfunc='sum' to be resilient to any remaining duplicates
                    pivot_df = m_df.pivot_table(index='Metric', columns='Period', values='Value', aggfunc='sum')
                    pivot_df = pivot_df.sort_index(axis=1) # Chronological sort
                    
                    # Generate display HTML (will filter internally)
                    fin_html = report_gen.generate_financial_table(pivot_df)
                    st.markdown(fin_html, unsafe_allow_html=True)
                    
                    # Generate Export DF (Apply SAME filter as ReportGenerator)
                    ALLOWED_METRICS = [
                        "Debt Yield", "1 Month DSCR", "12 Month DSCR", 
                        "Physical Occupancy", "Economic Occupancy", 
                        "Break Even Occ. - NOI", "Break Even Occ. - Cash Flow",
                        "Asking Rent (Stats)", 
                        "Inplace Eff. Rent", "Occupied Inplace Eff. Rent", "Concession %",
                        "Delinquency %", "Trailing 12 month NOI"
                    ]
                    
                    filtered_rows = []
                    # Create a clean DF with readable headers
                    export_fin = pivot_df.copy()
                    # Format Headers
                    export_fin.columns = [pd.to_datetime(c).strftime('%b-%y') if isinstance(c, (pd.Timestamp, datetime.date, datetime.datetime)) or (isinstance(c, str) and c[0].isdigit()) else str(c) for c in export_fin.columns]
                    
                    for metric in ALLOWED_METRICS:
                        # Find matching index using CONTAINS (ignoring case) to match UI Generator logic
                         matches = [i for i in export_fin.index if metric.lower() in str(i).strip().lower()]
                         if matches:
                             # Use the first match (most specific usually found first if sorted, but here we just take one)
                             # ReportGenerator iterates ALLOWED_METRICS and finds matches.
                             
                             # If multiple matches, we might want to disambiguate, but taking first is consistent with typical single-row logic
                             match_idx = matches[0]
                             
                             row = export_fin.loc[[match_idx]].copy()
                             # Format values
                             for c in row.columns:
                                 val = row.at[match_idx, c]
                                 if pd.isna(val) or val == "":
                                     row.at[match_idx, c] = "-"
                                 else:
                                     # Percentage logic
                                     is_pct = "Occupancy" in metric or "Retention" in metric or "Renewal" in metric or "Yield" in metric or "Break Even" in metric
                                     is_dscr = "DSCR" in metric
                                     if is_pct and abs(val) < 5: # Heuristic for pct
                                         row.at[match_idx, c] = f"{val:.1%}" if val != 0 else "0.0%"
                                     elif is_dscr:
                                         row.at[match_idx, c] = f"{val:.2f}"
                                     else:
                                         row.at[match_idx, c] = f"{val:,.0f}"
                             
                             # Reset index to make Metric a column
                             row = row.reset_index().rename(columns={'Metric': 'Metric', 'index': 'Metric'})
                             
                             # Force metric name to be the nice one (Clean Suffixes)
                             clean_metric = metric.replace("(Stats)", "").strip()
                             row['Metric'] = clean_metric
                             filtered_rows.append(row)
                    
                    if filtered_rows:
                        export_cache['financial_data'] = pd.concat(filtered_rows, ignore_index=True)
                    else:
                         # Fallback if no matches - use head but clean names
                         fallback = export_fin.head(25).reset_index().rename(columns={'index': 'Metric'})
                         fallback['Metric'] = fallback['Metric'].astype(str).str.replace(r"\s*\(Stats\)", "", regex=True)
                         export_cache['financial_data'] = fallback

                else:
                    st.warning("Financial data structure invalid for table generation.")
        
        # Save to session state for the downloader to pick up
        st.session_state['export_payload_cache'] = export_cache

    @staticmethod
    def _render_ai_analysis(monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, config: Dict[str, Any], selected_property: Optional[str] = None):
        """Render AI analysis with side-by-side option."""
        # ... existing implementation ...
        # (Assuming the rest of the method is unchanged except for calling the helper)
        # Check for existing analysis results first
        existing_output = get_existing_analysis_results()

        if existing_output:
            # Display existing results
            st.markdown("## 📊 Full AI Analysis Report")
            ProductionResults._display_analysis_with_options(existing_output, config, selected_property)
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
            st.markdown("## 📊 Full AI Analysis Report")
            # Persist for subsequent reruns so the UI shows existing results
            st.session_state['processed_analysis_output'] = processed_output
            st.session_state['last_analyzed_property'] = selected_property
            ProductionResults._display_analysis_with_options(processed_output, config, selected_property)
    
    @staticmethod
    def _display_analysis_with_options(output: Dict[str, Any], config: Dict[str, Any], selected_property: str):
        """Display raw response. Also show debug data if available."""
        # Main report content
        ProductionResults._display_raw_response_as_main_report(output, selected_property)
        
        # Add a preview view at the bottom for verification
        if 'last_structured_data' in st.session_state:
            with st.expander("📦 LLM Payload Preview (Structured JSON)", expanded=False):
                st.markdown("### 📊 Local Python Analysis Verification")
                st.info("This is the exact minimized data sent to the AI for variance analysis.")
                raw_data = st.session_state['last_structured_data']
                minimal_payload = {
                    "property_name": raw_data.get("property_name"),
                    "report_period": raw_data.get("report_period"),
                    "budget_variances": raw_data.get("budget_variances", {}),
                    "trailing_anomalies": raw_data.get("trailing_anomalies", {})
                }
                st.json(minimal_payload)
    
    @staticmethod
    def _display_raw_response_as_main_report(output: Dict[str, Any], selected_property: str):
        """Display the raw AI response as the main report content, using enhanced HTML formatting."""
        if "raw_response" in output:
            raw_response = output["raw_response"]
            
            # Use raw markdown to support tables and standard formatting
            final_response = raw_response
            
            # --- RENDER AI NARRATIVE SECTION ---
            st.markdown("### 🤖 AI Analysis & Recommendations")
            
            # Attempt to parse as JSON for Python-side rendering
            try:
                # 1. Improved JSON extraction: find the first { and last }
                json_str = raw_response.strip()
                
                # Check for code blocks first
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
                else:
                    # Look for the first { and the last } in the raw response
                    start_idx = json_str.find('{')
                    end_idx = json_str.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_str = json_str[start_idx:end_idx+1]
                
                # Handle potential trailing commas or other LLM artifacts if needed
                # (Simple json.loads is usually fine if we cut correctly)
                ai_data = json.loads(json_str)
                
                from src.core.report_generator import ReportGenerator
                report_gen = ReportGenerator()
                narrative_html = report_gen.generate_ai_variance_tables(ai_data)
                st.markdown(narrative_html, unsafe_allow_html=True)
                
            except Exception as e:
                # Fallback to raw markdown if JSON fails
                st.markdown(final_response, unsafe_allow_html=True)
                # Log the error for internal debugging
                logger.error(f"JSON Parse Error in AI narrative: {str(e)}")
            
            st.caption(f"Response length: {len(raw_response):,} characters")
            
            # Download options
            st.markdown("### 📥 Download Report")
            col1, col2, col3 = st.columns(3)
            
            # Prepare Visual Data for Export
            visual_data = {}
            if "last_structured_data" in st.session_state:
                struct_data = st.session_state["last_structured_data"]
                
                # Reconstruct KPI Table Data if possible
                # (Ideally we'd have the DFs ready, but we can access them from the struct)
            # Retrieve from cache populated during render
            visual_data = st.session_state.get('export_payload_cache', {})
            
            # Fallback (shouldn't happen if render was called)
            if not visual_data and "last_structured_data" in st.session_state:
                 # Last resort reconstruction if cache missed
                 pass 

            # Merge AI data into output for export if it's not already there (it should be)
            # The 'output' dict here usually contains just the raw response wrapper if it came from the response API.
            # We need to ensure 'budget_variances' and 'trailing_anomalies' are in the 'processed_output' passed to the generator.
            
            # If we parsed ai_data successfully above, add it to export_payload
            export_payload = output.copy()
            if 'ai_data' in locals() and ai_data:
                export_payload.update(ai_data)
            elif "structured_data" in output:
                # Fallback if parsing failed but structured data was passed through
                export_payload.update(output["structured_data"])

            # 3. Add Report Period (from structured data)
            report_period = output.get("report_period", "N/A")
            
            if "property_info" not in export_payload:
                export_payload["property_info"] = {}
            export_payload["property_info"]["report_period"] = report_period

            from src.ui.reports import (
                generate_pdf_report, 
                generate_word_report, 
                generate_text_report,
                generate_html_download
            )
            
            # Generate and offer downloads
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pdf_bytes = generate_pdf_report(processed_output=export_payload, visual_data=visual_data)
                st.download_button(
                    label="📄 PDF (App Styling)",
                    data=pdf_bytes,
                    file_name=f"{selected_property}_T12_Analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            with col2:
                word_bytes = generate_word_report(processed_output=export_payload, visual_data=visual_data)
                st.download_button(
                    label="📝 Word (Editable)",
                    data=word_bytes,
                    file_name=f"{selected_property}_T12_Analysis.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
            with col3:
                txt_bytes = generate_text_report(processed_output=export_payload)
                st.download_button(
                    label="📋 Text Summary",
                    data=txt_bytes,
                    file_name=f"{selected_property}_T12_Analysis.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col4:
                html_bytes = generate_html_download(processed_output=export_payload, visual_data=visual_data)
                st.download_button(
                    label="🌐 Web Report (Print)",
                    data=html_bytes,
                    file_name=f"{selected_property}_T12_Analysis.html",
                    mime="text/html",
                    help="For best 'Print to PDF' results.",
                    use_container_width=True
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
