from openai import OpenAI
from typing import List, Tuple
from dotenv import load_dotenv
import os

load_dotenv('config.env')

def decompose_statement_to_questions(
    statement: str,
    #model: str = "gpt-4o-mini",
    model: str = "gpt-3.5-turbo-instruct",
) -> Tuple[List[str], int]:
    """
    Decomposes a factual statement into atomic questions to enable fact-checking.
    
    Args:
        statement (str): The input factual statement to decompose.
        model (str): Model name to use for completion (default: gpt-4o-mini).
        
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

# Example usage
if __name__ == "__main__":
    test_statement = "Virat Kohli is the 21st Prime Minister of India"
    atomic_questions = decompose_statement_to_questions(test_statement)
    for idx, q in enumerate(atomic_questions, 1):
        print(f"{idx}. {q}")
