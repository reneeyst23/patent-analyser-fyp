import os
import json
import numpy as np
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# --- Load environment variables ---
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Configurations ---
QDRANT_HOST = "localhost"
QDRANT_API_KEY = None
COLLECTION_NAME = "patent_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- Initialization ---
embedding_model = SentenceTransformer(MODEL_NAME)
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4-turbo")
memory = ConversationBufferMemory(memory_key="chat_history", input_key="query")
qdrant = QdrantClient(host=QDRANT_HOST, api_key=QDRANT_API_KEY)
reranker = pipeline(
    "text-classification",
    model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    tokenizer="cross-encoder/ms-marco-MiniLM-L-6-v2",
    padding=True,
    truncation=True,
    return_all_scores=True
)

# --- Helper Functions ---
def load_extracted_text(json_filename):
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return "\n\n".join([
        data.get("essential_data", {}).get("title", ""),
        data.get("essential_data", {}).get("abstract", ""),
        data.get("background_summary", ""),
        data.get("description", ""),
        data.get("claims", "")
    ])

def embed_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)
    vectors = embedding_model.encode(chunks, convert_to_numpy=True)
    return chunks, vectors

def create_qdrant_index(chunks, vectors):
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=vectors.shape[1],
            distance=models.Distance.COSINE,
            on_disk=True,
            quantization_config=models.ScalarQuantization(
                scalar=models.ScalarQuantizationConfig(type="int8")
            )
        )
    )
    qdrant.upload_collection(
        collection_name=COLLECTION_NAME,
        vectors=vectors,
        payload=[{"text": chunk} for chunk in chunks],
        ids=[i for i in range(len(chunks))],
        batch_size=64
    )

def retrieve_chunks(query, top_k=5):
    query_vec = embedding_model.encode(query).tolist()
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k,
        with_payload=True
    )
    return [res.payload["text"] for res in results]

def rerank_chunks(query, chunks):
    scores = reranker([(query, chunk) for chunk in chunks])
    ranked = sorted(zip(chunks, scores), key=lambda x: -x[1][0]['score'])
    return [chunk for chunk, _ in ranked[:2]]

def generate_answer(query, context):
    history = memory.load_memory_variables({}).get("chat_history", "")
    prompt = f"""
Context:
{context}

Chat History:
{history}

User: {query}
Assistant:"""
    response = llm.predict(prompt)
    return response.strip()

def generate_suggested_questions(summary: str) -> list:
    """Call OpenAI to generate suggested questions based on the patent summary."""
    prompt = f"""
You are a helpful assistant. Based on the following patent summary, suggest 5 intelligent and relevant questions that a user might want to ask about this patent.
Make sure the questions are open-ended, technical, and focused on clarifying key aspects.

Patent Summary:
{summary}

Output format: A Python list of strings.
"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )
        generated = response.choices[0].message.content.strip()
        suggested_questions = eval(generated)
        return suggested_questions
    except Exception as e:
        print(f"Error generating suggested questions: {e}")
        return []

def clean_up_index():
    if qdrant.collection_exists(collection_name=COLLECTION_NAME):
        qdrant.delete_collection(collection_name=COLLECTION_NAME)
        print(f"🗑️ Deleted collection '{COLLECTION_NAME}' from disk.")

def chatbot_main(json_path, summary):
    print("🔄 Loading patent text and indexing...")
    full_text = load_extracted_text(json_path)
    chunks, vectors = embed_chunks(full_text)
    create_qdrant_index(chunks, vectors)

    suggested_questions = generate_suggested_questions(summary)

    print("✅ System ready. Start chatting!")
    print("\nYou can ask your own question, or choose from the suggestions below:")
    for idx, question in enumerate(suggested_questions, start=1):
        print(f"{idx}. {question}")
    print("Type your question or enter the number corresponding to a suggested question.")

    while True:
        query = input("\nYour Question ('exit' to quit): ")
        if query.lower() == "exit": 
            clean_up_index()
            break

        if query.isdigit():
            idx = int(query)
            if 1 <= idx <= len(suggested_questions):
                query = suggested_questions[idx - 1]
                print(f"\nYou selected: {query}")

        retrieved = retrieve_chunks(query)
        reranked = rerank_chunks(query, retrieved)
        context = "\n\n".join(reranked)
        answer = generate_answer(query, context)
        print("\nAssistant:", answer)
        memory.save_context({"query": query}, {"output": answer})

if __name__ == "__main__":
    chatbot_main("extracted_text.json", summary="")
