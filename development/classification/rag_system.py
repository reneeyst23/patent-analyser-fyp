import json
import os
import numpy as np
import faiss
from collections import defaultdict
from rank_bm25 import BM25Okapi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from keybert import KeyBERT
from openai import OpenAI
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
import hashlib

def compute_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def load_cached_embeddings(chunks, cache_file="embedding_cache.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}

    embeddings = []
    for chunk in chunks:
        chunk_id = compute_md5(chunk)
        if chunk_id in cache:
            embedding = cache[chunk_id]
        else:
            embedding = get_embedding(chunk)  # Call OpenAI API
            cache[chunk_id] = embedding
        embeddings.append(embedding)

    # Save updated cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f)

    return np.array(embeddings).astype('float32')

# Set your API Key securely here:
openai_api_key = "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"
client = OpenAI(api_key=openai_api_key)
llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4-turbo")

kw_model = KeyBERT()
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Efficient summarized memory for chatbot
memory = ConversationSummaryMemory(llm=llm, max_token_limit=500)

TRIZ_KEYWORDS = {
    1: ("Segmentation", ["modular", "segments", "divide", "split", "subsystem", "independent"]),
    2: ("Taking Out", ["removal", "separate", "detach", "extract", "remove"]),
    3: ("Local Quality", ["localized", "specific", "adapted", "targeted", "optimized"]),
    4: ("Asymmetry", ["asymmetric", "imbalance", "non-uniform", "lopsided", "uneven"]),
    5: ("Merging", ["combine", "integrate", "merge", "fuse", "join"]),
    6: ("Universality", ["universal", "multi-purpose", "general", "versatile", "multipurpose"]),
    7: ("Nested Doll", ["nested", "enclosed", "layered", "contained"]),
    8: ("Anti-weight", ["buoyancy", "lift", "counterweight", "lightweight"]),
    9: ("Preliminary Anti-action", ["shield", "delay", "prevention", "buffer"]),
    10: ("Preliminary Action", ["prepare", "preprocess", "preset", "setup"]),
    11: ("Beforehand Cushioning", ["reserve", "backup", "compensation", "redundancy", "cushion"]),
    12: ("Equipotentiality", ["even load", "balanced", "uniform tension", "equalize"]),
    13: ("The Other Way Round", ["reverse", "flip", "invert", "opposite", "turn around"]),
    14: ("Spheroidality – Curvature", ["curve", "round", "sphere", "circular", "arc", "curvature"]),
    15: ("Dynamics", ["adjustable", "flexible", "moving", "variable", "dynamic"]),
    16: ("Partial or Excessive Action", ["overdo", "extra", "partial", "excess", "overshoot"]),
    17: ("Moving to a New Dimension", ["3D", "dimension", "axis", "rotation", "multi-axis"]),
    18: ("Mechanical Vibration", ["vibration", "oscillation", "pulse", "resonance", "frequency"]),
    19: ("Periodic Action", ["interval", "cyclic", "repeat", "timing", "periodic"]),
    20: ("Continuity of Useful Action", ["continuous", "flow", "uninterrupted", "constant"]),
    21: ("Skipping", ["skip", "miss", "jump", "omit", "bypass"]),
    22: ("Blessing in Disguise", ["reuse waste", "harm into benefit", "drawback to advantage", "lemonade"]),
    23: ("Feedback", ["sensor", "monitor", "loop", "detect", "feedback", "control"]),
    24: ("Intermediary", ["interface", "mediator", "carrier", "middle step", "transfer"]),
    25: ("Self-service", ["automatic", "self-maintain", "autonomous", "self-clean", "self-regulate"]),
    26: ("Copying", ["imitate", "mimic", "simulate", "replicate", "copy"]),
    27: ("Cheap Short-Living Objects", ["disposable", "low-cost", "temporary", "replaceable", "inexpensive"]),
    28: ("Mechanics Substitution", ["electronic", "optical", "magnetic", "replace mechanical", "field-based"]),
    29: ("Pneumatics and Hydraulics", ["fluid", "pressure", "air", "liquid", "hydraulic", "pneumatic"]),
    30: ("Flexible Shells and Thin Films", ["membrane", "film", "elastic", "cover", "flexible shell"]),
    31: ("Porous Materials", ["foam", "mesh", "filter", "breathable", "porous"]),
    32: ("Color Changes", ["color shift", "indicator", "visual cue", "color change"]),
    33: ("Homogeneity", ["uniform", "same material", "blend", "homogeneous"]),
    34: ("Discarding and Recovering", ["eject", "reclaim", "recover", "waste removal", "discard"]),
    35: ("Parameter Changes", ["temperature", "shape", "size", "parameter", "property"]),
    36: ("Phase Transitions", ["melt", "freeze", "evaporate", "condense", "phase change"]),
    37: ("Thermal Expansion", ["expand heat", "shrink cold", "thermal expansion"]),
    38: ("Strong Oxidants", ["oxidize", "chemical reaction", "burn", "cleanse", "oxidation"]),
    39: ("Inert Atmosphere", ["nitrogen", "argon", "inert gas", "inert environment"]),
    40: ("Composite Materials", ["composite", "blend", "hybrid", "reinforced", "compound material"])
}

def format_principle(num, name):
    return f"Principle {num}.{name}"

def load_extracted_text(json_filename):
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    sections = {
        "Title": data.get("essential_data", {}).get("title", ""),
        "Abstract": data.get("essential_data", {}).get("abstract", ""),
        "Background": data.get("background_summary", ""),
        "Description": data.get("description", ""),
        "Claims": data.get("claims", "")
    }
    return sections

def extract_keywords(text):
    return [kw[0] for kw in kw_model.extract_keywords(text, top_n=10)]

def match_keywords_to_triz(keywords):
    matches = set()
    for num, (name, kw_list) in TRIZ_KEYWORDS.items():
        if any(any(k.lower() in word.lower() for k in kw_list) for word in keywords):
            matches.add((num, name))
    return sorted(matches)

def classify_triz_with_llm(sections):
    results = defaultdict(set)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for section, text in sections.items():
        chunks = splitter.split_text(text)
        for chunk in chunks:
            keywords = extract_keywords(chunk)
            matched_principles = match_keywords_to_triz(keywords)
            hints = ', '.join([format_principle(num, name) for num, name in matched_principles])

            prompt = f"""
You are a TRIZ analyst. Patent section hints:
{hints if hints else 'None'}

Section content:
{chunk}

List applicable TRIZ principles in this exact format:
- Principle [number].[name]
"""

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0
            )

            for line in response.choices[0].message.content.strip().splitlines():
                if line.startswith("- Principle"):
                    try:
                        principle_part = line.split("Principle")[1].strip()
                        num, _ = principle_part.split(".", 1)
                        num = int(num.strip())
                        standardized_name = TRIZ_KEYWORDS[num][0]
                        principle_formatted = format_principle(num, standardized_name)
                        results[principle_formatted].add(section)
                    except (ValueError, KeyError, IndexError):
                        continue
    return results

def format_triz_output(results):
    output_lines = []
    for principle in sorted(results, key=lambda x: int(x.split()[1].split(".")[0])):
        sections = ', '.join(sorted(results[principle]))
        output_lines.append(f"{principle} -> {sections}")
    return "\n".join(output_lines)

def summarize_patent(text):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Summarize this patent:\n\n{text}"}],
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

def build_retrieval_index(chunks):
    embeddings = load_cached_embeddings(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings

def hybrid_retrieve(query, chunks, index, embeddings):
    tokenized_chunks = [chunk.split(" ") for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    query_embedding = np.array(get_embedding(query)).astype("float32").reshape(1, -1)
    D, I = index.search(query_embedding, 5)
    scores = {i: bm25.get_scores(query.split())[i] - D[0][rank] for rank, i in enumerate(I[0])}
    return [chunks[i] for i in sorted(scores, key=scores.get, reverse=True)[:3]]

def rerank_chunks(query, chunks):
    scores = cross_encoder.predict([(query, chunk) for chunk in chunks])
    return [chunk for chunk, _ in sorted(zip(chunks, scores), key=lambda x: -x[1])[:2]]


def generate_structured_answer(summary, query, triz_output, context, history): 
    prompt = f"""
Summary:
{summary}

TRIZ Principles:
{triz_output}

Context:
{context}

Chat History:
{history}

User: {query}
Assistant:"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def main(json_filename):
    sections = load_extracted_text(json_filename)
    full_text = "\n\n".join(sections.values())
    summary = summarize_patent(full_text)

    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_text(full_text)
    index, embeddings = build_retrieval_index(chunks)

    triz_results = classify_triz_with_llm(sections)
    triz_output = format_triz_output(triz_results)

    print("📄 Patent Summary:\n", summary)
    print("\n🧠 TRIZ Principles Identified:\n", triz_output)

    while True:
        query = input("\nYour Question ('exit' to quit): ")
        if query.lower() == "exit": break
        context = "\n\n".join(rerank_chunks(query, hybrid_retrieve(query, chunks, index, embeddings)))
        history = memory.load_memory_variables({}).get("history", "")
        answer = generate_structured_answer(summary, query, triz_output, context, history) 
        print("\nAssistant:", answer)
        memory.save_context({"input": query}, {"output": answer})

# if __name__ == "__main__":
#     main("extracted_text.json")
