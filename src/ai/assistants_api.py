"""
OpenAI Assistants API implementation for T12 analysis
Enables AI to analyze raw data directly using code_interpreter
"""

import os
import logging
import tempfile
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class T12AssistantAnalyzer:
    """OpenAI Assistant for T12 data analysis with code_interpreter"""
    
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
        
    def create_assistant(self):
        """Create a specialized T12 analysis assistant"""
        try:
            assistant = self.client.beta.assistants.create(
                name="T12 Property Analysis Expert",
                instructions="""You are a senior real estate investment analyst specializing in multifamily property T12 (Trailing 12-month) financial analysis.

CRITICAL DATA STRUCTURE NOTES:
- The data contains both MONTHLY and YEAR-TO-DATE (YTD) figures
- YTD figures are CUMULATIVE totals from January 1st to the most recent month (NOT monthly amounts)
- YTD IS NOT A MONTH NAME - it indicates cumulative data, not a time period
- When analyzing trends, use monthly data for month-to-month comparisons
- Use YTD data to understand overall annual performance and compare to annual budgets/targets
- NEVER compare YTD figures to monthly figures directly - they represent different time scales

ANALYSIS REQUIREMENTS:
1. VERIFY DATA QUALITY: Check for missing values, outliers, and data consistency
2. CALCULATE KEY METRICS: Revenue trends, NOI, occupancy rates, expense ratios
3. TREND ANALYSIS: Month-over-month changes, seasonal patterns, performance trajectory
4. COMPARATIVE ANALYSIS: Compare monthly vs YTD performance appropriately
5. RISK ASSESSMENT: Identify red flags, concerning patterns, and potential issues
6. ACTIONABLE INSIGHTS: Provide specific, implementable recommendations

OUTPUT FORMAT:
- Generate exactly 5 strategic management questions for investigation
- Provide 3-5 specific actionable recommendations to improve NOI
- Highlight concerning trends requiring immediate attention
- Include industry context and benchmarking where relevant
- When referencing YTD figures, clearly state they are cumulative totals

Use code_interpreter to:
- Analyze the raw data thoroughly
- Create visualizations if helpful
- Perform statistical analysis
- Validate calculations
- Generate custom insights beyond the provided summary""",
                tools=[{"type": "code_interpreter"}],
                model="gpt-4-1106-preview"
            )
            
            self.assistant_id = assistant.id
            logger.info(f"Created assistant with ID: {self.assistant_id}")
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
    
    def create_thread_with_data(self, df, kpi_summary):
        """Create a conversation thread with both raw data and KPI summary"""
        try:
            # Upload the DataFrame
            file_id = self.upload_dataframe(df)
            
            # Create thread with initial message
            thread = self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"""I need you to analyze this T12 property financial data. I'm providing both:

1. RAW DATA: The attached CSV file contains the complete processed T12 data with all monthly and YTD figures
2. LOCAL SUMMARY: Here's a preliminary KPI summary I generated locally:

{kpi_summary}

Please use the code_interpreter to:
- Load and examine the raw CSV data
- Validate the calculations in my summary
- Perform your own comprehensive analysis
- Generate additional insights I may have missed
- Create any helpful visualizations
- Provide strategic recommendations based on the complete dataset

Focus on actionable insights for property management and investment decisions.""",
                        "file_ids": [file_id]
                    }
                ]
            )
            
            self.thread_id = thread.id
            logger.info(f"Created thread with ID: {self.thread_id}")
            return thread
            
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise
    
    def run_analysis(self):
        """Run the analysis and get response"""
        try:
            if not self.assistant_id or not self.thread_id:
                raise ValueError("Assistant and thread must be created first")
            
            # Create and run the analysis
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while run.status in ['queued', 'in_progress', 'cancelling']:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
                
            if run.status == 'completed':
                # Get the messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread_id
                )
                
                # Return the assistant's response
                for message in messages.data:
                    if message.role == 'assistant':
                        return message.content[0].text.value
                        
            else:
                logger.error(f"Run failed with status: {run.status}")
                return f"Analysis failed with status: {run.status}"
                
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            return f"Error running analysis: {str(e)}"
    
    def analyze_t12_data(self, df, kpi_summary):
        """Complete T12 analysis workflow"""
        try:
            # Create assistant if not exists
            if not self.assistant_id:
                self.create_assistant()
            
            # Create thread with data
            self.create_thread_with_data(df, kpi_summary)
            
            # Run analysis
            result = self.run_analysis()
            
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

def analyze_with_assistants_api(df, kpi_summary, api_key=None):
    """Convenience function for T12 analysis using Assistants API"""
    analyzer = T12AssistantAnalyzer(api_key)
    try:
        return analyzer.analyze_t12_data(df, kpi_summary)
    finally:
        analyzer.cleanup()
