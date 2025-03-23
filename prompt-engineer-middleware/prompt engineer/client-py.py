#!/usr/bin/env python3
"""
Client for Prompt Engineer Middleware

This script demonstrates how to use the Prompt Engineer Middleware
from a client application.
"""

import argparse
import json
import os
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PromptEngineerClient:
    """Client for the Prompt Engineer Middleware."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def process_prompt(
        self, 
        prompt: str, 
        provider: str = "openai", 
        model: Optional[str] = None, 
        options: Dict[str, Any] = None,
        bypass_enhancement: bool = False
    ) -> Dict[str, Any]:
        """
        Process a prompt through the middleware.
        
        Args:
            prompt: The user prompt to process
            provider: LLM provider to use (openai, anthropic, huggingface)
            model: Specific model to use
            options: Additional options for the provider
            bypass_enhancement: Whether to bypass prompt enhancement
            
        Returns:
            Dictionary with the response and enhancement_index
        """
        options = options or {}
        
        # Add API keys from environment if not provided
        if "api_key" not in options:
            if provider.lower() == "openai":
                options["api_key"] = os.getenv("OPENAI_API_KEY")
            elif provider.lower() == "anthropic":
                options["api_key"] = os.getenv("ANTHROPIC_API_KEY")
            elif provider.lower() == "huggingface":
                options["api_key"] = os.getenv("HUGGINGFACE_API_KEY")
        
        # Prepare request payload
        payload = {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "options": options,
            "bypass_enhancement": bypass_enhancement
        }
        
        # Send request to middleware
        response = requests.post(f"{self.base_url}/process", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def provide_feedback(self, enhancement_index: int, rating: int) -> Dict[str, Any]:
        """
        Provide feedback on a prompt enhancement.
        
        Args:
            enhancement_index: Index of the enhancement in history
            rating: Effectiveness rating (1-5)
            
        Returns:
            Status response
        """
        payload = {
            "enhancement_index": enhancement_index,
            "rating": rating
        }
        
        response = requests.post(f"{self.base_url}/feedback", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_enhancement_history(self) -> Dict[str, Any]:
        """
        Get the enhancement history.
        
        Returns:
            Dictionary with the enhancement history
        """
        response = requests.get(f"{self.base_url}/history")
        response.raise_for_status()
        
        return response.json()

def main():
    """Main function for the client example."""
    parser = argparse.ArgumentParser(description="Client for Prompt Engineer Middleware")
    parser.add_argument("--url", default="http://localhost:8000", help="Middleware base URL")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic", "huggingface"], help="LLM provider")
    parser.add_argument("--model", help="Specific model to use")
    parser.add_argument("--bypass", action="store_true", help="Bypass prompt enhancement")
    parser.add_argument("--history", action="store_true", help="Get enhancement history")
    parser.add_argument("--feedback", nargs=2, metavar=("INDEX", "RATING"), help="Provide feedback on enhancement")
    parser.add_argument("prompt", nargs="?", help="Prompt to process")
    
    args = parser.parse_args()
    client = PromptEngineerClient(args.url)
    
    if args.history:
        # Get enhancement history
        history = client.get_enhancement_history()
        print(json.dumps(history, indent=2))
    elif args.feedback:
        # Provide feedback
        index = int(args.feedback[0])
        rating = int(args.feedback[1])
        result = client.provide_feedback(index, rating)
        print(json.dumps(result, indent=2))
    elif args.prompt:
        # Process prompt
        result = client.process_prompt(
            args.prompt,
            provider=args.provider,
            model=args.model,
            bypass_enhancement=args.bypass
        )
        
        print("\nLLM Response:")
        print("=" * 40)
        print(result["response"])
        print("=" * 40)
        
        if result["enhancement_index"] is not None:
            print(f"\nEnhancement Index: {result['enhancement_index']}")
            print("You can provide feedback on this enhancement with:")
            print(f"python client.py --feedback {result['enhancement_index']} <rating>")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
