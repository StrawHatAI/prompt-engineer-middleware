# Prompt Engineer Middleware

A powerful middleware service that sits between users and Language Models to automatically enhance prompts for better responses.

## Overview

This middleware acts as a "prompt engineer" that improves user prompts behind the scenes before sending them to LLMs. It analyzes incoming prompts, adds relevant context and specificity, structures multi-part questions logically, and injects appropriate instructions based on the task type.

Key benefits:
- Better quality LLM responses without requiring users to master prompt engineering
- Domain-specific prompt enhancements for coding, creative, analytical, and other tasks
- Extensible architecture supporting multiple LLM providers (OpenAI, Anthropic, Hugging Face)
- Tracking and improvement of enhancement effectiveness over time

## Architecture

The middleware consists of several components:
- **LLM Providers**: Connectors for different LLM services (OpenAI, Anthropic, Hugging Face)
- **Prompt Engineer**: Core logic for enhancing prompts based on type and rules
- **API Server**: FastAPI endpoints for processing prompts, providing feedback, and viewing history
- **Client**: Example client for interacting with the middleware

## Quick Start

### Using Docker Compose

1. Clone this repository
2. Create a `.env` file with your API keys (use `.env.example` as a template):
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   HUGGINGFACE_API_KEY=your_huggingface_key
   ```
3. Run the middleware:
   ```
   docker-compose up -d
   ```

### Manual Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables for your API keys
4. Run the middleware:
   ```
   uvicorn src.prompt_engineer_middleware:app --host 0.0.0.0 --port 8000
   ```

## Usage

### Using the Client

The repository includes a sample client (`client.py`) that demonstrates how to use the middleware:

```bash
# Process a prompt
python client.py "Write a function to calculate fibonacci numbers"

# Specify a different provider
python client.py --provider anthropic "Explain quantum computing"

# Get enhancement history
python client.py --history

# Provide feedback on an enhancement
python client.py --feedback 0 5  # Rate enhancement #0 as 5/5
```

### API Endpoints

The middleware exposes the following REST endpoints:

- `POST /process` - Process a prompt through enhancement and LLM
- `POST /feedback` - Provide feedback on a prompt enhancement
- `GET /history` - Get the enhancement history

## Customization

### Enhancement Rules

You can customize enhancement rules by modifying the `enhancement_rules.json` file. Each rule includes:

- `system_prompt` - The system prompt for the meta-prompt LLM
- `template` - The template for enhancing prompts of this type

The middleware comes with built-in rules for common prompt types (coding, creative, analytical, etc.), which you can extend with your own domain-specific rules.

### LLM Providers

The middleware supports the following LLM providers out of the box:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Hugging Face (hosted models)

You can extend the middleware to support additional providers by creating new connector classes that implement the `LLMProvider` interface.

## Advanced Features

### Feedback Loop

The middleware includes a feedback mechanism to track the effectiveness of prompt enhancements. Users can rate the quality of enhanced prompts, which helps improve the enhancement process over time.

### Enhancement History

The middleware keeps a history of all enhanced prompts, along with their effectiveness ratings. This history can be used to analyze the impact of different enhancement techniques and improve the rules.

## Project Structure

```
prompt-engineer-middleware/
├── src/
│   ├── __init__.py
│   ├── prompt_engineer_middleware.py  # Main application
│   ├── llm_providers.py               # LLM provider connectors
│   ├── prompt_engineer.py             # Prompt enhancement logic
│   └── models.py                      # Pydantic models for API
├── client.py                          # Client example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── enhancement_rules.json             # Customizable rules
├── .env.example                       # Example environment variables
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This project was inspired by the need to make advanced prompt engineering techniques accessible to everyone, regardless of their expertise with LLMs.
- The meta-prompt approach was inspired by various research papers on prompt optimization and chain-of-thought prompting.
