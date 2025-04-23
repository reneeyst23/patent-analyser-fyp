from openai import OpenAI
# Set your OpenAI API key
import os
client = OpenAI(api_key='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')
import os
import json
import numpy as np
from typing import List, Dict
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import re

def load_triz_principles(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def embed_texts(texts: List[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return np.array([r.embedding for r in response.data], dtype=np.float32)
def explain_with_xai(claim: str, selected: List[Dict]) -> List[Dict]:
    explanations = []
    for p in selected:
        user_msg = (
            f"You are a TRIZ expert and explainable AI assistant.\n\n"
            f"Analyze the patent claim below and explain why TRIZ Principle {p['number']} ({p['name']}) applies.\n"
            f"Include:\n"
            f"- A brief explanation\n"
            f"- Supporting text from the claim\n"
            f"Patent Claim:\n\"\"\"\n{claim}\n\"\"\""
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a TRIZ expert specializing in patent analysis."},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.3
            )
            explanation_text = response.choices[0].message.content.strip()
        except Exception as e:
            explanation_text = f"⚠️ Error generating explanation: {e}"

        explanations.append({
            "number": p["number"],
            "name": p["name"],
            "explanation": explanation_text
        })
    return explanations

def filter_relevant_principles(claim_text: str, principles: List[Dict], threshold: float = 0.70) -> List[Dict]:
    principle_texts = [p["description"] for p in principles]
    embeddings = embed_texts([claim_text] + principle_texts)
    claim_vec = embeddings[0].reshape(1, -1)
    prin_vecs = embeddings[1:]
    sims = cosine_similarity(claim_vec, prin_vecs)[0]

    return [
        {
            "number": principles[i]["number"],
            "name": principles[i]["name"],
            "score": float(sims[i])
        }
        for i in range(len(principles)) if sims[i] >= threshold
    ]

if __name__ == "__main__":
    # File paths
    input_file = "result.json"
    principles_file = "triz_principles.json"
    output_file = "triz_output.json"
    threshold = 0.70

    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        patent_docs = json.load(f)
    principles = load_triz_principles(principles_file)

    results = []

    # Analyze each patent entry
    for entry in patent_docs:
        title = entry.get("essential_data", {}).get("title", "Untitled Patent")
        claim_text = entry.get("claims", "").strip()

        if not claim_text:
            print(f"⚠️ Skipping patent '{title}' – no claims found.")
            continue

        print(f" Analyzing: {title}")

        matched_principles = set()

        try:
            MAX_CHARS = 12000
            if len(claim_text) <= MAX_CHARS:
                # Normal path: process whole claim text
                matched = filter_relevant_principles(claim_text, principles, threshold=threshold)
                matched_principles.update((m["number"], m["name"]) for m in matched)
            else:
                print(f"⚠️ Claim too long, splitting into parts for: {title}")
                split_claims = re.split(r'\b\d{1,3}\s*\.', claim_text)
                split_claims = [c.strip() for c in split_claims if c.strip()]

                for idx, split_claim in enumerate(split_claims):
                    if len(split_claim) < 100:  
                        continue
                    try:
                        matched = filter_relevant_principles(split_claim, principles, threshold=threshold)
                        matched_principles.update((m["number"], m["name"]) for m in matched)
                    except Exception as e:
                        print(f"❌ Error analyzing claim {idx+1} in '{title}': {e}")
                        continue

        except Exception as e:
            print(f"❌ Error processing full claim text in '{title}': {e}")
            continue

        principles_cleaned = [{"number": num, "name": name} for num, name in sorted(matched_principles)]

        results.append({
            "title": title,
            "principles": principles_cleaned
        })

    # Write results to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n Saved results to {output_file}")
