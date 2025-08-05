"""
Data analysis and debugging UI components
"""
import streamlit as st
import pandas as pd
import io
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
    with st.expander("🧪 Test OpenAI Prompt", expanded=False):
        
        # Prompt type selection
        prompt_type = st.radio(
            "Select Prompt Type to Preview:",
            ["📄 Standard Analysis", "🚀 Enhanced Analysis"],
            horizontal=True,
            help="Choose which analysis method's prompt you want to see"
        )
        
        if st.button("Generate Test Prompt", key="test_prompt"):
            try:
                if prompt_type == "📄 Standard Analysis":
                    # Standard Analysis Prompt
                    system_prompt, user_prompt = build_prompt(kpi_summary)
                    
                    st.write("**📄 Standard Analysis - System Prompt:**")
                    st.text_area("", system_prompt, height=200, disabled=True, key="sys_prompt_std")
                    
                    st.write("**📄 Standard Analysis - User Prompt:**")
                    st.text_area("", user_prompt, height=300, disabled=True, key="user_prompt_std")
                    
                    # Show token count estimation
                    total_chars = len(system_prompt) + len(user_prompt)
                    estimated_tokens = total_chars // 4
                    st.info(f"📊 Standard Analysis - Estimated tokens: ~{estimated_tokens:,} (Characters: {total_chars:,})")
                    
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
                    
                    st.write("**🚀 Enhanced Analysis - System Instructions (Assistant):**")
                    st.text_area("", system_instructions, height=300, disabled=True, key="sys_prompt_enh")
                    
                    st.write("**🚀 Enhanced Analysis - User Message:**")
                    st.text_area("", user_content, height=250, disabled=True, key="user_prompt_enh")
                    
                    st.write("**🚀 Enhanced Analysis - Additional Context:**")
                    st.info("📁 **Raw Data File**: Complete T12 CSV data is uploaded to OpenAI with code_interpreter access")
                    st.info("🧠 **AI Model**: GPT-4o with code_interpreter tool enabled")
                    st.info("🔍 **Analysis Capability**: AI can run Python code to analyze your raw data directly")
                    
                    # Show token count estimation
                    total_chars = len(system_instructions) + len(user_content) + len(kpi_summary)
                    estimated_tokens = total_chars // 4
                    st.info(f"📊 Enhanced Analysis - Estimated tokens: ~{estimated_tokens:,} (Characters: {total_chars:,})")
                
                st.success("✅ Prompts generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating prompts: {str(e)}")

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
