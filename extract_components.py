#!/usr/bin/env python3
"""
Merged subject and predicate extraction module for fact-checking system.
Extracts both subject and predicate in a single pass to avoid duplicate parsing.
"""

import spacy
from typing import Optional, Tuple


def load_spacy_model():
    """Load spaCy model for NLP processing."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("Warning: spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
        return None


def extract_components_with_spacy(statement: str, nlp_model: spacy.Language) -> Tuple[str, str]:
    """
    Extract both subject and predicate using spaCy NLP model in a single pass.
    
    Args:
        statement (str): The input statement to analyze
        nlp_model (spacy.Language): spaCy NLP model
        
    Returns:
        Tuple[str, str]: (subject, predicate)
    """
    doc = nlp_model(statement)
    
    subject = ""
    predicate_parts = []
    
    # First pass: find subject and main verb
    main_verb = None
    for token in doc:
        # Find main subject (nsubj dependency)
        if token.dep_ == "nsubj" and not token.is_stop:
            subject = token.text
            # Include compound subjects
            for child in token.children:
                if child.dep_ == "compound":
                    subject = f"{child.text} {subject}"
        
        # Find main verb (root or main predicate)
        if token.dep_ in ["ROOT", "ccomp", "xcomp"] and token.pos_ == "VERB":
            main_verb = token
            predicate_parts.append(token.text)
    
    # If no clear subject found, try to find the first noun
    if not subject:
        for token in doc:
            if token.pos_ == "NOUN" and not token.is_stop:
                subject = token.text
                break
    
    # If still no subject, return the first few words
    if not subject:
        words = statement.split()[:3]
        subject = " ".join(words)
    
    # Second pass: build predicate around the main verb
    if main_verb:
        for child in main_verb.children:
            # Direct complements
            if child.dep_ in ("dobj", "attr", "acomp"):
                # Include object + its modifiers in correct order
                mods = [gc for gc in child.children if gc.dep_ in ("amod", "det", "compound")]
                # Sort by token position to preserve word order
                seq = sorted(mods + [child], key=lambda t: t.i)
                predicate_parts.extend(t.text for t in seq)

            # Prepositional phrase off the verb
            if child.dep_ == "prep":
                # Include the preposition itself
                predicate_parts.append(child.text)
                # Include pobj + its modifiers (det/amod/compound) in order
                for gc in child.children:
                    if gc.dep_ == "pobj":
                        mods = [gg for gg in gc.children if gg.dep_ in ("det", "amod", "compound")]
                        seq = sorted(mods + [gc], key=lambda t: t.i)
                        predicate_parts.extend(t.text for t in seq)
    
    # If no clear predicate found, extract everything after the subject
    if not predicate_parts:
        # Simple approach: remove common subject indicators and take the rest
        cleaned = statement
        for word in ['is', 'are', 'was', 'were', 'has', 'have', 'had']:
            if word in cleaned.lower():
                parts = cleaned.lower().split(word, 1)
                if len(parts) > 1:
                    cleaned = parts[1].strip()
                    break
        
        predicate_parts = [cleaned] if cleaned else [statement]
    
    predicate = " ".join(predicate_parts).strip()
    
    return subject, predicate


def extract_components_fallback(statement: str) -> Tuple[str, str]:
    """
    Fallback method to extract both subject and predicate without spaCy.
    
    Args:
        statement (str): The input statement to analyze
        
    Returns:
        Tuple[str, str]: (subject, predicate)
    """
    words = statement.split()
    
    # Extract subject
    subject = ""
    for i, word in enumerate(words):
        if word.lower() not in ['the', 'a', 'an', 'this', 'that', 'these', 'those']:
            # Take 1-3 words starting from this position
            subject_words = words[i:i+3]
            subject = " ".join(subject_words)
            break
    
    # Fallback to first 3 words if no subject found
    if not subject:
        subject = " ".join(words[:3])
    
    # Extract predicate
    subject_indicators = ['the', 'a', 'an', 'this', 'that', 'these', 'those']
    
    # Find where the predicate likely starts (after first noun phrase)
    predicate_start = 0
    for i, word in enumerate(words):
        if word.lower() in subject_indicators:
            predicate_start = i + 1
        elif word.lower() in ['is', 'are', 'was', 'were', 'has', 'have', 'had']:
            predicate_start = i + 1
            break
    
    if predicate_start < len(words):
        predicate = " ".join(words[predicate_start:])
    else:
        predicate = statement
    
    return subject, predicate


def extract_components(statement: str, nlp_model: Optional[spacy.Language] = None) -> Tuple[str, str]:
    """
    Extract both subject and predicate from a statement in a single pass.
    
    Args:
        statement (str): The input statement to analyze
        nlp_model (Optional[spacy.Language]): spaCy NLP model for advanced processing
        
    Returns:
        Tuple[str, str]: (subject, predicate)
    """
    if not statement:
        return "", ""
    
    if nlp_model:
        return extract_components_with_spacy(statement, nlp_model)
    else:
        return extract_components_fallback(statement)


if __name__ == "__main__":
    # Example usage
    test_statements = [
        "The Earth revolves around the Sun",
        "I think climate change is a serious problem",
        "Water boils at 100 degrees Celsius",
        "The company reported record profits",
        "Mount Everest is the highest mountain"
    ]
    
    print("Merged Components Extraction Module - Example Usage")
    print("=" * 60)
    
    # Load NLP model
    nlp_model = load_spacy_model()
    if nlp_model:
        print("✓ spaCy model loaded successfully")
    else:
        print("⚠ Using fallback method (no spaCy model)")
    
    for i, statement in enumerate(test_statements, 1):
        print(f"\n{i}. Statement: {statement}")
        
        # Extract both components in one pass
        subject, predicate = extract_components(statement, nlp_model)
        print(f"   Subject: {subject}")
        print(f"   Predicate: {predicate}")
        
        # Show which method was used
        if nlp_model:
            print(f"   Method: spaCy NLP (single pass)")
        else:
            print(f"   Method: Fallback (single pass)")
