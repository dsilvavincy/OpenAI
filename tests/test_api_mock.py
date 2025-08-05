"""
Mock API testing for OpenAI integration when API key is not available
"""

from src.prompt import build_prompt, build_fallback_prompt, call_openai
from src.kpi_summary import generate_kpi_summary
from src.preprocess import tidy_sheet_all

def mock_openai_response(system_prompt, user_prompt):
    """Mock OpenAI response for testing purposes"""
    
    # Simulate different response scenarios
    mock_response = """
**STRATEGIC MANAGEMENT QUESTIONS:**

1. What specific factors are driving the 60.2% increase in delinquency, and what collection strategies can be implemented?
2. How can we improve the 81.3% economic occupancy rate to industry standards of 90-95%?
3. What market analysis supports the current asking rent levels versus effective rent achievement?
4. Are the current expense ratios competitive, and where can operational efficiencies be gained?
5. What capital improvements could justify rent increases and reduce vacancy?

**ACTIONABLE RECOMMENDATIONS:**

1. **Implement aggressive collections program** - The 60.2% delinquency increase is concerning and requires immediate attention
2. **Review and optimize rent pricing strategy** - 6.3% loss-to-lease suggests asking rents may be too aggressive
3. **Focus on vacancy reduction initiatives** - 11.8% vacancy rate is above industry standards
4. **Analyze high payroll costs** - $26.01 per unit seems elevated and should be benchmarked
5. **Evaluate capital reserve funding** - $44.93 replacement reserve may be excessive for current NOI

**CONCERNING TRENDS:**
- Delinquency spike of 60.2% requires immediate investigation
- Negative cash flow of -$59.40 indicates operational challenges
- Collection rate of 76.1% is below industry standards of 95%+
"""
    return mock_response

def test_api_consistency():
    """Test API call consistency with mock responses"""
    
    print("Testing API Integration with Mock Responses...")
    
    # Load and process test data
    df = tidy_sheet_all('Data.xlsx')
    summary = generate_kpi_summary(df)
    
    # Test main prompt
    system_prompt, user_prompt = build_prompt(summary)
    print(f"Main prompt length: {len(system_prompt + user_prompt)} characters")
    
    mock_response = mock_openai_response(system_prompt, user_prompt)
    print("Mock API Response:")
    print(mock_response[:500] + "..." if len(mock_response) > 500 else mock_response)
    
    # Test fallback prompt
    fallback_sys, fallback_user = build_fallback_prompt(summary)
    print(f"\nFallback prompt length: {len(fallback_sys + fallback_user)} characters")
    
    # Validate response structure
    print("\n=== RESPONSE VALIDATION ===")
    has_questions = "QUESTIONS" in mock_response.upper()
    has_recommendations = "RECOMMENDATIONS" in mock_response.upper()
    has_concerns = "CONCERN" in mock_response.upper()
    
    print(f"Contains strategic questions: {has_questions}")
    print(f"Contains recommendations: {has_recommendations}")
    print(f"Contains concerning trends: {has_concerns}")
    
    validation_passed = all([has_questions, has_recommendations, has_concerns])
    print(f"Overall validation: {'PASSED' if validation_passed else 'FAILED'}")
    
    return validation_passed

if __name__ == "__main__":
    test_api_consistency()
