# Mistral Integration Guide

This document explains the local Mistral model integration with the FactChecker project.

## Overview

The project now supports two modes:
1. **OpenAI mode** (default): Uses OpenAI API for LLM operations
2. **Local Mistral mode**: Uses locally downloaded Mistral-7B-Instruct-v0.3 model

## Download Status

**Current Status**: ⚠️ **Partially downloaded** - One model file is missing

### Files Downloaded
- ✅ Configuration files (config.json, tokenizer.json, etc.)
- ✅ README and documentation
- ✅ Model directory structure
- ✅ `model-00002-of-00003.safetensors` (4.66 GB)
- ✅ `model-00003-of-00003.safetensors` (4.23 GB)
- ❌ `model-00001-of-00003.safetensors` (~5 GB) **MISSING**

### Expected Model Files
- ✅ `model-00002-of-00003.safetensors` (4.66 GB)
- ✅ `model-00003-of-00003.safetensors` (4.23 GB)
- ❌ `model-00001-of-00003.safetensors` (~5 GB) **MISSING**

**Downloaded**: 8.89 GB / **Total**: ~14.5 GB

To complete the download, run: `python download_model.py`

## Model Path Resolution

The system automatically resolves the model path to ensure it loads from the correct location:

- **Base path**: `models/Mistral-7B-Instruct-v0.3` (relative to project root)
- **Absolute path**: Automatically resolved using `Path().resolve()`
- **Works from any directory**: The path is resolved from the project root

### Pre-Load Checks

Before attempting to load the model, the system performs several checks:

1. **Directory existence**: Verifies the model directory exists
2. **Required files**: Checks for essential files (config.json, tokenizer.json)
3. **Graceful fallback**: Falls back to OpenAI if checks fail

### Error Messages

You'll see helpful error messages if the model isn't properly set up:

```
Error: Model directory not found at C:\...\models\Mistral-7B-Instruct-v0.3
Please run: python download_model.py
Falling back to OpenAI...
```

## Completing the Download

To complete the model download, run:

```bash
python download_model.py
```

Make sure you have:
1. Hugging Face token set in `HF_TOKEN` environment variable or provided via `--token`
2. Sufficient disk space (~15 GB)
3. Stable internet connection

## Updated Functions

### break_statement.py

#### New Functions:
- `decompose_statement_to_questions_openai()`: Original OpenAI implementation
- `decompose_statement_to_questions_mistral()`: Local Mistral implementation
- `load_mistral_model()`: Loads and caches the Mistral model

#### Modified Function:
- `decompose_statement_to_questions()`: Now accepts `use_local` parameter
  ```python
  questions, count = decompose_statement_to_questions(
      statement, 
      use_local=False  # Set to True for local Mistral
  )
  ```

### search_results.py

#### New Functions:
- `yes_no_openai()`: Original OpenAI implementation
- `yes_no_mistral()`: Local Mistral implementation
- `load_mistral_model()`: Loads and caches the Mistral model

#### Modified Function:
- `yes_no()`: Now accepts `use_local` parameter
  ```python
  answer = yes_no(
      question, 
      use_local=False  # Set to True for local Mistral
  )
  ```

### checker.py

#### Modified Function:
- `check_statement()`: Now accepts `use_local` parameter
  ```python
  is_factual = check_statement(
      statement, 
      use_local=False  # Set to True for local Mistral
  )
  ```

## Usage Examples

### Using OpenAI (Default)
```python
from checker import check_statement

result = check_statement("Virat Kohli is the 21st Prime Minister of India")
```

### Using Local Mistral
```python
from checker import check_statement

result = check_statement(
    "Virat Kohli is the 21st Prime Minister of India",
    use_local=True
)
```

### Direct Function Calls
```python
from break_statement import decompose_statement_to_questions
from search_results import yes_no

# With OpenAI
questions, count = decompose_statement_to_questions(statement, use_local=False)
answer = yes_no(question, use_local=False)

# With Mistral
questions, count = decompose_statement_to_questions(statement, use_local=True)
answer = yes_no(question, use_local=True)
```

## Dependencies

The following dependencies were added to support Mistral:

- `transformers>=4.30.0`: Hugging Face transformers library
- `torch>=2.0.0`: PyTorch for model inference
- `accelerate>=0.20.0`: Hugging Face accelerate for device mapping
- `safetensors>=0.3.0`: SafeTensors format support

Install with:
```bash
pip install -r requirements.txt
```

## Fallback Behavior

If the Mistral model fails to load (e.g., incomplete download), the functions automatically fall back to OpenAI with a warning message.

## Model Loading

The Mistral model is loaded on first use and cached in memory using global variables. This means:
- First call to `use_local=True` will take time to load (~30 seconds)
- Subsequent calls are fast as the model stays in memory
- Model uses ~14GB RAM when loaded

## Hardware Requirements

For optimal performance with local Mistral:
- **RAM**: 16GB minimum (32GB recommended)
- **GPU**: NVIDIA GPU with 16GB+ VRAM recommended
- **Storage**: 15GB free space for model files

Without a GPU, the model will run on CPU but will be significantly slower.

