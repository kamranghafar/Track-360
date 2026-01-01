# Ollama Integration for Product Chatbot

## Overview

This integration connects the product chatbot with Ollama, a local LLM runner, to provide context-aware answers about products. The integration uses models located at `C:\Users\kamran.ghaffar\.ollama\models` and includes fallback mechanisms to ensure robustness.

## Features

- **Local LLM Execution**: Uses Ollama to run LLMs locally for better privacy and reduced latency
- **Product Context Awareness**: Includes product documentation and information in the context
- **Tiered Fallback System**: Falls back to Hugging Face Transformers and then rule-based responses if needed
- **Flexible Model Selection**: Automatically uses available models from the Ollama models directory

## Requirements

1. **Ollama Installation**: Ollama must be installed and running on the local machine
   - Download from [Ollama's website](https://ollama.ai/download)
   - Install and start the Ollama service

2. **API Key**: The integration uses an Ollama API key for authentication
   - The API key is configured in the `ai_agent/llm_integration.py` file
   - Current API key: `d0db5a65f9ef44d780426cde5ebb65da.6Mu6fRU-kVeqoYfdkUfNherF`

3. **Models**: At least one model must be downloaded in the Ollama models directory
   - Models are stored at `C:\Users\kamran.ghaffar\.ollama\models`
   - You can download models using the Ollama CLI: `ollama pull llama3` (or other model names)
   - The default model used is `llama3`

4. **Python Dependencies**: The following dependencies are required:
   - `requests`: For making API calls to the Ollama service
   - These are included in the updated requirements.txt file

## How It Works

1. When a user sends a message to the chatbot, the system:
   - Collects context information about products, resources, and the dashboard
   - Formats this context into a prompt for the LLM
   - Sends the prompt to Ollama via its API with the API key for authentication

2. Ollama processes the prompt using the selected model and returns a response

3. If Ollama is unavailable or returns an error, the system falls back to:
   - Hugging Face Transformers (if available)
   - Rule-based responses (always available)

## Testing

A test script is provided to verify the Ollama integration:

```bash
python test_ollama_integration.py
```

This script:
- Checks if Ollama is available
- Creates a test context with product information
- Sends a test message to Ollama
- Reports whether the integration is working correctly

## Troubleshooting

If you encounter issues with the Ollama integration:

1. **Ollama Not Available**:
   - Ensure Ollama is installed and running
   - Check that the Ollama API is accessible at http://localhost:11434/api

2. **No Models Found**:
   - Verify that models are downloaded in `C:\Users\kamran.ghaffar\.ollama\models`
   - Use `ollama list` to see available models

3. **API Errors**:
   - Check the application logs for detailed error messages
   - Ensure the model specified is compatible with your Ollama version

## Implementation Details

The integration is implemented in the following files:

- `ai_agent/llm_integration.py`: Contains the Ollama integration code
- `LLM_INTEGRATION.md`: Documentation of the LLM integration architecture
- `requirements.txt`: Updated with dependencies for the Ollama integration
- `test_ollama_integration.py`: Test script for the Ollama integration

The system automatically detects available Ollama models and uses them for generating responses, with fallbacks to ensure the chatbot always provides a response.
