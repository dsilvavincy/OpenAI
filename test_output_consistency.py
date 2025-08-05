"""
Test output consistency across multiple runs
"""

from src.output_quality import post_process_output, QualityScorer
from src.prompt import build_prompt
from src.kpi_summary import generate_kpi_summary
from src.preprocess import tidy_sheet_all

def test_output_consistency():
    """Test output consistency with same input data"""
    
    print("Testing Output Consistency Across Multiple Runs...")
    
    # Load test data
    df = tidy_sheet_all('Data.xlsx')
    summary = generate_kpi_summary(df)
    
    # Simulate multiple AI responses (since we can't make real API calls without key)
    mock_responses = [
        """**STRATEGIC MANAGEMENT QUESTIONS:**
1. What factors are driving the 60.2% increase in delinquency?
2. How can we improve the 81.3% economic occupancy rate?
3. What market analysis supports current rent levels?

**ACTIONABLE RECOMMENDATIONS:**
1. Implement aggressive collections program for delinquency
2. Review and optimize rent pricing strategy  
3. Focus on vacancy reduction initiatives
4. Analyze high payroll costs for optimization

**CONCERNING TRENDS:**
- Delinquency spike of 60.2% requires immediate attention
- Negative cash flow indicates operational challenges
- Collection rate below industry standards""",

        """**STRATEGIC MANAGEMENT QUESTIONS:**
1. What specific collection strategies can address the delinquency increase?
2. How can occupancy be improved from 81.3% to industry standards?
3. What operational efficiencies can be gained to improve NOI?

**ACTIONABLE RECOMMENDATIONS:**
1. Implement enhanced tenant screening and collections
2. Evaluate rent pricing competitiveness in the market
3. Reduce vacancy through improved marketing and incentives
4. Review expense ratios and identify cost savings

**CONCERNING TRENDS:**
- Significant delinquency increase needs immediate intervention
- Cash flow challenges require operational review
- Economic occupancy below market expectations""",

        """**STRATEGIC MANAGEMENT QUESTIONS:**
1. What root causes explain the dramatic delinquency rise?
2. How can we achieve 90%+ occupancy rates consistently?
3. What capital improvements could justify rent increases?

**ACTIONABLE RECOMMENDATIONS:**
1. Deploy comprehensive collections and retention program
2. Conduct market study to optimize rent positioning
3. Implement vacancy reduction through targeted marketing
4. Analyze and reduce operational cost structure

**CONCERNING TRENDS:**
- Delinquency trends indicate collection process failures
- Operating cash flow concerns require immediate attention
- Performance metrics below industry benchmarks"""
    ]
    
    # Process each response
    results = []
    scorer = QualityScorer()
    
    for i, response in enumerate(mock_responses, 1):
        processed = post_process_output(response, {"name": f"Test Property Run {i}"})
        results.append(processed)
        
        print(f"\n=== RUN {i} ===")
        print(f"Quality Score: {processed['quality_metrics']['overall_score']}")
        print(f"Quality Level: {processed['quality_metrics']['quality_level']}")
        print(f"Questions Count: {len(processed['analysis']['strategic_questions'])}")
        print(f"Recommendations Count: {len(processed['analysis']['recommendations'])}")
        print(f"Concerns Count: {len(processed['analysis']['concerning_trends'])}")
    
    # Analyze consistency
    print("\n=== CONSISTENCY ANALYSIS ===")
    
    scores = [r['quality_metrics']['overall_score'] for r in results]
    question_counts = [len(r['analysis']['strategic_questions']) for r in results]
    rec_counts = [len(r['analysis']['recommendations']) for r in results]
    
    print(f"Quality Score Range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"Score Standard Deviation: {(max(scores) - min(scores)):.1f}")
    print(f"Question Count Range: {min(question_counts)} - {max(question_counts)}")
    print(f"Recommendation Count Range: {min(rec_counts)} - {max(rec_counts)}")
    
    # Consistency verdict
    score_consistency = (max(scores) - min(scores)) < 15  # Within 15 points
    count_consistency = (max(question_counts) - min(question_counts)) <= 1  # Within 1 item
    
    overall_consistency = score_consistency and count_consistency
    
    print(f"\nConsistency Assessment: {'PASSED' if overall_consistency else 'NEEDS IMPROVEMENT'}")
    
    return overall_consistency

if __name__ == "__main__":
    test_output_consistency()
