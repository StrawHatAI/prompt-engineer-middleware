"""
LLM Provider Connectors

This module contains connectors for different LLM providers.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("prompt_engineer.providers")

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate a response from the LLM for the given prompt."""
        pass

class OpenAIConnector(LLMProvider):
    """Connector for OpenAI models."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    async def generate_response(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate a response from OpenAI models."""
        options = options or {}
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": options.get("model", self.model),
            "messages": [
                {"role": "system", "content": options.get("system_prompt", "You are a helpful assistant.")},
                {"role": "user", "content": prompt}
            ],
            "temperature": options.get("temperature", 0.7),
            "max_tokens": options.get("max_tokens", 1000),
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {e}")
            raise

class AnthropicConnector(LLMProvider):
    """Connector for Anthropic Claude models."""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    async def generate_response(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate a response from Anthropic Claude models."""
        options = options or {}
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": options.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": options.get("max_tokens", 1000),
            "temperature": options.get("temperature", 0.7),
            "system": options.get("system_prompt", "You are Claude, a helpful AI assistant.")
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error generating response from Anthropic: {e}")
            raise

class HuggingFaceConnector(LLMProvider):
    """Connector for Hugging Face models."""
    
    def __init__(self, api_key: str = None, model: str = "meta-llama/Llama-2-70b-chat-hf"):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("Hugging Face API key is required")
        self.model = model
        self.base_url = f"https://api-inference.huggingface.co/models/{model}"
        
    async def generate_response(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate a response from Hugging Face models."""
        options = options or {}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": options.get("max_tokens", 1000),
                "temperature": options.get("temperature", 0.7),
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()[0]["generated_text"]
        except Exception as e:
            logger.error(f"Error generating response from Hugging Face: {e}")
            raise
