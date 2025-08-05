"""
Prompt construction and OpenAI API call
"""

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_prompt(kpi_summary):
    """Build standardized prompt for T12 property analysis"""
    
    system_instructions = """You are a senior real estate investment analyst specializing in multifamily property performance analysis. You have extensive experience in reviewing T12 (Trailing 12-month) financial statements and identifying key trends, risks, and opportunities.

Your task is to analyze the provided T12 property financial data and generate actionable insights for property management and investment decisions.

ANALYSIS FRAMEWORK:
1. FINANCIAL PERFORMANCE: Assess revenue trends, collection rates, and income stability
2. OPERATIONAL EFFICIENCY: Evaluate vacancy rates, concessions, and delinquency patterns  
3. MARKET POSITIONING: Analyze asking rents vs. effective rents and loss-to-lease
4. RISK ASSESSMENT: Identify red flags and potential concerns
5. IMPROVEMENT OPPORTUNITIES: Suggest specific actionable recommendations

OUTPUT REQUIREMENTS:
- Generate exactly 5 strategic management questions that should be investigated
- Provide 3-5 specific actionable recommendations to improve NOI
- Highlight any concerning trends that require immediate attention
- Include industry context and benchmarking where relevant

Be concise, specific, and focus on actionable insights that can drive real business decisions."""

    user_content = f"""Please analyze the following T12 property financial data:

{kpi_summary}

Based on this data, provide your analysis following the framework outlined in your instructions."""

    return system_instructions, user_content

def build_fallback_prompt(kpi_summary):
    """Build simplified fallback prompt for edge cases or API issues"""
    
    system_instructions = """You are a real estate analyst. Analyze the provided T12 data and provide:
1. Key performance observations
2. Top 3 concerns or red flags
3. Top 3 recommendations for improvement

Keep responses concise and actionable."""

    user_content = f"""Analyze this T12 data and provide key insights:

{kpi_summary}"""

    return system_instructions, user_content

def build_minimal_prompt(data_snippet):
    """Build minimal prompt for severely limited data or emergency fallback"""
    
    system_instructions = """Provide basic real estate financial analysis. Focus on actionable insights."""
    
    user_content = f"""Review this financial data and suggest improvements:

{data_snippet}"""
    
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

def validate_response(response):
    """Validate OpenAI API response for completeness and structure"""
    if not response or len(response.strip()) < 50:
        return False, "Response too short or empty"
    
    # Check for key sections
    response_upper = response.upper()
    has_questions = any(word in response_upper for word in ["QUESTION", "INVESTIGATE", "WHAT", "HOW", "WHY"])
    has_recommendations = any(word in response_upper for word in ["RECOMMEND", "SUGGEST", "IMPROVE", "ACTION"])
    has_analysis = any(word in response_upper for word in ["TREND", "PERFORMANCE", "CONCERN", "RISK"])
    
    if not (has_questions and has_recommendations and has_analysis):
        return False, "Response missing key sections (questions, recommendations, or analysis)"
    
    return True, "Response validation passed"
