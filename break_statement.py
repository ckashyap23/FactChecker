from openai import OpenAI
from typing import List, Tuple
from dotenv import load_dotenv
import os
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

load_dotenv('config.env')

# Global variables for Mistral model loading
_mistral_model = None
_mistral_tokenizer = None

def decompose_statement_to_questions_openai(
    statement: str,
    #model: str = "gpt-4o-mini",
    model: str = "gpt-3.5-turbo-instruct",
) -> Tuple[List[str], int]:
    """
    Decomposes a factual statement into atomic questions to enable fact-checking using OpenAI.
    
    Args:
        statement (str): The input factual statement to decompose.
        model (str): Model name to use for completion (default: gpt-3.5-turbo-instruct).
        
    Returns:
        List[str]: A list of atomic questions.
    """
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""
Given the following factual statement, break it into individual atomic questions that can be independently verified.

Statement: "{statement}"

Atomic questions:"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that verifies facts by breaking statements into verifiable sub-questions. Please ensure each question can be answered with a yes or no and an answer yes means that the original statement is true and an answer no means that the original statement is false. Please only include items from the statement that are objective facts"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )

    result = response.choices[0].message.content
    questions = [q.strip("- ").strip() for q in result.split("\n") if q.strip()]
    return questions, len(questions)


def decompose_statement_to_questions(
    statement: str,
    use_local: bool = False,
) -> Tuple[List[str], int]:
    """
    Decomposes a factual statement into atomic questions to enable fact-checking.
    By default uses OpenAI, but can use local Mistral model if use_local=True.
    
    Args:
        statement (str): The input factual statement to decompose.
        use_local (bool): If True, use local Mistral model. If False, use OpenAI.
        
    Returns:
        Tuple[List[str], int]: A list of atomic questions and count.
    """
    if use_local:
        return decompose_statement_to_questions_mistral(statement)
    else:
        return decompose_statement_to_questions_openai(statement)


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


def decompose_statement_to_questions_mistral(
    statement: str,
) -> Tuple[List[str], int]:
    """
    Decomposes a factual statement into atomic questions using local Mistral model.
    
    Args:
        statement (str): The input factual statement to decompose.
        
    Returns:
        Tuple[List[str], int]: A list of atomic questions and count.
    """
    model, tokenizer = load_mistral_model()
    
    if model is None or tokenizer is None:
        print("Mistral model not available, falling back to OpenAI")
        return decompose_statement_to_questions_openai(statement)
    
    # Create the prompt
    system_prompt = "You are a helpful assistant that verifies facts by breaking statements into verifiable sub-questions. Please ensure each question can be answered with a yes or no and an answer yes means that the original statement is true and an answer no means that the original statement is false. Please only include items from the statement that are objective facts"
    
    user_prompt = f"""Given the following factual statement, break it into individual atomic questions that can be independently verified.

Statement: "{statement}"

Atomic questions:"""
    
    # Format messages for Mistral
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Apply chat template
    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    except Exception as e:
        print(f"Warning: apply_chat_template failed: {e}")
        # Fallback: create prompt manually
        prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt")
    # Move to device if available
    if hasattr(model, 'device'):
        inputs = {k: v.to(model.device) if hasattr(v, 'to') else v for k, v in inputs.items()}
    
    # Generate
    # Set up generation parameters
    generation_kwargs = {
        "max_new_tokens": 300,
        "temperature": 0.7,
        "do_sample": True,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
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
    
    # Debug: print full output
    print(f"\nDebug: Full generated text length: {len(generated_text)}")
    print(f"Debug: Prompt length: {len(prompt)}")
    
    # Extract the generated part (after the input prompt)
    result = generated_text[len(prompt):].strip()
    
    print(f"Debug: Extracted result: {result[:200]}...")
    
    # Parse questions
    questions = [q.strip("- ").strip() for q in result.split("\n") if q.strip()]
    
    # Debug: print questions
    print(f"Debug: Parsed {len(questions)} questions")
    
    return questions, len(questions)

# Example usage
if __name__ == "__main__":
    test_statement = "Virat Kohli is the 21st Prime Minister of India"
    
    print("Testing with OpenAI (default):")
    atomic_questions, count = decompose_statement_to_questions(test_statement, use_local=False)
    for idx, q in enumerate(atomic_questions, 1):
        print(f"{idx}. {q}")
    
    # print("\nTesting with Mistral (if available):")
    # atomic_questions, count = decompose_statement_to_questions(test_statement, use_local=True)
    # for idx, q in enumerate(atomic_questions, 1):
    #     print(f"{idx}. {q}")
