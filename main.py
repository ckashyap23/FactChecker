import csv
import re
import spacy
from typing import List, Dict, Tuple, Optional, Union
import os
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('config.env')

# Get the Tavily API key
tavily_api_key = os.getenv('TAVILY_API_KEY')

if tavily_api_key:
    print("Tavily API key loaded successfully!")
    # Your code here
else:
    print("Please set your TAVILY_API_KEY in the config.env file")

# Import functions from separate modules
from extract_components import extract_components, load_spacy_model
from subjective_claim import (
    detect_subjectivity, get_subjective_patterns, get_opinion_words
)
from checker import check_statement



def validate_csv_file(csv_file_path: str) -> bool:
    """Validate that the CSV file exists and is readable."""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            return True
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error validating CSV file: {e}")
        return False


def validate_statement_column(row: Dict, statement_column: str) -> bool:
    """Validate that the statement column exists in the CSV row."""
    if statement_column not in row:
        print(f"Warning: Column '{statement_column}' not found in CSV. Available columns: {list(row.keys())}")
        return False
    return True


def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    return text.strip()


def is_empty_statement(statement: str) -> bool:
    """Check if statement is empty or contains only whitespace."""
    return not statement or not statement.strip()


# =============================================================================
# CSV PROCESSING FUNCTIONS
# =============================================================================

def read_csv_file(csv_file_path: str) -> List[Dict]:
    """Read CSV file and return list of rows."""
    if not validate_csv_file(csv_file_path):
        return []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []


def extract_statement_from_row(row: Dict, statement_column: str) -> Optional[str]:
    """Extract and clean statement from CSV row."""
    if not validate_statement_column(row, statement_column):
        return None
    
    statement = clean_text(row[statement_column])
    if is_empty_statement(statement):
        return None
    
    return statement


def process_csv_row(row: Dict, row_number: int, statement_column: str, 
                   nlp_model: Optional[spacy.Language] = None) -> Optional[Dict]:
    """Process a single CSV row through statement checking."""
    statement = extract_statement_from_row(row, statement_column)
    if not statement:
        return None
    
    try:
        # Check statement using checker.py
        is_factual = check_statement(statement)
        
        # Comment out extract_components call
        # subject, predicate = extract_components(statement, nlp_model)
        
        result = {
            'row_number': row_number,
            'original_statement': statement,
            'is_factual': is_factual,
            # Commented out subject and predicate extraction
            # 'subject': subject,
            # 'predicate': predicate,
            **row  # Include all original CSV columns
        }
        return result
    except Exception as e:
        print(f"Error processing row {row_number}: {e}")
        return None


# =============================================================================
# MAIN PROCESSING FUNCTIONS
# =============================================================================

def process_statements_from_csv(csv_file_path: str, statement_column: str = 'statement') -> List[Dict]:
    """
    Read statements from a CSV file, filter out subjective statements, 
    and process remaining statements through extraction functions.
    
    Args:
        csv_file_path (str): Path to the CSV file
        statement_column (str): Name of the column containing statements
        
    Returns:
        List[Dict]: List of processed factual statements with extracted components
    """
    # Load NLP model
    nlp_model = load_spacy_model()
    
    # Read CSV file
    csv_rows = read_csv_file(csv_file_path)
    if not csv_rows:
        return []
    
    # Filter out subjective statements first
    factual_rows = []
    subjective_count = 0
    
    for row_num, row in enumerate(csv_rows, start=1):
        statement = extract_statement_from_row(row, statement_column)
        if statement:
            if detect_subjectivity(statement):
                subjective_count += 1
                print(f"Row {row_num}: Dropped subjective statement - '{statement}'")
            else:
                factual_rows.append((row_num, row))
    
    print(f"Filtered out {subjective_count} subjective statements")
    print(f"Processing {len(factual_rows)} factual statements")
    
    # Process only factual statements
    processed_statements = []
    
    for row_num, row in factual_rows:
        result = process_csv_row(row, row_num, statement_column, nlp_model)
        
        if result:
            processed_statements.append(result)
    
    return processed_statements


# =============================================================================
# OUTPUT FUNCTIONS
# =============================================================================

def save_results_to_csv(results: List[Dict], output_file: str = 'processed_statements.csv') -> bool:
    """
    Save the processed results to a CSV file.
    
    Args:
        results (List[Dict]): The processed statements
        output_file (str): Output CSV file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not results:
        print("No results to save.")
        return False
    
    fieldnames = ['row_number', 'original_statement', 'is_factual']
    
    # Add any additional columns from the original CSV
    if results:
        additional_fields = set(results[0].keys()) - set(fieldnames)
        fieldnames.extend(sorted(additional_fields))
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Results saved to '{output_file}'")
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False


# =============================================================================
# LEGACY CLASS WRAPPER (for backward compatibility)
# =============================================================================

class FactChecker:
    def __init__(self):
        """Initialize the FactChecker with spaCy model for NLP processing."""
        self.nlp = load_spacy_model()
    
    def read_statements_from_csv(self, csv_file_path: str, statement_column: str = 'statement') -> List[Dict]:
        """Legacy method that calls the new decoupled function."""
        return process_statements_from_csv(csv_file_path, statement_column)
    
    def extract_subject(self, statement: str) -> str:
        """Legacy method that returns subject using merged extractor."""
        subject, _ = extract_components(statement, self.nlp)
        return subject
    
    def extract_predicate(self, statement: str) -> str:
        """Legacy method that returns predicate using merged extractor."""
        _, predicate = extract_components(statement, self.nlp)
        return predicate
    
    def detect_subjectivity(self, statement: str) -> bool:
        """Legacy method that calls the new decoupled function."""
        return detect_subjectivity(statement)
    
    def save_results(self, results: List[Dict], output_file: str = 'processed_statements.csv'):
        """Legacy method that calls the new decoupled function."""
        return save_results_to_csv(results, output_file)
    
# =============================================================================
# MAIN FUNCTION
# =============================================================================

if __name__ == "__main__":
    # Process statements from CSV using decoupled functions
    results = process_statements_from_csv('sample_statements.csv')
    
    if results:
        print(f"Processed {len(results)} statements:")
        print("-" * 80)
        
        for result in results[:3]:  # Show first 3 results
            print(f"Row {result['row_number']}:")
            print(f"Original: {result['original_statement']}")
            print(f"Is Factual: {result['is_factual']}")
            print("-" * 40)
        
        # Save results using decoupled function
        save_results_to_csv(results)
    else:
        print("No statements processed. Please check your CSV file.")
