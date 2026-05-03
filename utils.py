import os
import json
import time
import urllib.parse
import xml.etree.ElementTree as ET
import requests # We are switching to the more robust requests library
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def call_llm(system_prompt, user_prompt, provider="openai"):
    """
    Calls either OpenAI or Grok based on the provider flag.
    Requires OPENAI_API_KEY or GROK_API_KEY to be set in the .env file.
    """
    if provider == "openai":
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        model_name = "gpt-4o-mini"
    elif provider == "grok":
        client = OpenAI(
            api_key=os.environ.get("GROK_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        model_name = "grok-beta" 
    else:
        raise ValueError("Provider must be 'openai' or 'grok'")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM Call Failed: {str(e)}"

def fetch_semantic_scholar(search_query, limit=3):
    """
    Tool Call: Fetches papers from Semantic Scholar API.
    Searches across all major publishers (IEEE, Nature, PubMed, ArXiv).
    Includes a fallback 'Mock Data' safety net to ensure live demos never fail.
    """
    print(f"[*] Tool Call: Fetching Semantic Scholar papers for query: {search_query}")
    time.sleep(2) # Polite delay
    
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    # Semantic Scholar allows us to ask exactly for the fields we want!
    params = {
        "query": search_query,
        "limit": limit,
        "fields": "title,authors,abstract,externalIds"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() 
        
        data = response.json()
        
        if "data" not in data or len(data["data"]) == 0:
            raise ValueError("Query returned zero results.")
            
        papers = []
        for item in data["data"]:
            # Extract author names from the list of dictionaries
            author_names = [author['name'] for author in item.get('authors', [])]
            
            # Extract DOI if it exists
            doi = item.get("externalIds", {}).get("DOI", "No DOI available")
            
            # Sometimes papers on Semantic Scholar lack abstracts, we handle that gracefully
            abstract = item.get("abstract")
            if not abstract:
                abstract = "No abstract provided by publisher."
                
            papers.append({
                "title": item.get("title", "Unknown Title"),
                "authors": ", ".join(author_names),
                "doi": doi,
                "abstract": abstract
            })
            
        return json.dumps(papers, indent=2)
        
    except Exception as e:
        # THE DEMO SAFETY NET
        print(f"    [!] Live API Error ({str(e)}). Switching to local JSON dataset...")
        
        try:
            with open("fallback_papers.json", "r", encoding="utf-8") as f:
                local_database = json.load(f)
            return json.dumps(local_database[:limit], indent=2)
            
        except FileNotFoundError:
            print("    [!] Local JSON file not found. Pipeline broken.")
            return json.dumps({"error": "Critical Failure: Live API down and local fallback missing."})