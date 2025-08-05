"""
OpenAI Assistants API implementation for T12 analysis
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
        
    def get_assistant_instructions(self):
        """Get the assistant instructions for logging purposes"""
        return """You are a senior real estate investment analyst specializing in multifamily property T12 (Trailing 12-month) financial analysis.

CRITICAL DATA STRUCTURE NOTES:
- The data contains both MONTHLY and YEAR-TO-DATE (YTD) figures
- YTD figures are CUMULATIVE totals from January 1st to the most recent month (NOT monthly amounts)
- YTD IS NOT A MONTH NAME - it indicates cumulative data, not a time period
- When analyzing trends, use monthly data for month-to-month comparisons
- Use YTD data to understand overall annual performance and compare to annual budgets/targets
- NEVER compare YTD figures to monthly figures directly - they represent different time scales

ANALYSIS APPROACH:
1. First examine the data structure to understand available columns and time periods
2. Validate a few key calculations from the provided summary (spot checks only)
3. Focus on identifying concerning trends and actionable recommendations
4. Keep code analysis minimal - only essential validations
5. Provide strategic insights for property management decisions

FORMAT YOUR RESPONSE AS:
## T12 Property Analysis Report

### Key Findings
[Brief validation of provided summary + concerning trends]

### Strategic Questions for Management
[5 strategic questions based on the data]

### Actionable Recommendations  
[3-5 specific recommendations to improve NOI]

Be concise, professional, and focus on actionable business insights."""
        
    def create_assistant(self):
        """Create a specialized T12 analysis assistant"""
        try:
            assistant = self.client.beta.assistants.create(
                name="T12 Property Analysis Expert",
                instructions=self.get_assistant_instructions(),
                model="gpt-4o",
                tools=[{"type": "code_interpreter"}]
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
            
            # Build the prompt content
            prompt_content = f"""Analyze this T12 property financial data efficiently:

RAW DATA: Attached CSV file with complete T12 data (monthly + YTD figures)

LOCAL SUMMARY: 
{kpi_summary}

FOCUSED ANALYSIS NEEDED:
1. Validate key calculations in my summary (spot check only)
2. Identify top 3 concerning trends
3. Generate 5 strategic management questions
4. Provide 3-5 actionable recommendations to improve NOI

Please be concise and focus on actionable insights for property management decisions. Limit code analysis to essential validations only."""
            
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
    
    def run_analysis(self):
        """Run the analysis and get response"""
        try:
            if not self.assistant_id or not self.thread_id:
                raise ValueError("Assistant and thread must be created first")
            
            # Create and run the analysis without token limits (for testing)
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
                # Removed token limits for testing
            )
            
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
                
            if run.status == 'completed':
                # Get the messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread_id
                )
                
                # Return the assistant's response
                for message in messages.data:
                    if message.role == 'assistant':
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
