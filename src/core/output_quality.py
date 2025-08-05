"""
Output standardization and quality control for AI-generated T12 insights
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class OutputFormatter:
    """Standardize and format AI-generated insights"""
    
    def __init__(self):
        self.standard_sections = [
            "STRATEGIC MANAGEMENT QUESTIONS",
            "ACTIONABLE RECOMMENDATIONS", 
            "CONCERNING TRENDS",
            "KEY PERFORMANCE INSIGHTS",
            "RISK ASSESSMENT"
        ]
    
    def format_standard_output(self, raw_response: str, property_info: Dict = None) -> Dict:
        """
        Format raw AI response into standardized structure
        """
        formatted_output = {
            "timestamp": datetime.now().isoformat(),
            "property_info": property_info or {},
            "analysis": {
                "strategic_questions": [],
                "recommendations": [],
                "concerning_trends": [],
                "key_insights": [],
                "risk_assessment": []
            },
            "metadata": {
                "response_length": len(raw_response),
                "processing_timestamp": datetime.now().isoformat()
            }
        }
        
        # Extract sections using pattern matching
        sections = self._extract_sections(raw_response)
        
        # Map sections to standardized format
        formatted_output["analysis"]["strategic_questions"] = sections.get("questions", [])
        formatted_output["analysis"]["recommendations"] = sections.get("recommendations", [])
        formatted_output["analysis"]["concerning_trends"] = sections.get("concerns", [])
        formatted_output["analysis"]["key_insights"] = sections.get("insights", [])
        formatted_output["analysis"]["risk_assessment"] = sections.get("risks", [])
        
        return formatted_output
    
    def _extract_sections(self, text: str) -> Dict[str, List[str]]:
        """Extract structured sections from AI response"""
        sections = {
            "questions": [],
            "recommendations": [],
            "concerns": [],
            "insights": [],
            "risks": []
        }
        
        # Split text into lines for processing
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers (comprehensive pattern matching)
            line_upper = line.upper()
            
            # ONLY detect section headers - lines that start with ## or contain emoji headers
            if line.startswith('##') or any(emoji in line for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']):
                # Strategic Questions - Enhanced detection
                if ('4️⃣' in line or 
                    ('QUESTION' in line_upper and ('STRATEGIC' in line_upper or 'MANAGEMENT' in line_upper))):
                    current_section = 'questions'
                    continue
                # Recommendations - Enhanced detection  
                elif ('5️⃣' in line or 
                      ('RECOMMENDATION' in line_upper or 'ACTIONABLE' in line_upper)):
                    current_section = 'recommendations'
                    continue
                # Concerning Trends / Red Flags - Enhanced detection
                elif ('6️⃣' in line or '⚠️' in line or
                      ('CONCERN' in line_upper or 'TREND' in line_upper or 'RED FLAG' in line_upper or 
                       'IMMEDIATE ATTENTION' in line_upper or 'RED FLAGS' in line_upper)):
                    current_section = 'concerns'
                    continue
                # Key Observations
                elif ('3️⃣' in line or
                      ('OBSERVATION' in line_upper or ('KEY' in line_upper and 'OBSERVATION' in line_upper))):
                    current_section = 'insights'
                    continue
                # Other section headers we don't recognize - reset section
                else:
                    current_section = None
                    continue
            
            # Extract list items (handle both numbered lists and bullet points)
            if current_section:
                # Check for numbered items (1., 2., etc.) OR bullet points (-, *, •)
                if re.match(r'^\d+\.\s+', line) or re.match(r'^[-\*\•]\s+', line):
                    # Clean the line - remove prefixes and extra spaces
                    cleaned = re.sub(r'^\d+\.\s*', '', line).strip()  # Remove "1. " prefix
                    cleaned = re.sub(r'^[-\*\•]\s*', '', cleaned).strip()  # Remove bullet points
                    
                    # Further clean markdown formatting (remove **bold** markers)
                    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Remove **text** -> text
                    
                    if cleaned:
                        sections[current_section].append(cleaned)
        
        return sections
    
    def format_for_display(self, formatted_output: Dict) -> str:
        """Format structured output for display in UI"""
        display_text = []
        
        # Header
        timestamp = datetime.fromisoformat(formatted_output["timestamp"]).strftime("%B %d, %Y at %I:%M %p")
        display_text.append(f"# T12 Property Analysis Report")
        display_text.append(f"**Generated:** {timestamp}")
        
        if formatted_output["property_info"]:
            display_text.append(f"**Property:** {formatted_output['property_info'].get('name', 'N/A')}")
        
        display_text.append("")
        
        # Strategic Questions
        if formatted_output["analysis"]["strategic_questions"]:
            display_text.append("## 🔍 Strategic Management Questions")
            for i, question in enumerate(formatted_output["analysis"]["strategic_questions"], 1):
                display_text.append(f"{i}. {question}")
            display_text.append("")
        
        # Recommendations
        if formatted_output["analysis"]["recommendations"]:
            display_text.append("## 💡 Actionable Recommendations")
            for i, rec in enumerate(formatted_output["analysis"]["recommendations"], 1):
                display_text.append(f"{i}. {rec}")
            display_text.append("")
        
        # Concerning Trends
        if formatted_output["analysis"]["concerning_trends"]:
            display_text.append("## ⚠️ Concerning Trends")
            for i, concern in enumerate(formatted_output["analysis"]["concerning_trends"], 1):
                display_text.append(f"{i}. {concern}")
            display_text.append("")
        
        return "\n".join(display_text)

class QualityScorer:
    """Score AI response quality based on multiple criteria"""
    
    def __init__(self):
        self.scoring_criteria = {
            "completeness": {"weight": 0.3, "max_score": 100},
            "structure": {"weight": 0.25, "max_score": 100},
            "relevance": {"weight": 0.25, "max_score": 100},
            "actionability": {"weight": 0.2, "max_score": 100}
        }
    
    def score_response(self, response: str, expected_sections: List[str] = None) -> Dict:
        """
        Score AI response quality across multiple dimensions
        Returns score details and overall quality score (0-100)
        """
        scores = {}
        
        # Completeness score
        scores["completeness"] = self._score_completeness(response, expected_sections or [])
        
        # Structure score  
        scores["structure"] = self._score_structure(response)
        
        # Relevance score
        scores["relevance"] = self._score_relevance(response)
        
        # Actionability score
        scores["actionability"] = self._score_actionability(response)
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[criterion] * self.scoring_criteria[criterion]["weight"]
            for criterion in scores
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "dimension_scores": scores,
            "quality_level": self._get_quality_level(overall_score),
            "recommendations": self._get_improvement_recommendations(scores)
        }
    
    def _score_completeness(self, response: str, expected_sections: List[str]) -> float:
        """Score response completeness"""
        if len(response.strip()) < 100:
            return 0.0
        
        # Check for key sections
        response_upper = response.upper()
        section_keywords = ["QUESTION", "RECOMMEND", "CONCERN", "TREND", "RISK", "INSIGHT"]
        
        found_sections = sum(1 for keyword in section_keywords if keyword in response_upper)
        completeness_score = min(100.0, (found_sections / len(section_keywords)) * 100)
        
        return completeness_score
    
    def _score_structure(self, response: str) -> float:
        """Score response structure and formatting"""
        structure_score = 0.0
        
        # Check for headers/sections (worth 40 points)
        if re.search(r'\*\*[A-Z\s]+\*\*|#{1,3}\s+[A-Z]', response):
            structure_score += 40
        
        # Check for numbered/bulleted lists (worth 40 points)
        if re.search(r'^\d+\.|^\*|^\-|^\•', response, re.MULTILINE):
            structure_score += 40
            
        # Check for reasonable length (worth 20 points)
        if 200 <= len(response) <= 2000:
            structure_score += 20
        
        return min(100.0, structure_score)
    
    def _score_relevance(self, response: str) -> float:
        """Score response relevance to real estate/property management"""
        relevance_keywords = [
            "rent", "occupancy", "vacancy", "noi", "revenue", "expense", 
            "tenant", "lease", "property", "cash flow", "delinquency",
            "collection", "maintenance", "management", "market"
        ]
        
        response_lower = response.lower()
        found_keywords = sum(1 for keyword in relevance_keywords if keyword in response_lower)
        
        relevance_score = min(100.0, (found_keywords / len(relevance_keywords)) * 100 * 2)  # Scale up
        return relevance_score
    
    def _score_actionability(self, response: str) -> float:
        """Score how actionable the recommendations are"""
        action_keywords = [
            "implement", "analyze", "review", "investigate", "improve", 
            "reduce", "increase", "optimize", "monitor", "evaluate",
            "focus", "consider", "develop", "establish", "track"
        ]
        
        response_lower = response.lower()
        found_actions = sum(1 for keyword in action_keywords if keyword in response_lower)
        
        actionability_score = min(100.0, (found_actions / len(action_keywords)) * 100 * 3)  # Scale up
        return actionability_score
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level description"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Fair"
        else:
            return "Poor"
    
    def _get_improvement_recommendations(self, scores: Dict) -> List[str]:
        """Get recommendations for improving response quality"""
        recommendations = []
        
        if scores["completeness"] < 70:
            recommendations.append("Include more comprehensive analysis covering all key areas")
        
        if scores["structure"] < 70:
            recommendations.append("Improve formatting with clear headers and bullet points")
        
        if scores["relevance"] < 70:
            recommendations.append("Focus more on property-specific financial metrics and terminology")
        
        if scores["actionability"] < 70:
            recommendations.append("Provide more specific, actionable recommendations")
        
        return recommendations

def post_process_output(raw_response: str, property_info: Dict = None) -> Dict:
    """
    Complete post-processing pipeline for AI output
    """
    formatter = OutputFormatter()
    scorer = QualityScorer()
    
    # Format the output
    formatted = formatter.format_standard_output(raw_response, property_info)
    
    # Score the quality
    quality_score = scorer.score_response(raw_response)
    
    # Add quality metrics to output
    formatted["quality_metrics"] = quality_score
    
    # Generate display version
    formatted["display_text"] = formatter.format_for_display(formatted)
    
    return formatted
