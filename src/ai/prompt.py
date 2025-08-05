"""
Prompt construction and OpenAI API call
"""

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from .prompt_manager import prompt_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_prompt(kpi_summary, format_name="t12_monthly_financial"):
    """Build standardized prompt for property analysis based on format type"""
    
    # Use the dynamic prompt manager to build format-specific prompts
    system_instructions, user_content = prompt_manager.build_prompts(
        format_name=format_name,
        data_content=kpi_summary,
        analysis_type="standard"
    )
    
    return system_instructions, user_content

def build_fallback_prompt(kpi_summary, format_name="t12_monthly_financial"):
    """Build simplified fallback prompt for edge cases or API issues"""
    
    # Use the dynamic prompt manager for fallback prompts
    system_instructions, user_content = prompt_manager.build_prompts(
        format_name=format_name,
        data_content=kpi_summary,
        analysis_type="fallback"
    )
    
    return system_instructions, user_content

def build_minimal_prompt(data_snippet, format_name="t12_monthly_financial"):
    """Build minimal prompt for severely limited data or emergency fallback"""
    
    # Use the dynamic prompt manager for minimal prompts
    system_instructions, user_content = prompt_manager.build_prompts(
        format_name=format_name,
        data_content=data_snippet,
        analysis_type="minimal"
    )
    
    return system_instructions, user_content

def call_openai(system_prompt, user_prompt, api_key=None):
    """Call OpenAI API with the constructed prompts"""
    try:
        # Load .env file if present
        load_dotenv()
        
        # Initialize OpenAI client
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
        if not client.api_key:
            logger.error("OpenAI API key not provided")
            return "Error: OpenAI API key not provided. Please set it in a .env file or provide it in the UI."
        
        logger.info(f"Making OpenAI API call with prompt length: {len(system_prompt + user_prompt)} characters")
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        
        result = response.choices[0].message.content
        logger.info(f"OpenAI API call successful, response length: {len(result)} characters")
        return result
        
    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "api key" in error_msg:
            logger.error("OpenAI API authentication error")
            return "Error: Invalid OpenAI API key. Please check your API key."
        elif "rate" in error_msg or "limit" in error_msg:
            logger.warning("OpenAI API rate limit exceeded")
            return "Error: OpenAI API rate limit exceeded. Please try again later."
        else:
            logger.error(f"Unexpected OpenAI API error: {str(e)}")
            return f"Error calling OpenAI API: {str(e)}"

def validate_response(response, analysis_type="standard", format_name="t12_monthly_financial"):
    """Validate OpenAI API response for completeness and structure"""
    if not response or len(response.strip()) < 50:
        return False, "Response too short or empty"
    
    # Get format-specific validation keywords
    validation_keywords = prompt_manager.get_validation_keywords(format_name, analysis_type)
    
    # More flexible validation for Enhanced Analysis (Assistants API)
    if analysis_type == "enhanced" or analysis_type == "assistants":
        # Check for required content indicators
        response_upper = response.upper()
        required_content = validation_keywords.get("required_content", [])
        min_length = validation_keywords.get("min_length", 100)
        
        has_content_indicators = any(word.upper() in response_upper for word in required_content)
        
        if has_content_indicators and len(response.strip()) > min_length:
            return True, "Enhanced analysis validation passed"
        else:
            return False, f"Enhanced analysis lacks sufficient relevant content for {format_name} format"
    
    # Enhanced validation for structured responses
    response_upper = response.upper()
    
    # Check for structured sections (numbered headers with emojis)
    structured_sections = [
        "CURRENT MONTH KPI SNAPSHOT", "YTD PERFORMANCE", "KEY OBSERVATIONS", 
        "STRATEGIC MANAGEMENT QUESTIONS", "ACTIONABLE RECOMMENDATIONS", "RED FLAGS"
    ]
    section_count = sum(1 for section in structured_sections if section in response_upper)
    
    # If we have structured sections, validate those
    if section_count >= 4:  # At least 4 of the 6 main sections
        # Check for key financial content
        financial_indicators = ["$", "%", "INCOME", "EXPENSE", "NOI", "EBITDA"]
        has_financial_content = sum(1 for indicator in financial_indicators if indicator in response_upper) >= 3
        
        if has_financial_content:
            return True, f"Structured response validation passed ({section_count}/6 sections found)"
    
    # Fallback to standard validation using format-specific keywords
    questions_keywords = validation_keywords.get("questions", ["question", "what", "how", "why"])
    recommendations_keywords = validation_keywords.get("recommendations", ["recommend", "suggest", "improve", "actionable"])
    analysis_keywords = validation_keywords.get("analysis", ["trend", "performance", "concern", "observations", "kpi"])
    
    has_questions = any(word.upper() in response_upper for word in questions_keywords)
    has_recommendations = any(word.upper() in response_upper for word in recommendations_keywords)
    has_analysis = any(word.upper() in response_upper for word in analysis_keywords)
    
    if not (has_questions and has_recommendations and has_analysis):
        return False, f"Response missing key sections for {format_name} format (questions, recommendations, or analysis)"
    
    return True, "Response validation passed"
