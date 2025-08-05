"""
OpenAI Assistants API implementation for multi-format property analysis
Enables AI to analyze raw data directly using code_interpreter
"""

import os
import logging
import tempfile
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
from .prompt_manager import prompt_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyAssistantAnalyzer:
    """OpenAI Assistant for property data analysis with code_interpreter"""
    
    def __init__(self, api_key=None):
        """Initialize the assistant with OpenAI API key"""
        load_dotenv()
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
        if not self.client.api_key:
            raise ValueError("OpenAI API key not provided")
            
        self.assistant_id = None
        self.thread_id = None
        
    def get_assistant_instructions(self, format_name="t12_monthly_financial"):
        """Get format-specific assistant instructions"""
        return prompt_manager.build_system_instructions(format_name, "assistants")
        return """You are a senior real estate investment analyst specializing in multifamily property T12 (Trailing 12-month) financial analysis.

CRITICAL DATA STRUCTURE NOTES:
- The data contains both MONTHLY and YEAR-TO-DATE (YTD) figures
- YTD figures are CUMULATIVE totals from January 1st to the most recent month (NOT monthly amounts)
- YTD IS NOT A MONTH NAME - it indicates cumulative data, not a time period
- When analyzing trends, use monthly data for month-to-month comparisons
- Use YTD data to understand overall annual performance and compare to annual budgets/targets
- NEVER compare YTD figures to monthly figures directly - they represent different time scales

ANALYSIS APPROACH:
1. FIRST: Load and examine the CSV data structure - show me the columns and data shape
2. SECOND: Validate key calculations from my summary using actual data calculations 
3. THIRD: Perform month-over-month trend analysis on key metrics (Revenue, NOI, Occupancy)
4. FOURTH: Calculate percentage changes and identify concerning patterns
5. SHOW YOUR WORK: Display Python code and calculations you used
6. Provide strategic insights based on your data analysis

MANDATORY REQUIREMENTS:
- ALWAYS show the Python code you write to analyze the data
- ALWAYS display month-over-month trend calculations with actual numbers
- ALWAYS validate at least 3 key metrics from my summary against raw data
- ALWAYS show data structure (df.head(), df.shape, df.columns)
- Focus on actionable insights from your raw data analysis

FORMAT YOUR RESPONSE AS:
## T12 Property Analysis Report

### Data Validation & Structure
[Show data loading, structure, and validation of key calculations]

### Month-over-Month Trend Analysis  
[Show trend calculations with actual percentage changes]

### Key Findings
[Insights from your raw data analysis]

### Strategic Questions for Management
[5 strategic questions based on your data analysis]

### Actionable Recommendations
[3-5 specific recommendations based on trend analysis]

CRITICAL: Always show the Python code and calculations you performed."""
        
    def create_assistant(self, format_name="t12_monthly_financial"):
        """Create a specialized property analysis assistant for the given format"""
        try:
            assistant = self.client.beta.assistants.create(
                name=f"Property Analysis Expert - {format_name.upper()}",
                instructions=self.get_assistant_instructions(format_name),
                model="gpt-4o",
                tools=[{"type": "code_interpreter"}]
            )
            
            self.assistant_id = assistant.id
            logger.info(f"Created assistant with ID: {self.assistant_id} for format: {format_name}")
            return assistant
            
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            raise
    
    def upload_dataframe(self, df):
        """Upload DataFrame to OpenAI as CSV file"""
        try:
            # Create temporary CSV file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as temp_file:
                df.to_csv(temp_file, index=False)
                temp_path = temp_file.name
            
            # Upload file to OpenAI
            with open(temp_path, 'rb') as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose='assistants'
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            logger.info(f"Uploaded DataFrame as file ID: {uploaded_file.id}")
            return uploaded_file.id
            
        except Exception as e:
            logger.error(f"Error uploading DataFrame: {str(e)}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def create_thread_with_data(self, df, kpi_summary, format_name="t12_monthly_financial"):
        """Create a conversation thread with both raw data and KPI summary"""
        try:
            # Upload the DataFrame
            file_id = self.upload_dataframe(df)
            
            # Build format-specific prompt content
            format_upper = format_name.upper().replace("_", " ")
            prompt_content = f"""Analyze this {format_upper} property financial data by directly examining the raw CSV data:

RAW CSV DATA: Use the attached CSV file to perform your analysis - this contains complete property data.

MY LOCAL SUMMARY (for reference only): 
{kpi_summary}

ANALYSIS REQUIREMENTS:
1. Load and examine the CSV data structure
2. Perform detailed trend analysis on key metrics based on the format type
3. Validate key numbers from my summary using the raw data
4. Calculate percentage changes and identify patterns
5. Provide actionable insights based on your data analysis

FOCUS AREAS:
- Month-over-month Revenue trends with percentage changes
- NOI performance and concerning patterns  
- Occupancy/vacancy trends over time
- Validate my Revenue, NOI, and expense calculations against raw data
- Identify any data quality issues or anomalies

Please provide a comprehensive analysis with strategic recommendations based on your examination of the raw data."""
            
            # Log the exact prompt being sent
            logger.info("=== ENHANCED ANALYSIS PROMPT ===")
            logger.info(f"Assistant Instructions (system): {self.get_assistant_instructions()}")
            logger.info(f"User Message Content:\n{prompt_content}")
            logger.info(f"Attached File ID: {file_id}")
            logger.info("================================")
            
            # Create thread with initial message using correct attachments format
            thread = self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_content,
                        "attachments": [
                            {
                                "file_id": file_id,
                                "tools": [{"type": "code_interpreter"}]
                            }
                        ]
                    }
                ]
            )
            
            self.thread_id = thread.id
            logger.info(f"Created thread with ID: {self.thread_id}")
            return thread
            
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise
    
    def run_analysis(self, progress_callback=None):
        """Run the analysis and get response"""
        try:
            if not self.assistant_id or not self.thread_id:
                raise ValueError("Assistant and thread must be created first")

            if progress_callback:
                progress_callback("🚀 Starting analysis run...", 55)

            # Create and run the analysis without token limits (for testing)
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
                # Removed token limits for testing
            )
            
            if progress_callback:
                progress_callback("🔄 Analysis in progress...", 60)

            # Wait for completion with extended timeout (no token limits)
            max_polls = 60  # Increased from 30 for unlimited analysis
            poll_count = 0
            
            while run.status in ['queued', 'in_progress', 'cancelling'] and poll_count < max_polls:
                time.sleep(2)  # Wait 2 seconds between polls
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
                poll_count += 1
                logger.info(f"Run status: {run.status} (poll {poll_count}/{max_polls})")
                
                # Update progress during polling
                if progress_callback:
                    progress_pct = min(95, 60 + (poll_count / max_polls) * 35)  # 60% to 95%
                    if run.status == 'queued':
                        progress_callback(f"⏳ Analysis queued... (poll {poll_count}/{max_polls})", progress_pct)
                    elif run.status == 'in_progress':
                        progress_callback(f"🧠 AI analyzing your data... (poll {poll_count}/{max_polls})", progress_pct)
                    elif run.status == 'cancelling':
                        progress_callback(f"⚠️ Analysis cancelling... (poll {poll_count}/{max_polls})", progress_pct)
                
            if progress_callback:
                progress_callback("📄 Retrieving results...", 98)
                
            if run.status == 'completed':
                # Get the messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread_id
                )
                
                # Return the assistant's response
                for message in messages.data:
                    if message.role == 'assistant':
                        if progress_callback:
                            progress_callback("✅ Analysis complete!", 100)
                        return message.content[0].text.value
                        
            elif run.status == 'incomplete':
                # Handle incomplete runs (usually due to token limits)
                logger.warning(f"Run incomplete. Reason: {getattr(run, 'incomplete_details', 'Token limit likely exceeded')}")
                
                # Try to get partial response
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread_id
                )
                
                partial_response = None
                for message in messages.data:
                    if message.role == 'assistant':
                        partial_response = message.content[0].text.value
                        break
                
                if partial_response and len(partial_response.strip()) > 100:
                    return f"Enhanced analysis (partial due to length): {partial_response}"
                else:
                    return "Enhanced analysis incomplete: Analysis exceeded token limits. Try with a smaller dataset or use Standard Analysis."
                
            elif run.status == 'failed':
                # Get detailed error information
                logger.error(f"Run failed. Last error: {getattr(run, 'last_error', 'No error details available')}")
                return f"Enhanced analysis failed: {getattr(run, 'last_error', {}).get('message', 'Unknown error occurred during processing')}"
                
            elif poll_count >= max_polls:
                logger.error("Run timed out after maximum polling attempts")
                return "Enhanced analysis timed out. The analysis was taking too long to complete."
                
            else:
                logger.error(f"Run ended with unexpected status: {run.status}")
                return f"Enhanced analysis ended with status: {run.status}. Please try Standard Analysis instead."
                
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            return f"Error running analysis: {str(e)}"
    
    def analyze_property_data(self, df, kpi_summary, progress_callback=None, format_name="t12_monthly_financial"):
        """Complete property analysis workflow with format-specific instructions"""
        try:
            # Create assistant if not exists
            if not self.assistant_id:
                if progress_callback:
                    progress_callback("🤖 Creating AI assistant...", 10)
                self.create_assistant(format_name)
            
            # Create thread with data
            if progress_callback:
                progress_callback("📤 Uploading data to OpenAI...", 30)
            self.create_thread_with_data(df, kpi_summary, format_name)
            
            # Run analysis
            if progress_callback:
                progress_callback("🧠 Starting AI analysis...", 50)
            result = self.run_analysis(progress_callback)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in complete analysis: {str(e)}")
            return f"Error in analysis: {str(e)}"
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.assistant_id:
                self.client.beta.assistants.delete(self.assistant_id)
                logger.info(f"Deleted assistant: {self.assistant_id}")
        except Exception as e:
            logger.warning(f"Error cleaning up assistant: {str(e)}")

def analyze_with_assistants_api(df, kpi_summary, api_key=None, progress_callback=None, format_name="t12_monthly_financial"):
    """Convenience function for property analysis using Assistants API"""
    analyzer = PropertyAssistantAnalyzer(api_key)
    try:
        return analyzer.analyze_property_data(df, kpi_summary, progress_callback, format_name)
    finally:
        analyzer.cleanup()
