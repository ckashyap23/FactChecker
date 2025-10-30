# Fact Checker - Decoupled Architecture

A Python tool for processing statements from CSV files and extracting factual claims by removing subjective language. The system is built with a **decoupled architecture** where each function can be used independently.

## 🏗️ Architecture

The system is built with a **modular architecture** where each core function is in its own module:

### **Core Modules**
- `extract_subject.py` - Subject extraction functionality
- `extract_predicate.py` - Predicate extraction functionality  
- `transform_claim.py` - Factual claim transformation functionality
- `fact_checker.py` - Main orchestration and CSV processing

Each module can be used independently and is designed for easy integration into MCP servers or other systems.

### **Function Organization**

### **Utility Functions**
- `load_spacy_model()` - Load NLP model
- `validate_csv_file()` - Validate CSV file existence
- `clean_text()` - Clean and normalize text
- `is_empty_statement()` - Check for empty statements

### **CSV Processing Functions**
- `read_csv_file()` - Read CSV file into memory
- `extract_statement_from_row()` - Extract statement from CSV row
- `process_csv_row()` - Process single CSV row

### **Subject Extraction Functions**
- `extract_subject()` - Main subject extraction function
- `extract_subject_with_spacy()` - spaCy-based extraction
- `extract_subject_fallback()` - Heuristic-based fallback

### **Predicate Extraction Functions**
- `extract_predicate()` - Main predicate extraction function
- `extract_predicate_with_spacy()` - spaCy-based extraction
- `extract_predicate_fallback()` - Heuristic-based fallback

### **Transformation Functions**
- `transform_factual_claim()` - Main transformation function
- `get_subjective_patterns()` - Get regex patterns for subjective phrases
- `remove_subjective_phrases()` - Remove subjective phrases
- `clean_transformed_text()` - Clean up transformed text

### **Main Processing Functions**
- `process_statements_from_csv()` - Complete CSV processing pipeline
- `save_results_to_csv()` - Save results to CSV file

## 🚀 Features

- **Decoupled Functions**: Each function can be used independently
- **CSV Processing**: Reads statements from CSV files
- **Subject Extraction**: Identifies the main subject of each statement
- **Predicate Extraction**: Extracts factual claims about the subject
- **Subjective Language Removal**: Transforms statements by removing opinion-based phrases
- **Error Handling**: Robust error handling for edge cases
- **Fallback Support**: Works with or without spaCy

## 📦 Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Download the spaCy English model (optional):
```bash
python -m spacy download en_core_web_sm
```

## 🔌 MCP Server Integration

The modular design makes it easy to expose these functions as tools in an MCP server:

### **Available Tools**
- `extract_subject` - Extract subject from statements
- `extract_predicate` - Extract predicate from statements  
- `transform_factual_claim` - Transform statements by removing subjective language
- `process_statements_from_csv` - Process CSV files with statements

### **Example MCP Tool Definition**
```python
# Each module can be imported and used as MCP tools
from extract_subject import extract_subject
from extract_predicate import extract_predicate
from transform_claim import transform_factual_claim

# These functions can be directly exposed as MCP tools
# with proper input/output schemas
```

## 💻 Usage

### **Method 1: Using Decoupled Functions (Recommended)**

```python
from fact_checker import (
    extract_subject, extract_predicate, transform_factual_claim,
    process_statements_from_csv, save_results_to_csv, load_spacy_model
)

# Load NLP model (optional)
nlp_model = load_spacy_model()

# Process individual statement
statement = "I think climate change is definitely a serious problem"
subject = extract_subject(statement, nlp_model)
predicate = extract_predicate(statement, nlp_model)
transformed = transform_factual_claim(statement)

print(f"Subject: {subject}")
print(f"Predicate: {predicate}")
print(f"Transformed: {transformed}")

# Process CSV file
results = process_statements_from_csv('sample_statements.csv')
save_results_to_csv(results, 'output.csv')
```

### **Method 2: Using Legacy Class (Backward Compatibility)**

```python
from fact_checker import FactChecker

# Initialize the fact checker
fact_checker = FactChecker()

# Process statements from CSV
results = fact_checker.read_statements_from_csv('sample_statements.csv')

# Save results
fact_checker.save_results(results, 'processed_statements.csv')
```

### **CSV Format**

Your CSV file should have a column named 'statement' (or specify a different column name):

```csv
statement,category,source
"The Earth revolves around the Sun",astronomy,textbook
"I think climate change is definitely a serious problem",environment,opinion
```

### **Example Output**

For each statement, the tool extracts:
- **Subject**: The main entity being discussed
- **Predicate**: The factual claim about the subject
- **Transformed Claim**: The statement with subjective phrases removed

Example:
- Original: "I think climate change is definitely a serious problem"
- Subject: "climate change" 
- Predicate: "is a serious problem"
- Transformed: "climate change is a serious problem"

## 🧪 Testing

Run the main script to see example usage:

```bash
python fact_checker.py
```

## 📁 File Structure

```
FactChecker/
├── fact_checker.py              # Main module with CSV processing and orchestration
├── extract_subject.py            # Subject extraction functions
├── extract_predicate.py          # Predicate extraction functions
├── transform_claim.py            # Factual claim transformation functions
├── sample_statements.csv         # Sample data
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## 🔧 Dependencies

- **spacy**: For advanced NLP processing (optional)
- **pandas**: For data manipulation (optional)
- **nltk**: For additional text processing (optional)

## 🛡️ Error Handling

The system includes robust error handling:
- **File validation**: Checks CSV file existence
- **Empty statement handling**: Handles empty or whitespace-only statements
- **Fallback mechanisms**: Works without spaCy using heuristic methods
- **Graceful degradation**: Continues processing even if individual statements fail

## 🔄 Fallback Mode

If spaCy is not available, the tool automatically uses simpler heuristic-based methods for extraction, ensuring the system works in any environment.
