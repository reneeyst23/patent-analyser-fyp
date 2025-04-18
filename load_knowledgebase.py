import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
COLLECTION_NAME = "knowledgebase"
TXT_PATH = "knowledgebase.txt"
EMBEDDING_MODEL = "text-embedding-ada-002"
QADRANT_KEY = os.getenv("VECTORDB")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# --- API Key Checks ---
if not QADRANT_KEY or not OPENAI_KEY:
    raise EnvironmentError("❌ Missing API keys. Set VECTORDB and OPENAI_KEY in your environment.")

# --- Step 1: Embed using OpenAI or Sentence-Transformers ---
def embed_texts(texts, model_name=EMBEDDING_MODEL):
    if model_name.startswith("text-embedding"):
        # For OpenAI SDK >= 1.0
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        return [
            client.embeddings.create(input=text, model=model_name).data[0].embedding
            for text in texts
        ]
    else:
        # For local models using sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        return [vec.tolist() for vec in model.encode(texts)]

# --- Step 2: Connect to Qdrant ---
client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
    api_key=QADRANT_KEY,
)

# --- Step 3: Create Collection if Not Exists ---
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

# --- Step 4: Load Text File and Split into Chunks ---
def extract_txt_chunks(txt_path):
    with open(txt_path, "r") as file:
        text = file.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=20)
    return text_splitter.create_documents([text])

chunks = extract_txt_chunks(TXT_PATH)

if not chunks:
    raise ValueError("❌ No text chunks extracted from the TXT file.")

texts = [doc.page_content for doc in chunks]

# --- Step 5: Embed Chunks ---
vectors = embed_texts(texts)

if not vectors:
    raise ValueError("❌ No embeddings created. Check your OpenAI API key or model setup.")

if len(chunks) != len(vectors):
    raise ValueError("❌ Mismatch between number of chunks and number of vectors.")

# --- Step 6: Upload Embeddings to Qdrant ---
points = [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=vec,
        payload={"text": chunk.page_content}
    )
    for vec, chunk in zip(vectors, chunks)
]

if not points:
    raise ValueError("❌ No points to upload.")

client.upsert(collection_name=COLLECTION_NAME, points=points)

print(f"✅ Loaded {len(points)} chunks into Qdrant collection '{COLLECTION_NAME}'")
