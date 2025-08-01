"""
Prompt construction and OpenAI API call
"""

import os
import openai
from dotenv import load_dotenv

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

def call_openai(system_prompt, user_prompt, api_key=None):
    """Call OpenAI API with the constructed prompts"""
    try:
        # Load .env file if present
        load_dotenv()
        # Use provided API key or environment variable
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            return "Error: OpenAI API key not provided. Please set it in a .env file or provide it in the UI."
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        return response.choices[0].message['content']
    except openai.error.APIError as e:
        return f"OpenAI API Error: {str(e)}"
    except openai.error.AuthenticationError:
        return "Error: Invalid OpenAI API key. Please check your API key."
    except openai.error.RateLimitError:
        return "Error: OpenAI API rate limit exceeded. Please try again later."
    except Exception as e:
        return f"Unexpected error calling OpenAI API: {str(e)}"
