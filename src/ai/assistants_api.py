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
        
    def create_assistant(self, format_name="t12_monthly_financial", model="gpt-4o"):
        """Create a specialized property analysis assistant for the given format"""
        try:
            assistant = self.client.beta.assistants.create(
                name=f"Property Analysis Expert - {format_name.upper()}",
                instructions=self.get_assistant_instructions(format_name),
                model=model,
                tools=[{"type": "code_interpreter"}]
            )
            
            self.assistant_id = assistant.id
            logger.info(f"Created assistant with ID: {self.assistant_id} for format: {format_name} using model: {model}")
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
    
    def run_analysis(self, progress_callback=None, streaming_callback=None):
        """Run the analysis and get response using streaming (stream=True)"""
        try:
            if not self.assistant_id or not self.thread_id:
                raise ValueError("Assistant and thread must be created first")

            if progress_callback:
                progress_callback("🚀 Starting analysis run...", 55)

            # Create and run the analysis with streaming enabled
            stream = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id,
                stream=True
            )
            
            if progress_callback:
                progress_callback("🔄 Streaming analysis in progress...", 60)

            # Accumulate streamed deltas
            full_response = ""
            event_count = 0
            
            for event in stream:
                event_count += 1
                logger.info(f"Received event {event_count}: {type(event)} - {getattr(event, 'event', 'no event attr')}")
                
                # Handle different event types from OpenAI streaming
                new_text = ""
                
                # Check if this is a message delta event
                if hasattr(event, 'event') and event.event == 'thread.message.delta':
                    if hasattr(event, 'data') and hasattr(event.data, 'delta'):
                        delta = event.data.delta
                        if hasattr(delta, 'content') and delta.content:
                            for content_block in delta.content:
                                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                                    new_text += content_block.text.value
                                elif hasattr(content_block, 'text') and isinstance(content_block.text, str):
                                    new_text += content_block.text
                
                # Alternative event structure
                elif hasattr(event, 'data') and hasattr(event.data, 'delta'):
                    delta = event.data.delta
                    if hasattr(delta, 'content') and delta.content:
                        for block in delta.content:
                            if hasattr(block, 'text') and block.text:
                                if hasattr(block.text, 'value'):
                                    new_text += block.text.value
                                else:
                                    new_text += str(block.text)
                    elif hasattr(delta, 'text'):
                        if hasattr(delta.text, 'value'):
                            new_text += delta.text.value
                        else:
                            new_text += str(delta.text)
                
                # Handle completion-style events (fallback)
                elif hasattr(event, 'choices'):
                    for choice in event.choices:
                        if hasattr(choice, 'delta') and hasattr(choice.delta, 'content') and choice.delta.content:
                            new_text += choice.delta.content

                # If we got new text, add it and notify callbacks
                if new_text:
                    full_response += new_text
                    logger.info(f"Added text chunk: '{new_text[:50]}...' (total length: {len(full_response)})")
                    
                    # Call streaming callback to update UI live
                    if streaming_callback:
                        streaming_callback(full_response)
                    
                    # Update progress based on content length
                    if progress_callback:
                        progress_pct = min(95, 60 + len(full_response) // 100)
                        progress_callback(f"🧠 AI streaming... ({len(full_response)} chars)", progress_pct)

            if progress_callback:
                progress_callback("✅ Analysis complete!", 100)

            logger.info(f"Streaming completed. Total events: {event_count}, Response length: {len(full_response)}")
            return full_response

        except Exception as e:
            logger.error(f"Error running analysis (streaming): {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Error running analysis: {str(e)}"
    
    def analyze_property_data(self, df, kpi_summary, progress_callback=None, streaming_callback=None, format_name="t12_monthly_financial", model_config=None):
        """Complete property analysis workflow with format-specific instructions"""
        try:
            # Default model configuration
            if model_config is None:
                model_config = {"model_selection": "gpt-4o"}
            
            # Create assistant if not exists
            if not self.assistant_id:
                if progress_callback:
                    progress_callback("🤖 Creating AI assistant...", 10)
                self.create_assistant(format_name, model_config["model_selection"])
            
            # Create thread with data
            if progress_callback:
                progress_callback("📤 Uploading data to OpenAI...", 30)
            self.create_thread_with_data(df, kpi_summary, format_name)
            
            # Run analysis with streaming
            if progress_callback:
                progress_callback("🧠 Starting AI analysis...", 50)
            result = self.run_analysis(progress_callback, streaming_callback)
            
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

def analyze_with_assistants_api(df, kpi_summary, api_key=None, progress_callback=None, streaming_callback=None, format_name="t12_monthly_financial", model_config=None):
    """Convenience function for property analysis using Assistants API"""
    analyzer = PropertyAssistantAnalyzer(api_key)
    try:
        return analyzer.analyze_property_data(df, kpi_summary, progress_callback, streaming_callback, format_name, model_config)
    finally:
        analyzer.cleanup()
