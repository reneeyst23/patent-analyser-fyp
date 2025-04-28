import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from datasets import load_dataset

# --- Configuration ---
COLLECTION_NAME = "knowledgebase"
TXT_PATH = "knowledgebase.txt"
EMBEDDING_MODEL = "text-embedding-ada-002"
QADRANT_KEY = os.getenv("VECTORDB")
OPENAI_KEY = os.getenv("OPENAI_KEY")

if not QADRANT_KEY or not OPENAI_KEY:
    raise EnvironmentError("❌ Missing API keys. Set VECTORDB and OPENAI_KEY in your environment.")

def prepare_text_chunks(txt_path):
    with open(txt_path, "r") as file:
        text = file.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=20)
    chunks = text_splitter.create_documents([text])
    if not chunks:
        raise ValueError("❌ No text chunks extracted from the TXT file.")
    return chunks

def embed_and_vectorize(texts, model_name=EMBEDDING_MODEL):
    if model_name.startswith("text-embedding"):
        client = OpenAI(api_key=OPENAI_KEY)
        vectors = [
            client.embeddings.create(input=text, model=model_name).data[0].embedding
            for text in texts
        ]
    if not vectors:
        raise ValueError("❌ No embeddings created. Check your model or API key.")
    return vectors

def store_vectors_to_qdrant(chunks, vectors):
    if len(chunks) != len(vectors):
        raise ValueError("❌ Mismatch between number of chunks and number of vectors.")

    client = QdrantClient(
        url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
        api_key=QADRANT_KEY,
    )

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

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
    
    

ds = load_dataset("mlfoundations-dev/a1_science_camel_chemistry")
print(ds)
print(ds["train"][0])