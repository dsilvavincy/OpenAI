"""
AI analysis UI components for property analysis.
Supports both Assistants API (deprecated) and Responses API (recommended).
"""
import streamlit as st
from datetime import datetime
from src.ai.prompt import build_prompt, call_openai, validate_response
from src.ai.assistants_api import analyze_with_assistants_api  # Deprecated
from src.core.output_quality import post_process_output

# New Responses API imports
from src.core.local_analysis import PropertyAnalyzer, prepare_analysis_for_llm
from src.ai.responses_api import analyze_with_responses_api, PropertyResponsesAnalyzer

def get_existing_analysis_results():
    """Get existing analysis results from session state if available"""
    return st.session_state.get('processed_analysis_output', None)

def clear_analysis_results():
    """Clear stored analysis results (useful when data changes)"""
    if 'processed_analysis_output' in st.session_state:
        del st.session_state['processed_analysis_output']
    if 'analysis_data_hash' in st.session_state:
        del st.session_state['analysis_data_hash']

def display_ai_analysis_section(monthly_df, ytd_df, api_key, property_name, property_address, format_name="t12_monthly_financial", model_config=None, selected_property: str | None = None):
    """Display AI analysis section using Enhanced Analysis with format-specific prompts"""
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to generate analysis")
        return None
    if st.button("🎯 Generate Analysis", type="primary", use_container_width=True):
        # NEW: Use Responses API flow with local processing
        processed_output = run_ai_analysis_responses(monthly_df, ytd_df, api_key, property_name, property_address, format_name, model_config, selected_property)
        if processed_output:
            st.session_state['processed_analysis_output'] = processed_output
        return processed_output
    return None

def run_ai_analysis(monthly_df, ytd_df, api_key, property_name, property_address, format_name="t12_monthly_financial", model_config=None, selected_property: str | None = None):
    """Execute Enhanced AI analysis using Assistants API with both monthly and YTD data"""
    if model_config is None:
        model_config = {
            "model_selection": "gpt-4o",
            "temperature": 0.2,
        }
    st.info(f"🤖 **AI Model:** {model_config['model_selection']} | **Temperature:** {model_config['temperature']} | **Unlimited Tokens**")
    ai_progress = st.progress(0)
    ai_status = st.empty()
    ai_status.text("🔄 Initializing Enhanced AI Analysis...")
    ai_progress.progress(0.25)
    try:
        def update_progress(message, progress_pct):
            ai_status.text(message)
            progress_decimal = min(1.0, max(0.0, progress_pct / 100.0))
            ai_progress.progress(progress_decimal)
        streaming_container = st.empty()
        def update_streaming(response_so_far):
            with streaming_container.container():
                st.markdown("### 🔄 AI Analysis (Live Stream)")
                st.markdown(response_so_far)
                st.caption(f"📊 Characters received: {len(response_so_far)}")
        # Pass both monthly and YTD data to the analysis function
        try:
            ai_response = analyze_with_assistants_api(
                monthly_df,
                ytd_df,
                kpi_summary=None,
                api_key=api_key,
                progress_callback=update_progress,
                streaming_callback=update_streaming,
                format_name=format_name,
                model_config=model_config,
                selected_property=selected_property,
                reuse_session=True
            )
            ai_status.text("✨ Analysis complete!")
            ai_progress.progress(1.0)
            streaming_container.empty()
            st.session_state['last_enhanced_analysis_result'] = ai_response
            st.session_state['last_analysis_method'] = "Enhanced Analysis (Assistants API)"
            if ai_response.startswith("Enhanced analysis incomplete") or ai_response.startswith("Enhanced analysis ended"):
                st.warning(f"⚠️ {ai_response}")
                st.info("🔄 **AUTO-FALLBACK**: Switching to Standard Analysis...")
                ai_status.text("🔄 Falling back to standard analysis...")
                ai_progress.progress(0.6)
                # Fallback to standard analysis with simple user message; keep detailed system instructions
                from src.ai.prompt import build_prompt, call_openai
                system_prompt, _ = build_prompt("", format_name)
                fallback_property = selected_property or property_name
                user_prompt = (
                    f"Give me the report for '{fallback_property}'"
                    if fallback_property else "Give me the report"
                )
                ai_response = call_openai(system_prompt, user_prompt, api_key)
        except Exception as e:
            st.error(f"Enhanced analysis failed: {str(e)}")
            st.info("🔄 **FALLBACK**: Switching to Standard Analysis...")
            ai_status.text("🔄 Falling back to standard analysis...")
            ai_progress.progress(0.6)
            from src.ai.prompt import build_prompt, call_openai
            system_prompt, _ = build_prompt("", format_name)
            fallback_property = selected_property or property_name
            user_prompt = (
                f"Give me the report for '{fallback_property}'"
                if fallback_property else "Give me the report"
            )
            ai_response = call_openai(system_prompt, user_prompt, api_key)
        ai_status.text("✨ Processing AI response...")
        ai_progress.progress(0.75)
        if not ai_response.startswith("Error:"):
            st.success("🚀 **Enhanced Analysis Complete** - Processing results...")
            from src.ai.prompt import validate_response
            is_valid, validation_msg = validate_response(ai_response, "enhanced")
            if is_valid:
                property_info = {
                    "name": property_name or "Unknown Property",
                    "address": property_address or "No address provided"
                }
                from src.core.output_quality import post_process_output
                processed_output = post_process_output(ai_response, property_info)
                processed_output["raw_response"] = ai_response
                ai_status.text("✅ Analysis complete!")
                ai_progress.progress(1.0)
                return processed_output
            else:
                st.error(f"❌ Response validation failed: {validation_msg}")
                st.warning("🔄 Try regenerating the analysis or check your API key")
                return None
        else:
            st.error(f"❌ {ai_response}")
            if "api key" in ai_response.lower():
                st.info("💡 Please check your OpenAI API key in the sidebar")
            elif "rate limit" in ai_response.lower():
                st.info("💡 Please wait a moment and try again")
            return None
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.info("💡 **Troubleshooting tips:**")
        st.info("• Check that your data was processed correctly")
        st.info("• Verify your OpenAI API key is valid")
        st.info("• Try refreshing the page and uploading again")
        return None


def run_ai_analysis_responses(monthly_df, ytd_df, api_key, property_name, property_address, 
                               format_name="t12_monthly_financial", model_config=None, 
                               selected_property: str | None = None):
    """
    Execute AI analysis using Responses API with local Python processing.
    This is the NEW RECOMMENDED approach - replaces Assistants API.
    
    Flow:
    1. PropertyAnalyzer computes all metrics locally (Python)
    2. Structured JSON sent to Responses API
    3. LLM generates narrative report from pre-computed data
    """
    if model_config is None:
        model_config = {
            "model_selection": "gpt-4o",
            "temperature": 0.2,
        }
    
    st.info(f"🚀 **Responses API** | Model: {model_config['model_selection']} | Temp: {model_config['temperature']}")
    
    ai_progress = st.progress(0)
    ai_status = st.empty()
    
    try:
        # Step 1: Local Python Analysis
        ai_status.text("📊 Computing metrics locally...")
        ai_progress.progress(0.1)
        
        # Use the selected property or fall back to property_name
        analysis_property = selected_property or property_name
        
        if not analysis_property:
            st.error("❌ No property selected for analysis")
            return None
        
        # Create analyzer and compute all metrics
        analyzer = PropertyAnalyzer(monthly_df, ytd_df)
        structured_data = analyzer.analyze_property(analysis_property)
        
        ai_status.text(f"✅ Computed metrics for {analysis_property}")
        ai_progress.progress(0.3)
        
        # Display computed data summary - Hidden for Production
        # with st.expander("🔍 Inspect AI Data Package (Python Analysis Output)", expanded=False):
        #     st.json(structured_data)
            
        # Store for persistent inspection
        st.session_state['last_structured_data'] = structured_data
        
        # Step 2: Send to Responses API
        ai_status.text("🧠 Generating AI report...")
        ai_progress.progress(0.4)
        
        # streaming_container = st.empty()
        
        def update_streaming(response_so_far):
            # Disabled raw streaming per user request - only show progress bar
            pass
            # with streaming_container.container():
            #     st.markdown("### 🔄 AI Analysis (Live Stream)")
            #     st.markdown(response_so_far)
            #     st.caption(f"📊 Characters received: {len(response_so_far)}")
        
        def update_progress(message, progress_pct):
            ai_status.text(message)
            progress_decimal = min(1.0, max(0.0, progress_pct / 100.0))
            ai_progress.progress(progress_decimal)
        
        # Call Responses API
        ai_response = analyze_with_responses_api(
            structured_data=structured_data,
            api_key=api_key,
            model=model_config['model_selection'],
            temperature=model_config['temperature'],
            stream_callback=update_streaming,
            progress_callback=update_progress,
        )
        
        ai_status.text("✨ Analysis complete!")
        ai_progress.progress(1.0)
        # streaming_container.empty()
        
        # Store in session state
        st.session_state['last_enhanced_analysis_result'] = ai_response
        st.session_state['last_analysis_method'] = "Responses API (Recommended)"
        
        # Process the response
        if ai_response and not ai_response.startswith("Error:"):
            st.success("🚀 **Responses API Analysis Complete**")
            
            # Create property info for post-processing
            property_info = {
                "name": analysis_property or "Unknown Property",
                "address": property_address or "No address provided"
            }
            
            # Post-process the output
            processed_output = post_process_output(ai_response, property_info)
            processed_output["raw_response"] = ai_response
            processed_output["structured_data"] = structured_data  # Include computed data
            processed_output["api_method"] = "responses_api"
            
            return processed_output
        else:
            st.error(f"❌ {ai_response}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error during Responses API analysis: {str(e)}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")
        return None

def display_analysis_results(processed_output, display_mode="structured"):
    """
    Display formatted AI analysis results without duplicates
    
    Args:
        processed_output: The processed analysis output
        display_mode: "structured" (collapsible sections), "formatted" (HTML display), or "both"
    """
    if not processed_output:
        return

    # Show quality metrics first
    quality = processed_output["quality_metrics"]
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.metric("Quality Score", f"{quality['overall_score']}/100")
    with col_q2:
        st.metric("Quality Level", quality['quality_level'])
    with col_q3:
        st.metric("Questions Found", len(processed_output["analysis"]["strategic_questions"]))
    
    st.markdown("---")
    
    # Display based on mode to avoid duplicates
    if display_mode == "formatted":
        # Show only the formatted HTML/Markdown content (no duplicates)
        st.markdown("### 📊 Analysis Results")
        st.markdown(processed_output["display_text"])
        
    elif display_mode == "structured":
        # Show only structured sections in collapsible expanders (no HTML version)
        analysis = processed_output["analysis"]
        
        # Strategic Questions Section
        with st.expander("🎯 Strategic Management Questions", expanded=True):
            for i, question in enumerate(analysis["strategic_questions"], 1):
                st.markdown(f"**{i}.** {question}")
        
        # Recommendations Section
        with st.expander("💡 Actionable Recommendations", expanded=True):
            for i, rec in enumerate(analysis["recommendations"], 1):
                st.markdown(f"**{i}.** {rec}")
        
        # Concerning Trends Section
        with st.expander("⚠️ Concerning Trends", expanded=True):
            for i, concern in enumerate(analysis["concerning_trends"], 1):
                st.markdown(f"**{i}.** {concern}")
                
    elif display_mode == "both":
        # Show both views in separate tabs (developer mode)
        tab1, tab2, tab3 = st.tabs(["📋 Structured View", "📄 Report View", "🔧 Raw Response"])
        
        with tab1:
            analysis = processed_output["analysis"]
            
            # Strategic Questions Section
            with st.expander("🎯 Strategic Management Questions", expanded=True):
                for i, question in enumerate(analysis["strategic_questions"], 1):
                    st.markdown(f"**{i}.** {question}")
            
            # Recommendations Section  
            with st.expander("💡 Actionable Recommendations", expanded=True):
                for i, rec in enumerate(analysis["recommendations"], 1):
                    st.markdown(f"**{i}.** {rec}")
            
            # Concerning Trends Section
            with st.expander("⚠️ Concerning Trends", expanded=True):
                for i, concern in enumerate(analysis["concerning_trends"], 1):
                    st.markdown(f"**{i}.** {concern}")
        
        with tab2:
            st.markdown("### 📊 Analysis Results")
            st.markdown(processed_output["display_text"])
        
        with tab3:
            st.markdown("### 🔧 Raw AI Response")
            if "raw_response" in processed_output:
                st.markdown("**Raw unprocessed response from OpenAI:**")
                
                # Detect content type and render appropriately
                raw_response = processed_output["raw_response"]
                
                # Check if it contains HTML
                if "<html>" in raw_response.lower() or any(tag in raw_response.lower() for tag in ["<div>", "<p>", "<br>", "<h1>", "<h2>", "<h3>"]):
                    st.markdown("**Content Type:** HTML detected")
                    st.components.v1.html(raw_response, height=600, scrolling=True)
                else:
                    st.markdown("**Content Type:** Text/Markdown")
                    st.markdown("---")
                    st.markdown(raw_response)
                
                # Show response statistics
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Response Length", f"{len(raw_response)} chars")
                with col2:
                    st.metric("Word Count", f"{len(raw_response.split())} words")
                with col3:
                    st.metric("Line Count", f"{len(raw_response.splitlines())} lines")
            else:
                st.info("Raw response not available for this analysis.")
    
    return processed_output

def display_export_options(processed_output, property_name, export_type="full"):
    """Display export options for completed analysis
    
    Args:
        processed_output: The analysis results
        property_name: Name of the property
        export_type: Type of export - "full", "structured", "raw"
    """
    if not processed_output:
        return
    
    from src.ui.reports import generate_enhanced_report, generate_pdf_report, generate_word_report
    from datetime import datetime
    import json
    
    # Create filename base
    export_suffix = f"_{export_type}" if export_type != "full" else ""
    filename_base = f"T12_Analysis_{property_name.replace(' ', '_') if property_name else 'Property'}{export_suffix}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    if export_type == "structured":
        # Export only structured data
        st.subheader("� Export Structured Analysis")
        
        # Generate structured content
        structured_content = _generate_structured_export(processed_output)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download Structured Text",
                data=structured_content,
                file_name=f"{filename_base}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # JSON export of structured data
            if "analysis" in processed_output:
                structured_json = json.dumps(processed_output["analysis"], indent=2)
                st.download_button(
                    label="📊 Download JSON Data",
                    data=structured_json,
                    file_name=f"{filename_base}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    elif export_type == "raw":
        # Export raw AI response
        st.subheader("📄 Export Complete Report")
        
        raw_content = processed_output.get("raw_response", processed_output.get("display_text", "No content available"))
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download Raw Report",
                data=raw_content,
                file_name=f"{filename_base}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Markdown format
            st.download_button(
                label="📝 Download as Markdown",
                data=raw_content,
                file_name=f"{filename_base}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    else:
        # Full export with all formats (original behavior)
        st.subheader("📄 Export Options")
        
        # Generate enhanced report content
        report_content = generate_enhanced_report(processed_output)
        pdf_content = generate_pdf_report(processed_output)
        word_content = generate_word_report(processed_output)
        
        col_export1, col_export2, col_export3, col_export4 = st.columns(4)
        
        with col_export1:
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_content,
                file_name=f"{filename_base}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col_export2:
            st.download_button(
                label="📝 Download Word Report",
                data=word_content,
                file_name=f"{filename_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with col_export3:
            st.download_button(
                label="📄 Download Text Report",
                data=report_content,
                file_name=f"{filename_base}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_export4:
            st.download_button(
                label="📊 Download JSON Data",
                data=json.dumps(processed_output, indent=2, default=str),
                file_name=f"{filename_base}.json",
                mime="application/json",
                use_container_width=True
            )

def _generate_structured_export(processed_output):
    """Generate structured text export for structured analysis."""
    content = []
    content.append("T12 PROPERTY ANALYSIS - STRUCTURED REPORT")
    content.append("=" * 50)
    content.append("")
    
    if "analysis" in processed_output:
        analysis = processed_output["analysis"]
        
        # Strategic Questions
        if "strategic_questions" in analysis and analysis["strategic_questions"]:
            content.append("🎯 STRATEGIC MANAGEMENT QUESTIONS")
            content.append("-" * 30)
            for i, question in enumerate(analysis["strategic_questions"], 1):
                content.append(f"{i}. {question}")
            content.append("")
        
        # Recommendations
        if "recommendations" in analysis and analysis["recommendations"]:
            content.append("💡 ACTIONABLE RECOMMENDATIONS")
            content.append("-" * 30)
            for i, rec in enumerate(analysis["recommendations"], 1):
                content.append(f"{i}. {rec}")
            content.append("")
        
        # Concerning Trends
        if "concerning_trends" in analysis and analysis["concerning_trends"]:
            content.append("⚠️ CONCERNING TRENDS")
            content.append("-" * 30)
            for i, concern in enumerate(analysis["concerning_trends"], 1):
                content.append(f"{i}. {concern}")
            content.append("")
    
    content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return "\n".join(content)
