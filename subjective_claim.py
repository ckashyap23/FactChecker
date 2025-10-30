#!/usr/bin/env python3
"""
Factual claim transformation module for fact-checking system.
Transforms statements by removing subjective language and opinions.
"""

import re
from typing import List


def get_subjective_patterns() -> List[str]:
    """Get list of regex patterns for subjective phrases."""
    return [
        r'\b(i think|i believe|i feel|i guess|i suppose|i assume)\b',
        r'\b(in my opinion|in my view|personally|to me)\b',
        r'\b(it seems|it appears|it looks like|it sounds like)\b',
        r'\b(probably|maybe|perhaps|possibly|likely|unlikely)\b',
        r'\b(clearly|obviously|undoubtedly|certainly|definitely)\b',
        r'\b(surprisingly|unfortunately|fortunately|sadly|thankfully)\b',
        r'\b(amazing|incredible|terrible|awful|wonderful|fantastic)\b',
        r'\b(very|extremely|incredibly|absolutely|completely|totally)\b',
        r'\b(always|never|all|every|none|nothing|everything)\b',
        r'\b(should|must|ought to|need to|have to)\b'
    ]


def get_opinion_words() -> List[str]:
    """Get list of opinion words to remove as fallback."""
    return ['think', 'believe', 'feel', 'guess', 'suppose', 'assume', 
            'opinion', 'view', 'personally', 'probably', 'maybe', 'perhaps']

def detect_subjectivity(statement: str) -> bool:
    """
    Detect if a statement contains subjective language or opinions.
    
    Args:
        statement (str): The input statement to analyze
        
    Returns:
        bool: True if subjective language is detected, False otherwise
    """
    if not statement:
        return False
    
    # Check for subjective patterns
    patterns = get_subjective_patterns()
    
    for pattern in patterns:
        if re.search(pattern, statement, flags=re.IGNORECASE):
            return True
    
    # Check for opinion words as fallback
    opinion_words = get_opinion_words()
    words = statement.lower().split()
    
    for word in words:
        if word in opinion_words:
            return True
    
    return False


if __name__ == "__main__":
    # Example usage
    test_statements = [
        "I think climate change is definitely a serious problem",
        "In my opinion, this movie is absolutely fantastic",
        "I believe the new policy will probably help students",
        "This book is obviously the best novel ever written",
        "I guess the weather will be nice tomorrow",
        "The Earth revolves around the Sun",
        "Water boils at 100 degrees Celsius",
        "The company reported record profits this quarter"
    ]
    
    print("Subjectivity Detection Module - Example Usage")
    print("=" * 60)
    
    for i, statement in enumerate(test_statements, 1):
        print(f"\n{i}. Statement: {statement}")
        is_subjective = detect_subjectivity(statement)
        print(f"   Contains subjective language: {is_subjective}")
