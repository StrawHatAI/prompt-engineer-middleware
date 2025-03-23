"""
Prompt Engineer

This module contains the logic for enhancing prompts.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional

from .llm_providers import LLMProvider

logger = logging.getLogger("prompt_engineer.core")

class PromptEnhancement:
    """Record of a prompt enhancement."""
    
    def __init__(self, original_prompt: str, enhanced_prompt: str):
        self.original_prompt = original_prompt
        self.enhanced_prompt = enhanced_prompt
        self.timestamp = time.time()
        self.effectiveness_rating = None  # Can be set later based on feedback

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_prompt": self.original_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "timestamp": self.timestamp,
            "effectiveness_rating": self.effectiveness_rating
        }

class PromptEngineer:
    """Enhance user prompts to improve LLM responses."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.enhancement_history: List[PromptEnhancement] = []
        self.load_enhancement_rules()
        
    def load_enhancement_rules(self):
        """Load enhancement rules from configuration."""
        # Default enhancement rules and templates
        self.enhancement_rules = {
            "coding": {
                "system_prompt": "You are a professional software developer with expertise in clean code and best practices.",
                "template": """
                Consider this coding request: "{prompt}"
                
                Enhance this request by:
                1. Clarifying the programming language if not specified
                2. Adding requirements for error handling and edge cases
                3. Specifying if documentation is needed
                4. Asking for proper formatting and modular design
                5. Requesting appropriate comments and variable naming
                
                Return ONLY the enhanced prompt without explanations or preamble.
                """
            },
            "creative": {
                "system_prompt": "You are a creative writing and content creation expert.",
                "template": """
                Consider this creative request: "{prompt}"
                
                Enhance this request by:
                1. Clarifying the style, tone, and format
                2. Specifying target audience if relevant
                3. Adding structure guidance
                4. Including any relevant constraints
                5. Specifying length or detail level
                
                Return ONLY the enhanced prompt without explanations or preamble.
                """
            },
            "analytical": {
                "system_prompt": "You are an analytical expert specializing in structured thinking and clear analysis.",
                "template": """
                Consider this analytical request: "{prompt}"
                
                Enhance this request by:
                1. Adding structure for step-by-step reasoning
                2. Specifying the depth of analysis needed
                3. Clarifying what metrics or frameworks to use
                4. Adding requirements for evidence or citations
                5. Requesting specific output format if helpful
                
                Return ONLY the enhanced prompt without explanations or preamble.
                """
            },
            "default": {
                "system_prompt": "You are an expert prompt engineer who improves user prompts for better results.",
                "template": """
                Consider this prompt: "{prompt}"
                
                Enhance this prompt to be more effective by:
                1. Adding relevant context or specificity
                2. Clarifying any ambiguous aspects
                3. Structuring multi-part requests logically
                4. Adding appropriate constraints or guidance
                5. Preserving the original intent while improving clarity
                
                Return ONLY the enhanced prompt without explanations or preamble.
                """
            }
        }
        
        # Try to load custom rules from file
        try:
            with open("enhancement_rules.json", "r") as f:
                custom_rules = json.load(f)
                self.enhancement_rules.update(custom_rules)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No custom enhancement rules found or invalid format.")
    
    def detect_prompt_type(self, prompt: str) -> str:
        """Detect the type of prompt to apply appropriate enhancement rules."""
        prompt_lower = prompt.lower()
        
        if any(term in prompt_lower for term in ["code", "function", "program", "script", "develop", "bug", "debug", "coding"]):
            return "coding"
        elif any(term in prompt_lower for term in ["write", "story", "creative", "design", "article", "blog"]):
            return "creative"
        elif any(term in prompt_lower for term in ["analyze", "analysis", "research", "evaluate", "compare", "explain", "reason"]):
            return "analytical"
        else:
            return "default"
    
    async def enhance_prompt(self, prompt: str) -> str:
        """Enhance a user prompt for better results."""
        prompt_type = self.detect_prompt_type(prompt)
        enhancement_rule = self.enhancement_rules[prompt_type]
        
        # Use the meta-prompt approach - asking the LLM to enhance the prompt
        meta_prompt = enhancement_rule["template"].format(prompt=prompt)
        
        try:
            enhanced_prompt = await self.llm_provider.generate_response(
                meta_prompt,
                options={"system_prompt": enhancement_rule["system_prompt"]}
            )
            
            # Record enhancement
            enhancement = PromptEnhancement(prompt, enhanced_prompt)
            self.enhancement_history.append(enhancement)
            
            logger.info(f"Enhanced prompt of type '{prompt_type}'")
            logger.debug(f"Original: {prompt}")
            logger.debug(f"Enhanced: {enhanced_prompt}")
            
            return enhanced_prompt
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            # Fall back to original prompt in case of error
            return prompt
    
    def record_effectiveness(self, index: int, rating: int) -> None:
        """Record the effectiveness of a prompt enhancement."""
        if 0 <= index < len(self.enhancement_history):
            self.enhancement_history[index].effectiveness_rating = rating
            logger.info(f"Recorded effectiveness rating {rating} for enhancement at index {index}")
        else:
            logger.warning(f"Invalid enhancement index: {index}")
    
    def save_enhancement_history(self, filename: str = "enhancement_history.json") -> None:
        """Save the enhancement history to a file."""
        history_data = [enhancement.to_dict() for enhancement in self.enhancement_history]
        try:
            with open(filename, "w") as f:
                json.dump(history_data, f, indent=2)
            logger.info(f"Saved enhancement history to {filename}")
        except Exception as e:
            logger.error(f"Error saving enhancement history: {e}")
