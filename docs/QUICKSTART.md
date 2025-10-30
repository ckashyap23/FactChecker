# Quick Start Guide

This guide will help you get started with the updated FactChecker that supports both OpenAI and local Mistral models.

## Current Status

### ✅ What's Complete
- ✅ Code updated to support both OpenAI and Mistral
- ✅ Backward compatible (OpenAI still works as before)
- ✅ Documentation created
- ⚠️ Mistral model download incomplete (needs ~14.5GB)
- ⚠️ Dependencies need to be installed

## Installation Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- OpenAI API client
- Hugging Face transformers
- PyTorch
- And other required libraries

### Step 2A: Use OpenAI (Easiest)
If you already have an OpenAI API key, you can start using the system immediately:

```bash
# Make sure your config.env has the API key
python main.py
```

That's it! The system works as before.

### Step 2B: Download Mistral Model (Optional)
To use the local Mistral model instead:

1. **Get Hugging Face Token**:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token
   - Copy the token

2. **Set the token**:
   ```bash
   # Option 1: Environment variable
   set HF_TOKEN=your_token_here  # Windows
   export HF_TOKEN=your_token_here  # Linux/Mac
   
   # Option 2: Add to config.env (recommended)
   echo HF_TOKEN=your_token_here >> config.env
   ```

3. **Download the model**:
   ```bash
   python download_model.py
   ```
   
   This will download ~14.5GB. Time depends on your internet speed.

4. **Verify download**:
   ```bash
   python checker.py
   ```
   
   You should see it loading the Mistral model and running tests.

## Usage

### Basic Usage with OpenAI (Default)
```python
from checker import check_statement

# Uses OpenAI by default
result = check_statement("The Earth is flat")
print(f"Result: {'Factual' if result else 'Not Factual'}")
```

### Usage with Local Mistral
```python
from checker import check_statement

# Uses local Mistral model
result = check_statement("The Earth is flat", use_local=True)
print(f"Result: {'Factual' if result else 'Not Factual'}")
```

### Compare Both
```python
from checker import check_statement

statement = "Virat Kohli is the Prime Minister of India"

print("OpenAI result:", check_statement(statement, use_local=False))
print("Mistral result:", check_statement(statement, use_local=True))
```

## What Each Function Does

### `check_statement(statement, use_local=False)`
- Main entry point for checking facts
- Breaks statement into questions
- Evaluates each question
- Returns True if all are factual, False otherwise

### `decompose_statement_to_questions(statement, use_local=False)`
- Breaks a statement into atomic questions
- Returns list of questions and count

### `yes_no(question, use_local=False)`
- Evaluates a single yes/no question
- Uses Tavily search to get context
- Returns "Yes" or "No"

## Troubleshooting

### "ModuleNotFoundError: No module named 'transformers'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "Error loading Mistral model"
**Solution**: Model not downloaded or incomplete
```bash
python download_model.py
```

### "Mistral model not available, falling back to OpenAI"
**Solution**: Model download incomplete. Check that you have all model-*.safetensors files

### Mistral is very slow
**Solution**: Normal for CPU. Consider:
- Using GPU (CUDA-enabled PyTorch)
- Using OpenAI instead
- Reducing generation max_tokens

### "CUDA out of memory"
**Solution**: GPU doesn't have enough VRAM
- Model needs ~14GB VRAM or RAM
- Try CPU mode instead
- Or use OpenAI

## Performance Expectations

### OpenAI
- ✅ Fast (API calls)
- ✅ Good quality
- ❌ Costs money
- ❌ Requires internet

### Local Mistral
- ✅ Free to run
- ✅ No internet needed
- ✅ Privacy (data stays local)
- ❌ Slow on CPU (~10-30 seconds per query)
- ❌ Needs 16GB+ RAM
- ✅ Much faster on GPU (~2-5 seconds per query)

## Examples

See `USAGE_EXAMPLE.py` for comprehensive examples.

Run it:
```bash
python USAGE_EXAMPLE.py
```

## Need Help?

- Check [MISTRAL_INTEGRATION.md](MISTRAL_INTEGRATION.md) for detailed integration info
- Check [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) for technical details
- Check [README.md](README.md) for general project info

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Test OpenAI: `python checker.py`
3. ⏭️ Download Mistral: `python download_model.py` (optional)
4. ⏭️ Test Mistral: `python checker.py` (should use Mistral if downloaded)

