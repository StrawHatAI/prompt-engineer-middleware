"""
Prompt Engineer Middleware

A middleware service that sits between users and LLMs to automatically
enhance prompts for better responses.
"""

import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .models import PromptRequest, FeedbackRequest, PromptResponse
from .llm_providers import OpenAIConnector, AnthropicConnector, HuggingFaceConnector, LLMProvider
from .prompt_engineer import PromptEngineer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prompt_engineer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("prompt_engineer")

#################################################
# API Server
#################################################

app = FastAPI(
    title="Prompt Engineer Middleware",
    description="A middleware service that enhances prompts before sending to LLMs",
    version="1.0.0"
)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize providers and prompt engineer
llm_providers = {}
prompt_engineers = {}

def get_or_create_provider(provider_name: str, api_key: str = None, model: str = None) -> LLMProvider:
    """Get or create an LLM provider instance."""
    provider_key = f"{provider_name}_{model or 'default'}"
    
    if provider_key not in llm_providers:
        if provider_name.lower() == "openai":
            llm_providers[provider_key] = OpenAIConnector(api_key, model)
        elif provider_name.lower() == "anthropic":
            llm_providers[provider_key] = AnthropicConnector(api_key, model)
        elif provider_name.lower() == "huggingface":
            llm_providers[provider_key] = HuggingFaceConnector(api_key, model)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    return llm_providers[provider_key]

def get_or_create_prompt_engineer(provider: LLMProvider) -> PromptEngineer:
    """Get or create a prompt engineer instance for the given provider."""
    provider_id = id(provider)
    
    if provider_id not in prompt_engineers:
        prompt_engineers[provider_id] = PromptEngineer(provider)
    
    return prompt_engineers[provider_id]

@app.post("/process", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    """Process a user prompt through the prompt engineer and LLM."""
    try:
        # Get or create provider
        provider = get_or_create_provider(
            request.provider, 
            request.options.get("api_key"), 
            request.model
        )
        
        # Get or create prompt engineer
        prompt_engineer = get_or_create_prompt_engineer(provider)
        
        # Enhance the prompt if not bypassed
        if request.bypass_enhancement:
            final_prompt = request.prompt
            enhancement_index = None
        else:
            final_prompt = await prompt_engineer.enhance_prompt(request.prompt)
            enhancement_index = len(prompt_engineer.enhancement_history) - 1
        
        # Generate response from LLM
        llm_response = await provider.generate_response(final_prompt, request.options)
        
        return PromptResponse(
            response=llm_response,
            enhancement_index=enhancement_index
        )
    
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback on the effectiveness of a prompt enhancement."""
    try:
        # Since we don't know which prompt engineer to update, update all with the same index
        # In a real system, you'd want to track which prompt engineer was used
        for prompt_engineer in prompt_engineers.values():
            prompt_engineer.record_effectiveness(request.enhancement_index, request.rating)
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error providing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/history")
async def get_enhancement_history():
    """Get the enhancement history for analysis."""
    # For simplicity, return history from the first prompt engineer
    # In a real system, you'd want better tracking of prompt engineers
    if not prompt_engineers:
        return {"history": []}
    
    first_engineer = next(iter(prompt_engineers.values()))
    history = [enhancement.to_dict() for enhancement in first_engineer.enhancement_history]
    
    return {"history": history}

@app.on_event("shutdown")
async def shutdown_event():
    """Save enhancement history on shutdown."""
    for prompt_engineer in prompt_engineers.values():
        prompt_engineer.save_enhancement_history()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
