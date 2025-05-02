from openai import OpenAI
import os
import json
import re
import numpy as np
# Add imports for error handling
import sys
import time

# ── Configuration ───────────────────────────────────────────────────────────
# Load API key from environment variable for security
# Ensure you set the environment variable before running:
# export OPENAI_API_KEY='your-api-key-here'
# or if using a .env file, load it at the start of your script.
client = OpenAI(api_key='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')


# Using newer embedding model
EMBED_MODEL    = "text-embedding-3-small"
# Using chat completion model
DECODER_MODEL  = "gpt-3.5-turbo"

# SIM_THRESHOLD is less critical if we always take Top N candidates for the LLM
# It could be used later for post-processing or confidence scoring if needed.
# Let's keep it for now, but the candidate selection logic will prioritize TOP N.
SIM_THRESHOLD  = 0.3 # You might tune this or remove its effect on candidate selection
CAND_TOP_N     = 10  # Always pass the top 10 principles based on similarity to the LLM
MAX_TOKENS     = 200
TEMPERATURE    = 0.2

# ── Load Principles and Claims ───────────────────────────────────────────────
def load_data(principles_path, claims_path):
    """Loads TRIZ principles and patent data from JSON files."""
    principles = []
    patents = []
    try:
        with open(principles_path, 'r', encoding='utf-8') as f:
            principles = json.load(f)
        with open(claims_path, 'r', encoding='utf-8') as f:
            patents = json.load(f)
        print(f"Loaded {len(principles)} principles and {len(patents)} patents.")
    except FileNotFoundError as e:
        print(f"Error loading data file: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in data file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}", file=sys.stderr)
        sys.exit(1)

    return principles, patents

# ── Embedding Helper ─────────────────────────────────────────────────────────
def embed_texts(texts, model=EMBED_MODEL, max_retries=3, delay=5):
    """Generates embeddings for a list of texts with retry logic."""
    if not texts:
        return np.array([], dtype=np.float32) # Return empty array for empty input

    for attempt in range(max_retries):
        try:
            # Ensure input texts are strings
            string_texts = [str(text) for text in texts]
            resp = client.embeddings.create(model=model, input=string_texts)
            # Validate that the number of embeddings matches the input texts
            if len(resp.data) != len(texts):
                 print(f"Warning: Embedding response data count mismatch. Expected {len(texts)}, got {len(resp.data)}", file=sys.stderr)
                 # Attempt to return partial results if possible, or raise error
                 # For now, let's raise to be safe, or handle as needed
                 raise ValueError(f"Embedding response data count mismatch: {len(resp.data)} != {len(texts)}")

            return np.array([d.embedding for d in resp.data], dtype=np.float32)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to get embeddings: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(delay) # Wait before retrying
            else:
                print("Max retries reached for embedding texts.", file=sys.stderr)
                raise # Re-raise the last exception

def cosine_sim(a, b):
    """Calculates cosine similarity between two vectors."""
    # Add a small epsilon to denominators to prevent division by zero for zero vectors
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0 # Cosine similarity is undefined, return 0 or NaN depending on convention
    return np.dot(a, b) / (norm_a * norm_b)

# ── Prompt Builder (for Chat Model) ──────────────────────────────────────────
def build_messages(claim_text, candidate_principles):
    """Builds the messages list for the chat model."""
    system_message = {
        "role": "system",
        "content": "You are an expert at mapping patent claims to TRIZ principles. Analyze the action and technical contradiction described in the patent claim. Choose ONLY from the listed TRIZ principles below that *directly apply*. If none of the listed principles apply, answer 'None'. List the principle numbers ONLY, separated by commas (e.g., '1, 5, 10'). Do NOT include principle names or descriptions in the answer."
    }

    user_content = f"Claim: \"\"\"{claim_text.strip()}\"\"\"\n\nListed Principles:\n"

    for p in candidate_principles:
        try:
            principle_number = int(p.get('number', 0))
        except (ValueError, TypeError):
             principle_number = 0
             print(f"Warning: Invalid principle number found: {p.get('number')}", file=sys.stderr)

        example_note = p.get('Example', '')
        description = p.get('description', 'No description provided.')
        note = f" Example: {example_note}" if example_note else ''
        user_content += f"{principle_number}: {p.get('name', 'Unnamed Principle')} - {description}{note}\n"

    user_content += "\nAnswer:"

    user_message = {
        "role": "user",
        "content": user_content
    }

    return [system_message, user_message]


# ── Chat Model-Based Labeler ────────────────────────────────────────────────────
def label_claim_with_chat_model(claim_text, principles, princ_embs):
    """Labels a claim using the chat model and candidate principles."""
    if not claim_text.strip():
        print("Warning: Empty claim text provided.", file=sys.stderr)
        return [] # Return empty list for empty claims

    # Calculate similarity to all principles
    try:
        claim_emb = embed_texts([claim_text])[0]
        sims = [cosine_sim(claim_emb, pe) for pe in princ_embs]
    except Exception as e:
        print(f"Error generating claim embedding or calculating similarities: {e}", file=sys.stderr)
        return [] # Return empty list on embedding/sim error

    # Always select the top CAND_TOP_N principles based on similarity
    top_n_indices = np.argsort(sims)[-min(CAND_TOP_N, len(sims)):]
    top_n_indices = sorted(top_n_indices) # Sort indices for consistent prompt order

    candidates = [principles[i] for i in top_n_indices]

    if not candidates:
        print(f"Warning: No principle candidates selected for claim: {claim_text[:50]}...", file=sys.stderr)
        return []

    # Build messages for the chat model
    messages = build_messages(claim_text, candidates)

    try:
        # Use chat.completions.create for chat models
        resp = client.chat.completions.create(
            model=DECODER_MODEL,
            messages=messages, # Pass messages list
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            # stop=["\n"] # Stop sequence might not be needed/work the same way in chat models
        )
        # Extract content from the chat model response
        out = resp.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error calling OpenAI chat completions API for claim: {e}", file=sys.stderr)
        print(f"Claim text: {claim_text[:100]}...", file=sys.stderr) # Log part of the claim
        return [] # Return empty list on API error

    # --- Output Parsing ---
    # Expect output format like "1, 5, 10" or "None"
    if out.lower().startswith('none'):
        return [] # Return empty list if LLM says None

    principle_numbers = set()
    # Find all numbers in the output string
    found_numbers_str = re.findall(r"\d+", out)
    for num_str in found_numbers_str:
        try:
            principle_number = int(num_str)
            principle_numbers.add(principle_number)
        except ValueError:
            print(f"Warning: Could not parse number from LLM output segment: '{num_str}'", file=sys.stderr)

    # Return sorted list of unique principle numbers
    return sorted(list(principle_numbers))

# ── Main Annotation ──────────────────────────────────────────────────────────
def annotate(principles_path="triz_principles.json", claims_path="result.json", output_path="claim_level_triz_output.json"):
    """Main function to load data, annotate claims, and save results."""
    principles, patents = load_data(principles_path, claims_path)

    # Generate embeddings for principles ONCE
    # Filter out principles that might be missing 'name' or 'description' or number
    valid_principles = [p for p in principles if p.get('name') and p.get('description') and p.get('number') is not None]
    if len(valid_principles) < len(principles):
        print(f"Warning: Filtered out {len(principles) - len(valid_principles)} principles missing name, description, or number.", file=sys.stderr)

    princ_texts = [f"{p['name']}. {p['description']}" for p in valid_principles]

    if not princ_texts:
        print("Error: No valid principles found to embed.", file=sys.stderr)
        sys.exit(1)

    try:
        print("Generating embeddings for principles...")
        princ_embs = embed_texts(princ_texts)
        print("Principle embeddings generated.")
    except Exception as e:
        print(f"Fatal Error: Could not generate embeddings for principles: {e}", file=sys.stderr)
        sys.exit(1)


    all_claim_entries = []
    # Regex to split claims starting with a number followed by a dot and optional space
    # Added negative lookbehind (?<!\d) to avoid splitting on numbers within text
    split_re = re.compile(r'(?<!\d)\d+\.\s*')

    total_claims_processed = 0
    for pat_index, pat in enumerate(patents):
        # Use .get for safe access to nested dictionaries
        title = pat.get("essential_data", {}).get("title", f"Untitled Patent {pat_index + 1}")
        raw_claims = pat.get("claims", "")

        if not raw_claims.strip():
            print(f"Skipping patent '{title}': No claims found.")
            continue

        # Split claims and handle the potential empty first element
        claims_list = split_re.split(raw_claims)
        if claims_list and not claims_list[0].strip():
             claims_list = claims_list[1:]

        claims = [c.strip() for c in claims_list if c.strip()]

        if not claims:
             print(f"Warning: Could not split claims for patent '{title}'. Raw claims:\n{raw_claims[:200]}...")
             continue # Skip this patent if claims couldn't be split

        print(f"\nProcessing patent: {title} with {len(claims)} claims.")

        for idx, claim in enumerate(claims, start=1):
            total_claims_processed += 1
            print(f"  Annotating '{title}' — claim {idx}...")
            # Use the chat model labeling function
            assigned_principles = label_claim_with_chat_model(claim, valid_principles, princ_embs)
            all_claim_entries.append({
                "patent_title": title,
                "claim_index": idx,
                "claim_text": claim,
                "principles": assigned_principles
            })
            print(f"  ✓ Claim {idx}: labeled principles {assigned_principles}")
            # Add a small delay to avoid hitting API rate limits
            time.sleep(1)

    # Save results to JSON file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_claim_entries, f, indent=2)
        print(f"\nAnnotation complete.")
        print(f"Processed {total_claims_processed} claims.")
        print(f"Wrote {len(all_claim_entries)} annotated claim-level entries to {output_path}")
    except IOError as e:
        print(f"Error writing output file {output_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while writing output: {e}", file=sys.stderr)


if __name__ == "__main__":
    # Ensure your triz_principles.json and result.json files are in the same directory
    # or provide the correct paths here.
    annotate()
