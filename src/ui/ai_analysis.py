"""
AI analysis UI components with enhanced and standard options
"""
import streamlit as st
from datetime import datetime
from src.ai.prompt import build_prompt, call_openai, validate_response
from src.ai.assistants_api import analyze_with_assistants_api
from src.core.output_quality import post_process_output

def display_ai_analysis_section(df, kpi_summary, api_key, property_name, property_address):
    """Display AI analysis section with method selection"""
    
    st.subheader("🤖 AI-Powered Analysis")
    
    # Analysis method selection
    analysis_method = st.radio(
        "Choose Analysis Method:",
        ["🚀 Enhanced Analysis (Assistants API + Raw Data)", "📄 Standard Analysis (Text Summary Only)"],
        help="Enhanced analysis lets AI examine your raw data directly for deeper insights"
    )
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to generate AI analysis")
        st.info("💡 Your API key is used securely and is not stored")
        return None
    
    if st.button("🎯 Generate AI Analysis", type="primary", use_container_width=True):
        return run_ai_analysis(df, kpi_summary, analysis_method, api_key, property_name, property_address)
    
    return None

def run_ai_analysis(df, kpi_summary, analysis_method, api_key, property_name, property_address):
    """Execute AI analysis based on selected method"""
    
    # AI Analysis with detailed progress
    ai_progress = st.progress(0)
    ai_status = st.empty()
    
    ai_status.text("🔧 Building analysis prompt...")
    ai_progress.progress(25)
    
    try:
        # Choose analysis method based on user selection  
        if analysis_method.startswith("🚀 Enhanced"):
            # Enhanced Analysis with Assistants API
            ai_status.text("🚀 Initializing Enhanced AI Analysis...")
            ai_progress.progress(30)
            
            ai_status.text("📊 Uploading raw data to OpenAI...")
            ai_progress.progress(50)
            
            try:
                ai_response = analyze_with_assistants_api(df, kpi_summary, api_key)
                ai_status.text("✨ Enhanced analysis complete!")
                ai_progress.progress(100)
                
            except Exception as e:
                st.error(f"Enhanced analysis failed: {str(e)}")
                ai_status.text("🔄 Falling back to standard analysis...")
                ai_progress.progress(60)
                
                # Fallback to standard analysis
                system_prompt, user_prompt = build_prompt(kpi_summary)
                ai_response = call_openai(system_prompt, user_prompt, api_key)
        
        else:
            # Standard Analysis (Text Summary Only)
            system_prompt, user_prompt = build_prompt(kpi_summary)
            ai_status.text("🤖 Calling OpenAI API...")
            ai_progress.progress(50)
            ai_response = call_openai(system_prompt, user_prompt, api_key)
        
        ai_status.text("✨ Processing AI response...")
        ai_progress.progress(75)
        
        # Validate and post-process response
        if not ai_response.startswith("Error:"):
            is_valid, validation_msg = validate_response(ai_response)
            
            if is_valid:
                # Post-process the output
                property_info = {
                    "name": property_name or "Unknown Property",
                    "address": property_address or "No address provided"
                }
                
                processed_output = post_process_output(ai_response, property_info)
                
                ai_status.text("✅ Analysis complete!")
                ai_progress.progress(100)
                
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

def display_analysis_results(processed_output):
    """Display formatted AI analysis results"""
    if not processed_output:
        return
    
    # Display formatted results
    st.markdown("### 📊 Analysis Results")
    st.markdown(processed_output["display_text"])
    
    # Show detailed AI analysis sections
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
    
    # Show quality metrics
    quality = processed_output["quality_metrics"]
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.metric("Quality Score", f"{quality['overall_score']}/100")
    with col_q2:
        st.metric("Quality Level", quality['quality_level'])
    with col_q3:
        st.metric("Questions Found", len(processed_output["analysis"]["strategic_questions"]))
    
    return processed_output

def display_export_options(processed_output, property_name):
    """Display export options for completed analysis"""
    if not processed_output:
        return
    
    from src.ui.reports import generate_enhanced_report, generate_pdf_report, generate_word_report
    
    st.subheader("📄 Export Options")
    
    # Generate enhanced report content
    report_content = generate_enhanced_report(processed_output)
    pdf_content = generate_pdf_report(processed_output)
    word_content = generate_word_report(processed_output)
    
    # Create filename base
    filename_base = f"T12_Analysis_{property_name.replace(' ', '_') if property_name else 'Property'}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
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
            data=str(processed_output),
            file_name=f"{filename_base}.json",
            mime="application/json",
            use_container_width=True
        )
