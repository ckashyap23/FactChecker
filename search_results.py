import os
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Optional, List
import requests
import json
from openai import OpenAI

load_dotenv('config.env')

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

def yes_no (question: str) -> str:
    """
    Returns True if the question is answered with a yes and False if the question is answered with a no.
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


# 🔍 Test the function directly when running this script
if __name__ == "__main__":
    # tavily_search(
    #     query="which is the best LLM model",
    #     # max_results=3,
    #     # search_depth="basic",
    #     # include_answer=True,
    #     # include_raw_content=False,
    #     # print_output=True
    # )
    print(yes_no("Is VIrat Kohli the Prime Minister of India?"))