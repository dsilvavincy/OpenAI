"""
Data analysis and debugging UI components
"""
import streamlit as st
import pandas as pd
import io
import os
from src.core.kpi_summary import generate_kpi_summary
from src.ai.prompt import build_prompt

def display_data_analysis_section(df):
    """Display comprehensive data analysis and debugging tools"""
    
    # Data preview
    with st.expander("📊 View Data Preview", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.info(f"Showing first 10 rows of {len(df):,} total rows")

    # YTD vs Monthly data analysis
    if 'MonthParsed' in df.columns and 'IsYTD' in df.columns:
        # Only check non-YTD rows for invalid MonthParsed
        non_ytd_df = df[df['IsYTD'] == False]
        invalid_month_rows = non_ytd_df[non_ytd_df['MonthParsed'].isnull()]
        
        with st.expander(f"🚨 Invalid MonthParsed (Non-YTD): {len(invalid_month_rows)}", expanded=False):
            if len(invalid_month_rows) > 0:
                st.dataframe(invalid_month_rows, use_container_width=True)
                st.error(f"❌ {len(invalid_month_rows)} non-YTD rows have invalid MonthParsed")
                
                # Show unique Month values that failed to parse
                unique_failed_months = invalid_month_rows['Month'].unique()
                st.write("**Failed to parse these Month values:**")
                for month in unique_failed_months[:10]:  # Show first 10
                    st.write(f"- '{month}'")
                if len(unique_failed_months) > 10:
                    st.write(f"... and {len(unique_failed_months) - 10} more")
            else:
                st.success("✅ All non-YTD MonthParsed values are valid!")
        
        # Show YTD summary separately
        ytd_df = df[df['IsYTD'] == True]
        with st.expander(f"📅 YTD Rows Summary: {len(ytd_df)}", expanded=False):
            if len(ytd_df) > 0:
                st.info(f"✅ {len(ytd_df)} YTD rows found (MonthParsed is expected to be null)")
                st.dataframe(ytd_df[['Metric', 'Month', 'Value']].head(10), use_container_width=True)
            else:
                st.warning("⚠️ No YTD rows found in data")
    
    # DataFrame structure and statistics
    with st.expander("📊 DataFrame Analysis", expanded=False):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.write("**Shape:**", df.shape)
            st.write("**Columns:**", list(df.columns))
            st.write("**Data Types:**")
            st.dataframe(pd.DataFrame(df.dtypes).rename(columns={0: 'Type'}), use_container_width=True)
        
        with col_info2:
            st.write("**Key Statistics:**")
            if 'IsYTD' in df.columns:
                ytd_count = df[df['IsYTD'] == True].shape[0]
                non_ytd_count = df[df['IsYTD'] == False].shape[0]
                st.write(f"- YTD rows: {ytd_count}")
                st.write(f"- Monthly rows: {non_ytd_count}")
            
            if 'Metric' in df.columns:
                st.write(f"- Unique metrics: {df['Metric'].nunique()}")
                st.write("**Top 10 Metrics:**")
                top_metrics = df['Metric'].value_counts().head(10)
                for metric, count in top_metrics.items():
                    st.write(f"  • {metric}: {count} rows")
            
            if 'Value' in df.columns:
                st.write(f"- Total values: {df['Value'].count()}")
                st.write(f"- Missing values: {df['Value'].isna().sum()}")

def display_kpi_testing_section(df):
    """Display KPI summary testing tools"""
    with st.expander("🧪 Test KPI Summary Generation", expanded=False):
        if st.button("Generate Test KPI Summary", key="test_kpi"):
            try:
                test_kpi_summary = generate_kpi_summary(df)
                st.text_area("Generated KPI Summary:", test_kpi_summary, height=400)
                st.success("✅ KPI Summary generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating KPI Summary: {str(e)}")
                st.write("**DataFrame info for debugging:**")
                st.write(f"Shape: {df.shape}")
                st.write(f"Columns: {list(df.columns)}")
                if not df.empty:
                    st.write("**Sample data:**")
                    st.dataframe(df.head(), use_container_width=True)

def display_prompt_testing_section(kpi_summary, df=None):
    """Display OpenAI prompt testing tools"""
    with st.expander("🧪 View OpenAI Prompts (Click to expand)", expanded=True):
        
        st.markdown("**🔍 What you'll see here:**")
        st.markdown("- The exact system and user prompts sent to OpenAI")
        st.markdown("- Token count estimates for cost planning")  
        st.markdown("- Comparison between Standard vs Enhanced Analysis approaches")
        st.markdown("- Test your custom prompt modifications live")
        
        # Prompt Library/Save functionality
        st.markdown("**💾 Prompt Management:**")
        col_save, col_load = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Current Prompts", help="Save your edited prompts for later use"):
                if 'sys_prompt_std' in st.session_state or 'sys_prompt_enh' in st.session_state:
                    if 'saved_prompts' not in st.session_state:
                        st.session_state['saved_prompts'] = {}
                    
                    prompt_name = st.text_input("Save as:", placeholder="My Custom Prompt")
                    if prompt_name:
                        st.session_state['saved_prompts'][prompt_name] = {
                            'std_system': st.session_state.get('sys_prompt_std', ''),
                            'std_user': st.session_state.get('user_prompt_std', ''),
                            'enh_system': st.session_state.get('sys_prompt_enh', ''),
                            'enh_user': st.session_state.get('user_prompt_enh', '')
                        }
                        st.success(f"✅ Saved '{prompt_name}'")
        
        with col_load:
            if st.button("📁 Load Saved Prompts", help="Load previously saved prompts"):
                if st.session_state.get('saved_prompts'):
                    saved_names = list(st.session_state['saved_prompts'].keys())
                    selected = st.selectbox("Choose saved prompt:", saved_names)
                    if selected and st.button("Load"):
                        saved = st.session_state['saved_prompts'][selected]
                        st.session_state['sys_prompt_std'] = saved['std_system']
                        st.session_state['user_prompt_std'] = saved['std_user']
                        st.session_state['sys_prompt_enh'] = saved['enh_system']
                        st.session_state['user_prompt_enh'] = saved['enh_user']
                        st.success(f"✅ Loaded '{selected}'")
                        st.rerun()
                else:
                    st.info("No saved prompts found")
        
        # Prompt type selection
        prompt_type = st.radio(
            "Select Prompt Type to Preview:",
            ["📄 Standard Analysis", "🚀 Enhanced Analysis"],
            horizontal=True,
            help="Choose which analysis method's prompt you want to see"
        )
        
        if st.button("🔍 Show Me The Prompts!", key="test_prompt", type="primary"):
            try:
                if prompt_type == "📄 Standard Analysis":
                    # Standard Analysis Prompt
                    system_prompt, user_prompt = build_prompt(kpi_summary)
                    
                    st.write("**📄 Standard Analysis - System Prompt (Editable):**")
                    edited_system_prompt = st.text_area(
                        "System Prompt", 
                        system_prompt, 
                        height=200, 
                        key="sys_prompt_std",
                        label_visibility="collapsed"
                    )
                    
                    st.write("**📄 Standard Analysis - User Prompt (Editable):**")
                    edited_user_prompt = st.text_area(
                        "User Prompt", 
                        user_prompt, 
                        height=300, 
                        key="user_prompt_std",
                        label_visibility="collapsed"
                    )
                    
                    # Show token count estimation
                    total_chars = len(edited_system_prompt) + len(edited_user_prompt)
                    estimated_tokens = total_chars // 4
                    st.info(f"📊 Standard Analysis - Estimated tokens: ~{estimated_tokens:,} (Characters: {total_chars:,})")
                    
                    # Test the edited prompts
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🧪 Test Edited Prompts", key="test_edited_std"):
                            st.session_state['test_system_prompt'] = edited_system_prompt
                            st.session_state['test_user_prompt'] = edited_user_prompt
                            st.session_state['show_test_result'] = True
                    
                    with col2:
                        if st.button("↩️ Reset to Default", key="reset_std"):
                            st.rerun()
                    
                else:
                    # Enhanced Analysis Prompt
                    if df is None:
                        st.warning("⚠️ Enhanced Analysis requires uploaded data. Please upload a T12 file first.")
                        return
                        
                    from src.ai.assistants_api import T12AssistantAnalyzer
                    
                    # Get the Enhanced Analysis prompts
                    analyzer = T12AssistantAnalyzer()
                    system_instructions = analyzer.get_assistant_instructions()
                    
                    # Build the user prompt
                    user_content = f"""Analyze this T12 property financial data efficiently:

RAW DATA: Attached CSV file with complete T12 data (monthly + YTD figures)

LOCAL SUMMARY: 
{kpi_summary}

FOCUSED ANALYSIS NEEDED:
1. Validate key calculations in my summary (spot check only)
2. Identify top 3 concerning trends
3. Generate 5 strategic management questions
4. Provide 3-5 actionable recommendations to improve NOI

Please be concise and focus on actionable insights for property management decisions. Limit code analysis to essential validations only."""
                    
                    st.write("**🚀 Enhanced Analysis - System Instructions (Editable):**")
                    edited_system_instructions = st.text_area(
                        "System Instructions", 
                        system_instructions, 
                        height=300, 
                        key="sys_prompt_enh",
                        label_visibility="collapsed"
                    )
                    
                    st.write("**🚀 Enhanced Analysis - User Message (Editable):**")
                    edited_user_content = st.text_area(
                        "User Message", 
                        user_content, 
                        height=250, 
                        key="user_prompt_enh",
                        label_visibility="collapsed"
                    )
                    
                    st.write("**🚀 Enhanced Analysis - Additional Context:**")
                    st.info("📁 **Raw Data File**: Complete T12 CSV data is uploaded to OpenAI with code_interpreter access")
                    st.info("🧠 **AI Model**: GPT-4o with code_interpreter tool enabled")
                    st.info("🔍 **Analysis Capability**: AI can run Python code to analyze your raw data directly")
                    
                    # Show token count estimation
                    total_chars = len(edited_system_instructions) + len(edited_user_content) + len(kpi_summary)
                    estimated_tokens = total_chars // 4
                    st.info(f"📊 Enhanced Analysis - Estimated tokens: ~{estimated_tokens:,} (Characters: {total_chars:,})")
                    
                    # Test the edited prompts for Enhanced Analysis
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🧪 Test Edited Enhanced Analysis", key="test_edited_enh"):
                            st.session_state['test_enhanced_system'] = edited_system_instructions
                            st.session_state['test_enhanced_user'] = edited_user_content
                            st.session_state['show_enhanced_test_result'] = True
                    
                    with col2:
                        if st.button("↩️ Reset to Default", key="reset_enh"):
                            st.rerun()
                
                st.success("✅ Prompts generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating prompts: {str(e)}")
        
        # Handle test results for edited prompts
        if st.session_state.get('show_test_result', False):
            st.markdown("---")
            st.markdown("### 🧪 Custom Prompt Test Results")
            
            # Get API key from session state or environment
            from dotenv import load_dotenv
            load_dotenv()
            api_key = st.session_state.get('openai_api_key') or os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                st.error("❌ API key required to test prompts. Please set your API key in the sidebar.")
                st.session_state['show_test_result'] = False
            else:
                with st.spinner("🔄 Testing your custom prompts..."):
                    try:
                        from src.ai.prompt import call_openai
                        result = call_openai(
                            st.session_state['test_system_prompt'],
                            st.session_state['test_user_prompt'],
                            api_key
                        )
                        
                        st.success("✅ Custom prompt test completed!")
                        st.text_area("Test Result", result, height=400, label_visibility="collapsed")
                        
                        # Clear test state
                        if st.button("✨ Clear Test Results"):
                            st.session_state['show_test_result'] = False
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error testing custom prompts: {str(e)}")
                        st.session_state['show_test_result'] = False
        
        # Handle Enhanced Analysis test results  
        if st.session_state.get('show_enhanced_test_result', False):
            st.markdown("---")
            st.markdown("### 🚀 Custom Enhanced Analysis Test Results")
            st.info("⚠️ Enhanced Analysis testing requires the full Assistants API implementation with file upload.")
            st.info("💡 **Note:** This would create a new Assistant with your custom instructions and test it with your data.")
            
            # For now, show what would be sent
            st.write("**Your Custom System Instructions:**")
            st.text_area("", st.session_state.get('test_enhanced_system', ''), height=200, disabled=True)
            
            st.write("**Your Custom User Message:**")
            st.text_area("", st.session_state.get('test_enhanced_user', ''), height=150, disabled=True)
            
            if st.button("✨ Clear Enhanced Test Results"):
                st.session_state['show_enhanced_test_result'] = False
                st.rerun()

def display_file_processing_section(uploaded_file):
    """Handle file processing workflow"""
    try:
        # Show file details
        file_size = len(uploaded_file.getvalue())
        st.info(f"📁 **File:** {uploaded_file.name}")
        st.info(f"📏 **Size:** {file_size/1024:.1f} KB")
        
        # Process the file with progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📂 Reading Excel file...")
        progress_bar.progress(20)
        
        # Read Excel file directly from memory (no temp file)
        status_text.text("⚙️ Processing T12 data...")
        progress_bar.progress(50)
        
        # Use BytesIO to pass file-like object to tidy_sheet_all
        from src.core.preprocess import tidy_sheet_all
        excel_buffer = io.BytesIO(uploaded_file.getvalue())
        df = tidy_sheet_all(excel_buffer)
        
        status_text.text("✅ Data processing complete!")
        progress_bar.progress(100)
        
        st.success(f"✅ Successfully processed {len(df):,} data points")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("💡 **Troubleshooting tips:**")
        st.info("• Ensure the file is a valid T12 Excel format")
        st.info("• Check that the file isn't corrupted")
        st.info("• Try uploading a different file")
        return None
