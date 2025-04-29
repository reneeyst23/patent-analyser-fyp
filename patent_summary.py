import os
import json
from dotenv import load_dotenv
from typing import Dict
from openai import OpenAIError, OpenAI

# --- Load environment variables ---
load_dotenv()
openai_client = OpenAI()

# --- Patent Summarization Prompt ---
PATENT_SUMMARIZATION_PROMPT = """
You are an expert technical writer specializing in summarizing patents clearly and concisely.

Your task:
1. Read the patent's Title, Abstract, Description, and Claims provided below.
2. Produce a **structured plain-text summary** that covers:
    - The **main invention** or innovation.
    - The **technical problem** the invention solves.
    - The **key technical features** that make the invention unique.
    - Any **advantages** over existing solutions.

Instructions:
- Write the summary in a clear, professional, but **accessible** manner.
- Limit the output to **200-250 words** maximum.
- Focus on **technical clarity**, not legal phrasing.
- Do not copy sections verbatim — **paraphrase** and **synthesize**.
- Avoid mentioning "this patent" — directly explain the invention.
- No bullet points — use paragraph format.

📝 Input Patent:
Title:
{title}

Abstract:
{abstract}

Description:
{description}

Claims:
{claims}

Output: 
A plain text paragraph summarizing the patent.
"""

# --- Helper Functions ---

def load_patent_json(file_path: str) -> Dict:
    """Load and validate a patent JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

def construct_prompt(patent_data: Dict) -> str:
    """Construct a summarization prompt using relevant patent fields."""
    try:
        title = patent_data.get("essential_data", {}).get("title", "")
        abstract = patent_data.get("essential_data", {}).get("abstract", "")
        claims = patent_data.get("claims", "")
        description = patent_data.get("description", "")

        return PATENT_SUMMARIZATION_PROMPT.format(
            title=title,
            abstract=abstract,
            description=description,
            claims=claims
        )
    except Exception as e:
        raise ValueError(f"Error constructing prompt: {e}")

def summarize_patent(prompt: str) -> str:
    """Call OpenAI API to generate a summary."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {e}")

# --- Main Execution ---

def main(file_path: str):
    try:
        patent_data = load_patent_json(file_path)
        prompt = construct_prompt(patent_data)
        summary = summarize_patent(prompt)
        print("\n--- Patent Summary ---\n")
        print(summary)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example usage
    main("extracted_text.json")