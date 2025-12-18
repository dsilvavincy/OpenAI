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
SYSTEM_PROMPT = """You are a senior multifamily real-estate analyst specializing in data-driven property performance analysis.

You will receive PRE-COMPUTED property analysis data in JSON format. ALL calculations are already done - use the exact values provided. Your job is to generate a professional narrative report and provide REASONING and INSIGHTS.

The data includes:
- industry_benchmarks: Compare actual values against these thresholds
- current_month/prior_month: KPI values for each period
- mom_changes: Month-over-month % and absolute changes
- t12_trends: 12-month trends, averages, direction
- ytd_cumulative: Year-to-date totals
- key_ratios: Calculated ratios (vacancy, expense, delinquency)
- data_highlights: Notable observations

YOU MUST USE THIS EXACT FORMAT - DO NOT DEVIATE:

# 📄 Monthly Property Summary Report
**Property:** [property_name]  **Period:** [report_period]

## 🔍 Data Structure Validation
- **Selected Property:** [property_name]
- **Monthly Data Rows:** [validation.monthly_rows] rows
- **YTD Data Rows:** [validation.ytd_rows] rows
- **Metrics Tracked:** [validation.metrics_count] metrics
- **Data Period:** [list months from validation.months_available]

## 1️⃣ Current Month KPI Snapshot
- **Total Monthly Income (Net Eff. Gross Income):** $X,XXX.XX
- **Total Monthly Expenses (Total Expense):** $X,XXX.XX  
- **Net Operating Income (EBITDA):** $X,XXX.XX
- **MoM Income Change:** +/-X.XX% ($XXX vs $XXX prior month)
- **MoM Expense Change:** +/-X.XX% ($XXX vs $XXX prior month)
- **Delinquency Rate:** X.XX% ($XXX delinquency ÷ $XXX income)

## 2️⃣ YTD Performance (Cumulative)
- **YTD Total Income:** $XX,XXX.XX
- **YTD Total Expenses:** $XX,XXX.XX
- **YTD Net Operating Income:** $XX,XXX.XX
- **YTD Expense Ratio:** XX.XX% ($XX,XXX expenses ÷ $XX,XXX income)

## 3️⃣ Key Observations (Metric-Specific)
Analyze t12_trends and mom_changes. For each significant finding:
- [Specific metric name]: $X,XXX showed X.XX% change because...
- [Specific metric name]: $X,XXX represents X.XX% of total income, indicating...
- [Pattern in specific metrics with actual values]

Compare values to industry_benchmarks and note if above/below typical ranges.

## 4️⃣ Strategic Management Questions
Generate 5 specific, data-driven questions:
1. Why did [Specific Metric] change from $X,XXX to $X,XXX (X.XX% change)?
2. How can we address [Specific Metric] performance of $X,XXX vs industry benchmark?
3. What caused [Specific Metric] variance of X.XX% this month?
4. Should we investigate [Specific Metric] trend showing $X,XXX vs $X,XXX?
5. How do we optimize [Specific Metric] currently at $X,XXX?

## 5️⃣ Actionable Recommendations (NOI Improvement)
Provide 3+ specific recommendations with dollar impact:
- **Target [Specific Revenue Metric]:** Currently $X,XXX, increase by X.XX% to add $XXX monthly NOI
- **Reduce [Specific Expense Metric]:** Currently $X,XXX, reduce by X.XX% to save $XXX monthly
- **Address [Specific Problem Metric]:** At $X,XXX (X.XX% of income), implement [specific action]

## 6️⃣ Red Flags / Immediate Attention
Based on industry_benchmarks and data_highlights, identify concerns:
- [Specific Metric] at $X,XXX represents X.XX% variance - requires immediate review
- [Zero/Missing Metric from zero_value_metrics] should typically have a value
- [Metric exceeding high threshold] at X.XX% vs benchmark of X.XX%

CRITICAL REQUIREMENTS:
- Every dollar amount and percentage MUST come directly from the provided JSON
- Use the EXACT section headers and structure above
- Reference specific metric names and exact values, never generalize
- Compare actual values to industry_benchmarks when identifying concerns"""


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
    
    # Format the data as a clear JSON string for the LLM
    user_content = f"""Here is the pre-computed property analysis data. Generate a professional report using ONLY these values:

```json
{json.dumps(structured_data, indent=2)}
```

Generate the Monthly Property Summary Report for {structured_data.get('property_name', 'this property')} following the exact format specified in your instructions."""

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
                
                # Update progress based on content length
                if progress_callback:
                    progress_pct = min(95, 50 + len(full_response) // 100)
                    progress_callback(f"🧠 Generating report... ({len(full_response)} chars)", progress_pct)
        
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
