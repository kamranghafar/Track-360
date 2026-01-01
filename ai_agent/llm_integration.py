"""
LLM integration module for the AI agent.
This module provides functions for loading models, generating responses,
and formatting output using Hugging Face's Transformers library and Ollama.
"""

import os
import warnings
import torch
import requests
import json
from typing import Dict, Any, List, Optional, Tuple

# Suppress specific warnings from transformers
warnings.filterwarnings("ignore", message="torch.utils.checkpoint: please pass in use_reentrant=True")
warnings.filterwarnings("ignore", message="Truncation was not explicitly activated")

# Define constants
DEFAULT_MODEL = "distilgpt2"  # Using a non-gated model as default
DEFAULT_OLLAMA_MODEL = "llama3"  # Default Ollama model
OLLAMA_API_BASE = "http://localhost:11434/api"  # Default Ollama API endpoint
OLLAMA_API_KEY = "d0db5a65f9ef44d780426cde5ebb65da.6Mu6fRU-kVeqoYfdkUfNherF"  # Ollama API key

# Cache for loaded models and tokenizers
MODEL_CACHE = {}

# Flag to check if transformers is available
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
    print("Transformers library is available")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"Transformers library is not available: {str(e)}")

# Flag to check if Ollama is available
OLLAMA_AVAILABLE = False
# Store available Ollama models
AVAILABLE_OLLAMA_MODELS = []
try:
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    response = requests.get(f"{OLLAMA_API_BASE}/tags", headers=headers)
    if response.status_code == 200:
        OLLAMA_AVAILABLE = True
        print("Ollama is available")
        # List available models
        models_data = response.json().get("models", [])
        AVAILABLE_OLLAMA_MODELS = [model['name'] for model in models_data]
        print(f"Available Ollama models: {AVAILABLE_OLLAMA_MODELS}")
except Exception as e:
    print(f"Ollama is not available: {str(e)}")


def is_llm_available() -> bool:
    """
    Check if any LLM functionality is available (either Transformers or Ollama).

    Returns:
        bool: True if any LLM is available, False otherwise
    """
    return TRANSFORMERS_AVAILABLE or OLLAMA_AVAILABLE


def format_context_for_llm(context) -> str:
    """
    Format the dashboard context into a string that can be used as input to the LLM.

    Args:
        context: DashboardContext object

    Returns:
        str: Formatted context string
    """
    context_str = f"""
Dashboard Context:
- Total Products: {context.total_products}
- Total Resources: {context.total_resources}
- Active Products: {context.active_products}
- Completed Products: {context.completed_products}
- Current View: {context.current_view}
"""

    # Add filters if any
    if hasattr(context, 'applied_filters') and context.applied_filters:
        context_str += "Applied Filters:\n"
        for key, value in context.applied_filters.items():
            context_str += f"- {key}: {value}\n"

    # Add visible charts if any
    if hasattr(context, 'visible_charts') and context.visible_charts:
        context_str += "Visible Charts:\n"
        for chart in context.visible_charts:
            context_str += f"- {chart}\n"

    # Add recent actions if any
    if hasattr(context, 'recent_actions') and context.recent_actions:
        context_str += "Recent Actions:\n"
        for i, action in enumerate(context.recent_actions[:3], 1):  # Show only the 3 most recent actions
            context_str += f"- {action.get('action_type', 'Unknown')}: {action.get('details', 'No details')}\n"

    # Add current product if available
    if hasattr(context, 'current_product') and context.current_product:
        context_str += f"Current Product: {context.current_product}\n"

    # Add current resource if available
    if hasattr(context, 'current_resource') and context.current_resource:
        context_str += f"Current Resource: {context.current_resource}\n"

    # Add product documentation if available
    try:
        # Check if database is available from context
        database_available = True
        if hasattr(context, 'applied_filters') and isinstance(context.applied_filters, dict):
            database_available = context.applied_filters.get('database_available', True)

        if database_available:
            from dashboard.models import ProductDocumentation, Project
            projects = Project.objects.all()[:5]  # Limit to 5 projects to avoid overwhelming the context
            if projects:
                context_str += "\nProduct Information:\n"
                for project in projects:
                    context_str += f"- {project.name} (Status: {project.status})\n"
                    docs = ProductDocumentation.objects.filter(project=project)[:3]  # Limit to 3 docs per project
                    if docs:
                        context_str += "  Documentation:\n"
                        for doc in docs:
                            context_str += f"  - {doc.title}\n"
        else:
            context_str += "\nNote: Database connection is currently unavailable. Product information cannot be retrieved.\n"
    except Exception as e:
        print(f"Error fetching product documentation: {str(e)}")
        context_str += "\nNote: There was an error retrieving product information from the database.\n"

    return context_str


def load_model_and_tokenizer(model_name: str = DEFAULT_MODEL) -> Tuple[Any, Any]:
    """
    Load a model and tokenizer, with caching.

    Args:
        model_name (str): Name of the model to load

    Returns:
        tuple: (model, tokenizer)
    """
    # Check if model and tokenizer are already loaded
    if model_name in MODEL_CACHE:
        print(f"Using cached model: {model_name}")
        return MODEL_CACHE[model_name]

    print(f"Loading model {model_name}...")

    # Set device to CPU explicitly to avoid CUDA issues
    print("Device set to use CPU")
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    try:
        # Load tokenizer with truncation explicitly set
        tokenizer = AutoTokenizer.from_pretrained(model_name, truncation=True)

        # Try to load with 8-bit quantization if available
        try:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                quantization_config=quantization_config
            )
        except ImportError:
            # Fall back to regular loading if bitsandbytes is not available
            model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", low_cpu_mem_usage=True)

        # Cache the model and tokenizer
        MODEL_CACHE[model_name] = (model, tokenizer)

        return model, tokenizer
    except Exception as e:
        print(f"Error loading model {model_name}: {str(e)}")
        # Fall back to a smaller model if the requested one fails
        if model_name != "distilgpt2":  # Use a very small model as ultimate fallback
            print(f"Falling back to distilgpt2")
            return load_model_and_tokenizer("distilgpt2")
        else:
            raise


def generate_ollama_response(message: str, context, model_name: str = DEFAULT_OLLAMA_MODEL) -> str:
    """
    Generate a response using Ollama based on the user's message and dashboard context.

    Args:
        message (str): The user's message
        context: DashboardContext object
        model_name (str): Name of the Ollama model to use

    Returns:
        str: The Ollama-generated response or None if there was an error
    """
    if not OLLAMA_AVAILABLE:
        print("Ollama is not available")
        return None

    try:
        print(f"Generating Ollama response using model {model_name} for message: {message}")

        # Format the context
        context_str = format_context_for_llm(context)

        # Create the prompt
        prompt = f"""
You are an AI assistant for a product dashboard application. You help users understand their dashboard data and answer questions about projects, resources, and KPIs.

{context_str}

User Question: {message}

Please provide a helpful, accurate, and concise response based on the dashboard context:
"""

        # Set up the API request to Ollama
        api_url = f"{OLLAMA_API_BASE}/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }

        # Make the API request
        print(f"Sending request to Ollama API at {api_url}")
        headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Error from Ollama API: {response.status_code} - {response.text}")
            return None

        # Parse the response
        response_data = response.json()
        assistant_response = response_data.get("response", "")

        # Clean up the response if needed
        assistant_response = assistant_response.replace("AI:", "").replace("Assistant:", "").strip()

        # If the response is empty or too short, return None
        if len(assistant_response) < 20:
            print("Ollama response too short")
            return None

        print(f"Ollama response generated: {assistant_response[:50]}...")
        return assistant_response

    except Exception as e:
        # Log the error
        print(f"Error generating Ollama response: {str(e)}")
        return None


def generate_llm_response(message: str, context, request, model_name: str = DEFAULT_MODEL) -> str:
    """
    Generate a response using an LLM based on the user's message and dashboard context.
    Tries Ollama first, then falls back to Transformers, then falls back to rule-based.

    Args:
        message (str): The user's message
        context: DashboardContext object
        request: The HTTP request
        model_name (str): Name of the model to use

    Returns:
        str: The LLM-generated response
    """
    if not is_llm_available():
        print("No LLM is available, falling back to rule-based approach")
        from .views import generate_ai_response_rule_based
        return generate_ai_response_rule_based(message, context, request)

    # Try Ollama first if available
    if OLLAMA_AVAILABLE:
        print("Trying Ollama first...")
        # Always use llama3 if available, otherwise fall back to other models
        try:
            # Force the use of llama3 if it's in the available models
            if "llama3" in AVAILABLE_OLLAMA_MODELS or "llama3:latest" in AVAILABLE_OLLAMA_MODELS:
                ollama_model = "llama3"
            # Otherwise, use the default model if available
            elif DEFAULT_OLLAMA_MODEL in AVAILABLE_OLLAMA_MODELS:
                ollama_model = DEFAULT_OLLAMA_MODEL
            # Otherwise, use the first available model
            elif AVAILABLE_OLLAMA_MODELS:
                ollama_model = AVAILABLE_OLLAMA_MODELS[0]
            # If no models are available, use llama3 (will likely fail but with a clear error)
            else:
                ollama_model = "llama3"
            print(f"Using Ollama model: {ollama_model}")
        except Exception as e:
            print(f"Error determining Ollama model: {str(e)}")
            ollama_model = DEFAULT_OLLAMA_MODEL

        ollama_response = generate_ollama_response(message, context, ollama_model)
        if ollama_response:
            return ollama_response
        print("Ollama response failed, falling back to Transformers")

    # Fall back to Transformers if Ollama failed
    if TRANSFORMERS_AVAILABLE:
        try:
            print(f"Generating Transformers response for message: {message}")

            # Format the context
            context_str = format_context_for_llm(context)

            # Create the prompt
            prompt = f"""
You are an AI assistant for a product dashboard application. You help users understand their dashboard data and answer questions about projects, resources, and KPIs.

{context_str}

User Question: {message}

Please provide a helpful, accurate, and concise response based on the dashboard context:
"""

            # Load model and tokenizer
            model, tokenizer = load_model_and_tokenizer(model_name)

            # Create a text generation pipeline with explicit truncation
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=300,  # Increased max length for longer responses
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                truncation=True
            )

            # Generate response
            print("Generating response...")
            response = generator(prompt, max_length=300, num_return_sequences=1)[0]['generated_text']

            # Extract just the assistant's response (after the prompt)
            try:
                # Try to extract the response after the prompt
                if "Please provide a helpful, accurate, and concise response based on the dashboard context:" in response:
                    assistant_response = response.split("Please provide a helpful, accurate, and concise response based on the dashboard context:")[-1].strip()
                else:
                    # If the split point is not found, try to extract the response after the user question
                    question_marker = f"User Question: {message}"
                    if question_marker in response:
                        assistant_response = response.split(question_marker)[-1].strip()
                        # Remove any remaining prompt text if present
                        if "Please provide" in assistant_response:
                            assistant_response = assistant_response.split("Please provide")[0].strip()
                    else:
                        # If all else fails, use the whole response but limit it
                        assistant_response = response[-200:].strip()
            except Exception as e:
                print(f"Error extracting assistant response: {str(e)}")
                # Use a simple approach as fallback
                assistant_response = response[-200:].strip()

            # If the response is empty or too short, fall back to the rule-based approach
            if len(assistant_response) < 20:
                print("Transformers response too short, falling back to rule-based approach")
                from .views import generate_ai_response_rule_based
                return generate_ai_response_rule_based(message, context, request)

            # Clean up the response if needed
            assistant_response = assistant_response.replace("AI:", "").replace("Assistant:", "").strip()

            print(f"Transformers response generated: {assistant_response[:50]}...")
            return assistant_response

        except Exception as e:
            # Log the error
            print(f"Error generating Transformers response: {str(e)}")

    # Fall back to the rule-based approach if all else fails
    print("All LLM approaches failed, falling back to rule-based approach")
    from .views import generate_ai_response_rule_based
    return generate_ai_response_rule_based(message, context, request)
