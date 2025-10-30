import search_results
import break_statement

def check_statement(statement: str, use_local: bool = False) -> bool:
    """
    Check if a statement is factual.
    
    Args:
        statement (str): The statement to check.
        use_local (bool): If True, use local Mistral model. If False, use OpenAI.
        
    Returns:
        bool: True if statement is factual, False otherwise.
    """
    questions, num_questions = break_statement.decompose_statement_to_questions(statement, use_local=use_local)
    for question in questions:
            if search_results.yes_no(question, use_local=use_local) == "No":
                return False
    return True

if __name__ == "__main__":
    print("Testing with OpenAI:")
    print(check_statement("Virat Kohli is the 21st Prime Minister of India", use_local=False))
    # print("\nTesting with Mistral:")
    # print(check_statement("Virat Kohli is the 21st Prime Minister of India", use_local=True))