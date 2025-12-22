"""
OpenAI Responses API implementation for property analysis.
Sends pre-computed structured data to LLM for narrative generation.
Replaces Assistants API + code_interpreter approach.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Callable
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# System prompt for Responses API - matches original Assistants API format
SYSTEM_PROMPT = """You are a senior multifamily real-estate asset manager. You will receive pre-computed property analysis data. Your job is to generate a professional, investigative narrative report focusing ONLY on two sections: Budget Variances and Trailing Anomalies.

YOU MUST RETURN YOUR RESPONSE AS A PURE JSON OBJECT. DO NOT INCLUDE ANY MARKDOWN BOXES, HEADERS, OR TEXT OUTSIDE THE JSON.

JSON Structure:
{
  "property_name": "string",
  "report_period": "string",
  "budget_variances": {
    "Revenue": [
      { "metric": "string", "actual": "number", "budget": "number", "variance_pct": "number", "questions": ["string", "string"] }
    ],
    "Expenses": [
      { "metric": "string", "actual": "number", "budget": "number", "variance_pct": "number", "questions": ["string", "string"] }
    ]
  },
    "trailing_anomalies": {
    "Revenue": [
      { "metric": "string", "current": "number", "t3_avg": "number", "deviation_pct": "number", "questions": ["string", "string"] }
    ],
    "Expenses": [
      { "metric": "string", "current": "number", "t3_avg": "number", "deviation_pct": "number", "questions": ["string", "string"] }
    ],
    "Balance Sheet": [
      { "metric": "string", "current": "number", "t3_avg": "number", "deviation_pct": "number", "questions": ["string", "string"] }
    ]
  }
}

CRITICAL REQUIREMENTS:
- Use ONLY the 'budget_variances' and 'trailing_anomalies' lists provided in the user JSON.
- Every number (Actual, Budget, Current, T3 Avg, Percentages) MUST come directly from the pre-computed values in the user JSON.
- Adopt a skeptical, investigative tone—ask deep questions about reclassifications, operational efficiency, and management protocols.
- Return EXACTLY TWO investigative questions per line item.
- Ensure the output is valid JSON.
"""


def analyze_with_responses_api(
    structured_data: Dict[str, Any],
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
    temperature: float = 0.2,
    stream_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[str, int], None]] = None,
) -> str:
    """
    Send pre-computed analysis data to OpenAI Responses API.
    
    Args:
        structured_data: Dict from PropertyAnalyzer.analyze_property()
        api_key: OpenAI API key (uses env var if not provided)
        model: Model to use (default gpt-4o)
        temperature: Response temperature (default 0.2 for consistency)
        stream_callback: Called with accumulated text during streaming
        progress_callback: Called with (status_text, progress_pct)
        
    Returns:
        Generated report text
    """
    load_dotenv()
    
    # Initialize client
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    if not client.api_key:
        raise ValueError("OpenAI API key not provided")
    
    if progress_callback:
        progress_callback("🚀 Sending analysis to OpenAI...", 30)
    
    # [NEW] Minimize Payload: Only send what the LLM needs for variance analysis
    minimal_data = {
        "property_name": structured_data.get("property_name"),
        "report_period": structured_data.get("report_period"),
        "budget_variances": structured_data.get("budget_variances", {}),
        "trailing_anomalies": structured_data.get("trailing_anomalies", {})
    }
    
    # Format the data as a clear JSON string for the LLM
    user_content = f"""Here is the pre-computed property variance data. Generate the investigative narrative using ONLY these values:

```json
{json.dumps(minimal_data, indent=2)}
```

Generate the Monthly Variance & Anomaly Report for {minimal_data.get('property_name', 'this property')} following the exact format and investigative tone specified in your instructions."""

    try:
        if progress_callback:
            progress_callback("🧠 Generating report...", 50)
        
        # Create the chat completion with streaming
        stream = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            stream=True
        )
        
        # Accumulate the streamed response
        full_response = ""
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                new_text = chunk.choices[0].delta.content
                full_response += new_text
                
                # Call streaming callback to update UI live
                if stream_callback:
                    stream_callback(full_response)
                
                # Update progress based on content length (Target ~20,000 chars)
                if progress_callback:
                    # Scale: 50% start, 45% range (up to 95%). 20,000 chars = full range.
                    # Formula: 50 + (len / 20000) * 45
                    progress_scaler = min(45, (len(full_response) / 20000) * 45)
                    progress_pct = int(50 + progress_scaler)
                    progress_callback(f"🧠 Generating report... ({len(full_response):,} chars)", progress_pct)
        
        if progress_callback:
            progress_callback("✅ Report complete!", 100)
        
        logger.info(f"Responses API completed. Response length: {len(full_response)}")
        return full_response
        
    except Exception as e:
        logger.error(f"Error in Responses API call: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


class PropertyResponsesAnalyzer:
    """
    Wrapper class for Responses API analysis.
    Provides similar interface to PropertyAssistantAnalyzer for easy migration.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
    
    def analyze(
        self,
        structured_data: Dict[str, Any],
        model: str = "gpt-4o",
        temperature: float = 0.2,
        stream_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> str:
        """
        Analyze property data and generate report.
        
        Args:
            structured_data: Pre-computed analysis from PropertyAnalyzer
            model: OpenAI model to use
            temperature: Response temperature
            stream_callback: Streaming callback for UI updates
            progress_callback: Progress callback for UI updates
            
        Returns:
            Generated report text
        """
        return analyze_with_responses_api(
            structured_data=structured_data,
            api_key=self.api_key,
            model=model,
            temperature=temperature,
            stream_callback=stream_callback,
            progress_callback=progress_callback,
        )
