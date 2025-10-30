import os
from pathlib import Path
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Optional, List
import requests
import json
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

load_dotenv('config.env')

# Global variables for Mistral model loading
_mistral_model = None
_mistral_tokenizer = None

def tavily_search(
    query: str = "",
    api_key: str = os.getenv('TAVILY_API_KEY'),
    max_results: int = 5,
    topic: str = "general",
    search_depth: str = "basic",  # "basic" or "advanced"
    include_answer: bool = True,
    include_raw_content: bool = False,
    include_images: bool = False,
    include_image_descriptions: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    country: Optional[str] = None,
    time_range: Optional[str] = None,     # "day", "week", "month", "year"
    start_date: Optional[str] = None,     # format: "YYYY-MM-DD"
    end_date: Optional[str] = None,       # format: "YYYY-MM-DD"
    print_output: bool = True
) -> Optional[dict]:
    """
    Calls the Tavily Search API with given parameters.

    All inputs are function parameters with defaults, so this function can be
    directly imported and called from another Python file.

    Returns:
        dict: JSON response from Tavily API if successful.
        None: If an error occurs.
    """
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "query": query,
        "max_results": max_results,
        "topic": topic,
        "search_depth": search_depth,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
        "include_images": include_images,
        "include_image_descriptions": include_image_descriptions,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains,
        "country": country,
        "time_range": time_range,
        "start_date": start_date,
        "end_date": end_date
    }

    # Remove None values to avoid sending empty fields
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # if print_output:
        #     print(json.dumps(data, indent=4))

        return data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def yes_no_openai(question: str) -> str:
    """
    Returns "Yes" or "No" based on analysis using OpenAI.
    """
    data=tavily_search(
        query=question,
        # max_results=3,
        # search_depth="basic",
    )

    prompt = f"""
You are a precise analyst.
Analyze the data below and answer the question strictly with "Yes" or "No".

Data:
{data}

Question:
{question}

Answer (Yes/No only):
"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        #model="gpt-4o-mini",  # lightweight reasoning model
        model="gpt-3.5-turbo-instruct",
        messages=[
            {"role": "system", "content": "You are a data analyst that only answers Yes or No."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,  # make output deterministic
    )

    answer = response.choices[0].message.content.strip()

    # Normalize the output (e.g., "yes", "YES" → "Yes")
    return "Yes" if answer.lower().startswith("y") else "No"


def yes_no(question: str, use_local: bool = False) -> str:
    """
    Returns "Yes" or "No" based on analysis.
    By default uses OpenAI, but can use local Mistral model if use_local=True.
    
    Args:
        question (str): The question to evaluate.
        use_local (bool): If True, use local Mistral model. If False, use OpenAI.
        
    Returns:
        str: "Yes" or "No"
    """
    if use_local:
        return yes_no_mistral(question)
    else:
        return yes_no_openai(question)


def load_mistral_model():
    """
    Load the local Mistral model and tokenizer.
    Uses global variables to cache the model after first load.
    """
    global _mistral_model, _mistral_tokenizer
    
    if _mistral_model is not None and _mistral_tokenizer is not None:
        return _mistral_model, _mistral_tokenizer
    
    # Get absolute path to the model directory
    model_path = Path("models/Mistral-7B-Instruct-v0.3").resolve()
    
    print(f"Loading Mistral model from {model_path}...")
    
    # Check if model directory exists
    if not model_path.exists():
        print(f"Error: Model directory not found at {model_path}")
        print("Please run: python download_model.py")
        print("Falling back to OpenAI...")
        return None, None
    
    # Check for essential model files
    required_files = ["config.json", "tokenizer.json"]
    missing_files = [f for f in required_files if not (model_path / f).exists()]
    if missing_files:
        print(f"Error: Missing required files: {missing_files}")
        print("Model download appears incomplete. Please run: python download_model.py")
        print("Falling back to OpenAI...")
        return None, None
    
    try:
        _mistral_tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
        
        # Set pad token if not set
        if _mistral_tokenizer.pad_token is None:
            _mistral_tokenizer.pad_token = _mistral_tokenizer.eos_token
        
        _mistral_model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("Mistral model loaded successfully!")
        return _mistral_model, _mistral_tokenizer
    except Exception as e:
        print(f"Error loading Mistral model: {e}")
        print("Falling back to OpenAI...")
        return None, None


def yes_no_mistral(question: str) -> str:
    """
    Returns "Yes" or "No" based on analysis using local Mistral model.
    
    Args:
        question (str): The question to evaluate.
        
    Returns:
        str: "Yes" or "No"
    """
    model, tokenizer = load_mistral_model()
    
    if model is None or tokenizer is None:
        print("Mistral model not available, falling back to OpenAI")
        return yes_no_openai(question)
    
    data = tavily_search(query=question)
    
    prompt = f"""
You are a precise analyst.
Analyze the data below and answer the question strictly with "Yes" or "No".

Data:
{data}

Question:
{question}

Answer (Yes/No only):
"""
    
    # Format messages for Mistral
    messages = [
        {"role": "system", "content": "You are a data analyst that only answers Yes or No."},
        {"role": "user", "content": prompt}
    ]
    
    # Apply chat template
    try:
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    except Exception as e:
        print(f"Warning: apply_chat_template failed: {e}")
        # Fallback: create prompt manually
        formatted_prompt = f"You are a data analyst that only answers Yes or No.\n\n{prompt}"
    
    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    # Move to device if available
    if hasattr(model, 'device'):
        inputs = {k: v.to(model.device) if hasattr(v, 'to') else v for k, v in inputs.items()}
    
    # Set up generation parameters
    generation_kwargs = {
        "max_new_tokens": 50,
        "temperature": 0.0,
        "do_sample": False,
    }
    
    # Handle pad token
    if tokenizer.pad_token_id is None:
        generation_kwargs["pad_token_id"] = tokenizer.eos_token_id
    else:
        generation_kwargs["pad_token_id"] = tokenizer.pad_token_id
    
    # Generate
    with torch.no_grad():
        try:
            outputs = model.generate(**inputs, **generation_kwargs)
        except Exception as e:
            print(f"Error during generation: {e}")
            raise
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract the generated part (after the input prompt)
    answer = generated_text[len(formatted_prompt):].strip()
    
    # Normalize the output (e.g., "yes", "YES" → "Yes")
    return "Yes" if answer.lower().startswith("y") else "No"


# 🔍 Test the function directly when running this script
if __name__ == "__main__":
    question = "Is VIrat Kohli the Prime Minister of India?"
    
    print("Testing with OpenAI (default):")
    print(yes_no(question, use_local=False))
    
    # print("\nTesting with Mistral (if available):")
    # print(yes_no(question, use_local=True))