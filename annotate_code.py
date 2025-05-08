
from openai import OpenAI
import os, json, re, sys, time
import numpy as np

# ── Configuration ───────────────────────────────────────────────────────────
client = OpenAI(api_key='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')

EMBED_MODEL    = "text-embedding-ada-002"  # high-quality semantic embeddings
DECODER_MODEL  = "gpt-3.5-turbo"           # for zero-shot classification

CAND_TOP_N     = 10    # shortlist this many top-similarity principles
MAX_TOKENS     = 256
TEMPERATURE    = 0.0   # deterministic outputs

# ── Load data ───────────────────────────────────────────────────────────────
def load_data(principles_path="triz_principles.json", claims_path="result.json"):
    with open(principles_path, encoding="utf-8") as f:
        principles = json.load(f)
    with open(claims_path, encoding="utf-8") as f:
        patents = json.load(f)
    print(f"Loaded {len(principles)} principles; {len(patents)} patents.", file=sys.stderr)
    return principles, patents

# ── Embeddings ──────────────────────────────────────────────────────────────
def embed_texts(texts, model=EMBED_MODEL, retries=3, delay=1):
    for _ in range(retries):
        try:
            resp = client.embeddings.create(model=model, input=texts)
            return np.array([d.embedding for d in resp.data], dtype=np.float32)
        except Exception as e:
            print(f"Embedding error: {e}", file=sys.stderr)
            time.sleep(delay)
    raise RuntimeError("Embedding failed after retries")

def cosine_sim(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(np.dot(a, b) / (na * nb))

# ── Zero-shot classifier ────────────────────────────────────────────────────
def classify_zero_shot(claim, candidates):
    """
    Zero-shot LLM call: lists claim and candidate principles,
    asks for numbers of all that apply.
    """
    system = {
        "role": "system",
        "content": (
            "You are an expert at TRIZ. Given a patent claim and a numbered list "
            "of TRIZ principles, respond with the numbers of all principles that apply, "
            "separated by commas (e.g. '1, 5, 10'). If none apply, respond 'None'. "
            "Output ONLY the numbers or 'None'."
        )
    }
    user_content = f"Claim:\n\"\"\"{claim.strip()}\"\"\"\n\nPrinciples:\n"
    for p in candidates:
        desc = p.get("description", "").split(".")[0]  # first sentence
        user_content += f"{p['number']}: {p['name']} – {desc}.\n"
    user_content += "\nAnswer:"
    resp = client.chat.completions.create(
        model=DECODER_MODEL,
        messages=[system, {"role":"user","content":user_content}],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    out = resp.choices[0].message.content.strip()
    print(f"LLM says: {out}", file=sys.stderr)
    if out.lower().startswith("none"):
        return []
    return sorted({int(n) for n in re.findall(r"\d+", out)})

# ── Hybrid labeler ───────────────────────────────────────────────────────────
def label_claim(claim, principles, princ_embs):
    """
    1) Embed claim, compute sims.
    2) Shortlist top N principles by sim.
    3) If one candidate, return it.
    4) Else zero-shot LLM classify among shortlisted.
    """
    claim_emb = embed_texts([claim])[0]
    sims = [cosine_sim(claim_emb, pe) for pe in princ_embs]
    # shortlist top-N
    top_idxs = np.argsort(sims)[-min(CAND_TOP_N, len(sims)):]
    candidates = [principles[i] for i in top_idxs]
    # single candidate shortcut
    if len(candidates) == 1:
        return [int(candidates[0]["number"])]
    # multi-candidate zero-shot classification
    return classify_zero_shot(claim, candidates)

# ── Aggregation ─────────────────────────────────────────────────────────────
def aggregate_to_patent(entries):
    patent_map = {}
    for e in entries:
        patent_map.setdefault(e["patent_title"], set()).update(e["principles"])
    return [{"title": t, "principles": sorted(v)} for t, v in patent_map.items()]

# ── Main ────────────────────────────────────────────────────────────────────
def annotate(principles_path="triz_principles.json",
             claims_path="result.json",
             claim_output="claim_level_triz.json",
             patent_output="patent_level_triz.json"):
    principles, patents = load_data(principles_path, claims_path)
    valid = [p for p in principles if p.get("number") and p.get("name")]
    texts = [f"{p['name']}. {p.get('description','')}" for p in valid]
    princ_embs = embed_texts(texts)

    all_entries = []
    split_re = re.compile(r'(?<!\d)\d+\.\s*')

    for pat in patents:
        title = pat.get("essential_data", {}).get("title", "Untitled")
        raw   = pat.get("claims", "")
        parts = split_re.split(raw)
        if parts and not parts[0].strip(): parts = parts[1:]
        claims = [c.strip() for c in parts if c.strip()]
        for idx, claim in enumerate(claims, 1):
            nums = label_claim(claim, valid, princ_embs)
            all_entries.append({
                "patent_title": title,
                "claim_index": idx,
                "claim_text": claim,
                "principles": nums
            })
            time.sleep(0.5)

    # write claim-level
    with open(claim_output, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, indent=2)
    # write patent-level
    patent_level = aggregate_to_patent(all_entries)
    with open(patent_output, 'w', encoding='utf-8') as f:
        json.dump(patent_level, f, indent=2)

    print(f"Wrote {len(all_entries)} claims → {claim_output}", file=sys.stderr)
    print(f"Wrote {len(patent_level)} patents → {patent_output}", file=sys.stderr)

if __name__ == "__main__":
    annotate()