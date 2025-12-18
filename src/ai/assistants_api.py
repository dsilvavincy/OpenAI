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
import streamlit as st

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
        
    def get_assistant_instructions(self, format_name="t12_monthly_financial", selected_property: str | None = None):
        """Get format-specific assistant instructions. Keep property generic to enable reuse across selections."""
        # Do not inject a specific property into assistant instructions; rely on the user message to specify it
        instructions = prompt_manager.build_system_instructions(format_name, "assistants")
        return instructions
        
    def create_assistant(self, format_name="t12_monthly_financial", model="gpt-4o", selected_property: str | None = None):
        """Create a specialized property analysis assistant for the given format"""
        try:
            instructions = self.get_assistant_instructions(format_name, selected_property)
            assistant = self.client.beta.assistants.create(
                name=f"Property Analysis Expert - {format_name.upper()}",
                instructions=instructions,
                model=model,
                tools=[{"type": "code_interpreter"}]
            )
            
            self.assistant_id = assistant.id
            logger.info(f"Created assistant with ID: {self.assistant_id} for format: {format_name} using model: {model}")
            return assistant
            
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            raise
    
    def upload_dataframe(self, df, label=None):
        """Upload DataFrame to OpenAI as CSV file, optionally with a label for prompt."""
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
            return uploaded_file.id, label or temp_file.name
        except Exception as e:
            logger.error(f"Error uploading DataFrame: {str(e)}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def create_thread_with_data(self, monthly_df, ytd_df, kpi_summary, format_name="t12_monthly_financial", selected_property: str | None = None):
        """Create a conversation thread with both monthly and YTD data and KPI summary"""
        try:
            # Upload both DataFrames (or reuse if available in session_state)
            file_id_monthly = st.session_state.get('assist_file_id_monthly')
            file_id_ytd = st.session_state.get('assist_file_id_ytd')
            label_monthly, label_ytd = "Monthly Data", "YTD Data"
            if not file_id_monthly:
                file_id_monthly, label_monthly = self.upload_dataframe(monthly_df, label="Monthly Data")
                st.session_state['assist_file_id_monthly'] = file_id_monthly
            if not file_id_ytd:
                file_id_ytd, label_ytd = self.upload_dataframe(ytd_df, label="YTD Data")
                st.session_state['assist_file_id_ytd'] = file_id_ytd
            # Minimal user message; rely on system instructions for all details
            format_upper = format_name.upper().replace("_", " ")
            property_clause = f" for property '{selected_property}'" if selected_property else ""
            prompt_content = (
                f"Give me the report{property_clause}."
            )
            # Log the exact prompt being sent
            logger.info("=== ENHANCED ANALYSIS PROMPT ===")
            logger.info(f"Assistant Instructions (system): {self.get_assistant_instructions(format_name, selected_property)}")
            logger.info(f"User Message Content:\n{prompt_content}")
            logger.info(f"Attached File IDs: {file_id_monthly}, {file_id_ytd}")
            logger.info("================================")
            # Create thread with initial message using both attachments
            thread = self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_content,
                        "attachments": [
                            {
                                "file_id": file_id_monthly,
                                "tools": [{"type": "code_interpreter"}]
                            },
                            {
                                "file_id": file_id_ytd,
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

    def add_message_to_existing_thread(self, prompt_content: str):
        """Add a new user message to the existing thread, re-attaching existing files for the code interpreter."""
        if not self.thread_id:
            raise ValueError("No existing thread to add a message to")
        file_id_monthly = st.session_state.get('assist_file_id_monthly')
        file_id_ytd = st.session_state.get('assist_file_id_ytd')
        attachments = []
        if file_id_monthly:
            attachments.append({"file_id": file_id_monthly, "tools": [{"type": "code_interpreter"}]})
        if file_id_ytd:
            attachments.append({"file_id": file_id_ytd, "tools": [{"type": "code_interpreter"}]})
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=prompt_content,
            attachments=attachments if attachments else None
        )
    
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
    
    def analyze_property_data(self, monthly_df, ytd_df, kpi_summary, progress_callback=None, streaming_callback=None, format_name="t12_monthly_financial", model_config=None, selected_property: str | None = None):
        """Complete property analysis workflow with format-specific instructions, using both monthly and YTD data"""
        try:
            if model_config is None:
                model_config = {"model_selection": "gpt-4o"}
            if not self.assistant_id:
                if progress_callback:
                    progress_callback("🤖 Creating AI assistant...", 10)
                self.create_assistant(format_name, model_config["model_selection"], selected_property)
            if progress_callback:
                progress_callback("📤 Uploading data to OpenAI...", 30)
            self.create_thread_with_data(monthly_df, ytd_df, kpi_summary, format_name, selected_property)
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

def analyze_with_assistants_api(monthly_df, ytd_df, kpi_summary, api_key=None, progress_callback=None, streaming_callback=None, format_name="t12_monthly_financial", model_config=None, selected_property: str | None = None, reuse_session: bool = True):
    """Convenience function for property analysis using Assistants API with both monthly and YTD data"""
    analyzer = PropertyAssistantAnalyzer(api_key)
    try:
        # Reuse assistant if available and model matches
        requested_model = (model_config or {}).get("model_selection", "gpt-4o")
        if reuse_session:
            existing_assistant = st.session_state.get('assist_assistant_id')
            existing_thread = st.session_state.get('assist_thread_id')
            stored_model = st.session_state.get('assist_model_name')
            
            # Only reuse if model matches
            if existing_assistant and stored_model == requested_model:
                analyzer.assistant_id = existing_assistant
                if existing_thread:
                    analyzer.thread_id = existing_thread
            else:
                # Model changed or no assistant exists - reset
                if existing_assistant:
                    logger.info(f"Switching models: {stored_model} -> {requested_model}. Creating new assistant.")
                reuse_session = False  # Force new session creation logic below

        # Ensure assistant exists
        if not analyzer.assistant_id:
            if progress_callback:
                progress_callback(f"🤖 Creating AI assistant ({requested_model})...", 10)
            assistant = analyzer.create_assistant(format_name, requested_model, selected_property)
            st.session_state['assist_assistant_id'] = assistant.id
            st.session_state['assist_model_name'] = requested_model

        # Create or reuse thread
        format_upper = format_name.upper().replace("_", " ")
        property_clause = f" for property '{selected_property}'" if selected_property else ""
        prompt_content = f"Give me the report{property_clause}."

        if not analyzer.thread_id:
            if progress_callback:
                progress_callback("📤 Preparing data and starting thread...", 30)
            thread = analyzer.create_thread_with_data(monthly_df, ytd_df, kpi_summary, format_name, selected_property)
            st.session_state['assist_thread_id'] = thread.id
        else:
            if progress_callback:
                progress_callback("✉️ Adding message to existing thread...", 40)
            analyzer.add_message_to_existing_thread(prompt_content)

        if progress_callback:
            progress_callback("🧠 Starting AI analysis...", 50)
        result = analyzer.run_analysis(progress_callback, streaming_callback)
        return result
    finally:
        # Do not cleanup if reusing session; otherwise, cleanup resources
        if not reuse_session:
            analyzer.cleanup()
