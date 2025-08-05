"""
Dynamic Prompt Manager for Multi-Format Analysis
Loads format-specific prompts and instructions from configuration files
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptManager:
    """Manager for format-specific prompts and instructions"""
    
    def __init__(self, config_dir: str = None):
        """Initialize prompt manager with configuration directory"""
        if config_dir is None:
            # Default to config/prompts directory relative to this file
            self.config_dir = Path(__file__).parent.parent.parent / "config" / "prompts"
        else:
            self.config_dir = Path(config_dir)
            
        self._prompt_cache = {}
        logger.info(f"PromptManager initialized with config directory: {self.config_dir}")
    
    def load_format_prompts(self, format_name: str) -> Dict:
        """Load prompt configuration for a specific format"""
        if format_name in self._prompt_cache:
            return self._prompt_cache[format_name]
            
        # Convert format name to filename (e.g., "T12_Monthly_Financial" -> "t12_monthly_financial.json")
        filename = format_name.lower() + ".json"
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            logger.warning(f"Prompt config not found for format {format_name} at {config_path}")
            return self._get_default_prompts(format_name)
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._prompt_cache[format_name] = config
                logger.info(f"Loaded prompts for format: {format_name}")
                return config
        except Exception as e:
            logger.error(f"Error loading prompt config for {format_name}: {str(e)}")
            return self._get_default_prompts(format_name)
    
    def build_system_instructions(self, format_name: str, analysis_type: str = "standard") -> str:
        """Build system instructions for a specific format and analysis type"""
        config = self.load_format_prompts(format_name)
        
        if analysis_type == "assistants":
            instructions_config = config.get("assistants_api_instructions", {})
        elif analysis_type == "fallback":
            instructions_config = config.get("fallback_instructions", {})
        elif analysis_type == "minimal":
            instructions_config = config.get("minimal_instructions", {})
        else:
            instructions_config = config.get("system_instructions", {})
        
        # Build the system instruction string
        parts = []
        
        # Role description
        if "role_description" in instructions_config:
            parts.append(instructions_config["role_description"])
        
        # Task description
        if "task_description" in instructions_config:
            parts.append(f"\n{instructions_config['task_description']}")
        
        # Data structure notes
        if "data_structure_notes" in instructions_config:
            parts.append("\nIMPORTANT DATA STRUCTURE NOTES:")
            for note in instructions_config["data_structure_notes"]:
                parts.append(f"- {note}")
        
        # Analysis framework or approach
        framework_key = "analysis_approach" if analysis_type == "assistants" else "analysis_framework"
        if framework_key in instructions_config:
            framework_title = "ANALYSIS APPROACH:" if analysis_type == "assistants" else "ANALYSIS FRAMEWORK:" 
            parts.append(f"\n{framework_title}")
            for i, item in enumerate(instructions_config[framework_key], 1):
                parts.append(f"{i}. {item}")
        
        # Specific analysis areas (for Assistants API)
        if "specific_analysis_areas" in instructions_config:
            parts.append("\nSPECIFIC ANALYSIS AREAS:")
            for area in instructions_config["specific_analysis_areas"]:
                parts.append(f"- {area}")
        
        # Output requirements or format
        output_key = "output_format" if analysis_type == "assistants" else "output_requirements"
        if output_key in instructions_config:
            output_title = "OUTPUT FORMAT:" if analysis_type == "assistants" else "OUTPUT REQUIREMENTS:"
            parts.append(f"\n{output_title}")
            for requirement in instructions_config[output_key]:
                parts.append(f"- {requirement}")
        elif "requirements" in instructions_config:  # For fallback
            parts.append("\nProvide:")
            for i, req in enumerate(instructions_config["requirements"], 1):
                parts.append(f"{i}. {req}")
        
        # Mandatory output format for assistants (highest priority)
        if "MANDATORY_OUTPUT_FORMAT" in instructions_config:
            parts.append(f"\nMANDATORY OUTPUT FORMAT:")
            parts.append(instructions_config["MANDATORY_OUTPUT_FORMAT"])
        
        # Critical requirements for assistants
        if "CRITICAL_REQUIREMENTS" in instructions_config:
            parts.append(f"\nCRITICAL REQUIREMENTS:")
            for requirement in instructions_config["CRITICAL_REQUIREMENTS"]:
                parts.append(f"- {requirement}")
        
        # Analysis tasks (structured approach)
        if "analysis_tasks" in instructions_config:
            parts.append(f"\nANALYSIS TASKS:")
            for task in instructions_config["analysis_tasks"]:
                parts.append(f"- {task}")
        
        # Data format information
        if "data_format" in instructions_config:
            parts.append(f"\nDATA FORMAT:")
            parts.append(instructions_config["data_format"])
        
        # Output style
        if "output_style" in instructions_config:
            parts.append(f"\n{instructions_config['output_style']}")
        
        return "\n".join(parts)
    
    def build_user_prompt(self, format_name: str, data_content: str, analysis_type: str = "standard") -> str:
        """Build user prompt for a specific format"""
        config = self.load_format_prompts(format_name)
        
        # Select appropriate prompt template
        if analysis_type == "fallback":
            template = config.get("fallback_prompt_template", "Analyze this data:\n\n{data_content}")
        elif analysis_type == "minimal":
            template = config.get("minimal_prompt_template", "Review this data:\n\n{data_content}")
        else:
            template = config.get("user_prompt_template", "Please analyze the following data:\n\n{data_content}")
        
        return template.format(data_content=data_content)
    
    def build_prompts(self, format_name: str, data_content: str, analysis_type: str = "standard") -> Tuple[str, str]:
        """Build both system and user prompts for a format"""
        system_prompt = self.build_system_instructions(format_name, analysis_type)
        user_prompt = self.build_user_prompt(format_name, data_content, analysis_type)
        
        logger.info(f"Built prompts for format {format_name}, analysis type {analysis_type}")
        logger.debug(f"System prompt length: {len(system_prompt)} chars")
        logger.debug(f"User prompt length: {len(user_prompt)} chars")
        
        return system_prompt, user_prompt
    
    def get_validation_keywords(self, format_name: str, analysis_type: str = "standard") -> Dict:
        """Get validation keywords for response validation"""
        config = self.load_format_prompts(format_name)
        validation_config = config.get("validation_keywords", {})
        
        # Return appropriate validation keywords based on analysis type
        if analysis_type == "enhanced" or analysis_type == "assistants":
            return {
                "required_content": validation_config.get("required_content", []),
                "min_length": 100
            }
        else:
            return validation_config.get("standard_analysis", {})
    
    def get_available_formats(self) -> list:
        """Get list of available format configurations"""
        if not self.config_dir.exists():
            return []
        
        formats = []
        for file_path in self.config_dir.glob("*.json"):
            format_name = file_path.stem
            formats.append(format_name)
        
        return sorted(formats)
    
    def _get_default_prompts(self, format_name: str) -> Dict:
        """Generate default prompt configuration if none exists"""
        logger.info(f"Using default prompts for format: {format_name}")
        
        return {
            "format_name": format_name,
            "description": f"Default prompt templates for {format_name}",
            "system_instructions": {
                "role_description": "You are a senior real estate investment analyst with expertise in property financial analysis.",
                "task_description": "Your task is to analyze the provided property financial data and generate actionable insights for property management and investment decisions.",
                "data_structure_notes": [
                    "Analyze the data structure and identify key financial metrics",
                    "Pay attention to trends and patterns in the data",
                    "Consider industry benchmarks and best practices"
                ],
                "analysis_framework": [
                    "FINANCIAL PERFORMANCE: Assess revenue and income trends",
                    "OPERATIONAL EFFICIENCY: Evaluate operational metrics and ratios",
                    "RISK ASSESSMENT: Identify potential concerns and red flags",
                    "IMPROVEMENT OPPORTUNITIES: Suggest specific actionable recommendations"
                ],
                "output_requirements": [
                    "Generate 3-5 strategic questions for management consideration",
                    "Provide 3-5 specific actionable recommendations",
                    "Highlight any concerning trends that require attention",
                    "Include relevant industry context and benchmarking"
                ],
                "output_style": "Be concise, specific, and focus on actionable insights that can drive business decisions."
            },
            "user_prompt_template": "Please analyze the following property financial data:\n\n{data_content}\n\nBased on this data, provide your analysis following the framework outlined in your instructions.",
            "fallback_prompt_template": "Analyze this property data and provide key insights:\n\n{data_content}",
            "validation_keywords": {
                "required_content": ["property", "financial", "analysis", "performance", "recommend"],
                "standard_analysis": {
                    "questions": ["question", "what", "how", "why"],
                    "recommendations": ["recommend", "suggest", "improve"],
                    "analysis": ["trend", "performance", "concern"]
                }
            }
        }

# Global instance for easy access
prompt_manager = PromptManager()
