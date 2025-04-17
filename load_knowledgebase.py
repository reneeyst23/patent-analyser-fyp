import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# --- Configuration ---
COLLECTION_NAME = "knowledgebase"
TXT_PATH = "/content/knowledgebase.txt "
EMBEDDING_MODEL = "text-embedding-ada-002"
QADRANT_KEY=os.getenv("VECTORDB")
OPENAI_KEY=os.getenv("OPENAI_KEY")


# --- Load API keys securely ---

# --- Step 2: Embed using OpenAI or sentence-transformers ---
def embed_texts(texts, model_name=EMBEDDING_MODEL):
    if model_name.startswith("text-embedding"):
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        return [
            client.embeddings.create(input=text, model=model_name).data[0].embedding
            for text in texts
        ]
    else:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        return [vec.tolist() for vec in model.encode(texts)]

# --- Step 3: Connect to Qdrant ---
client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333", 
    api_key=QADRANT_KEY,
)

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

# --- Step 4: Process TXT file and embed ---
def extract_txt_chunks(txt_path, chunk_size=500):
    with open(txt_path, "r") as file:
        text = file.read()
    # Split the text into chunks (you can adjust the chunk size)
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

chunks = extract_txt_chunks(TXT_PATH)
if not chunks:
    raise ValueError("❌ No text chunks extracted from the TXT file.")

vectors = embed_texts(chunks)
if not vectors:
    raise ValueError("❌ No embeddings created. Check your OpenAI API key or model setup.")

if len(chunks) != len(vectors):
    raise ValueError("❌ Mismatch between number of chunks and number of vectors.")

# --- Step 5: Upload to Qdrant ---
points = [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=vec,
        payload={"text": chunk}
    )
    for vec, chunk in zip(vectors, chunks)
]

if not points:
    raise ValueError("❌ No points to upload.")

client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"✅ Loaded {len(points)} chunks into Qdrant collection '{COLLECTION_NAME}'")