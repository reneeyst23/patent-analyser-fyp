from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import json
import ast
import numpy as np

VECTORDB_KEY = os.getenv("VECTORDB")
COLLECTION = "patent_collection"

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
    api_key=VECTORDB_KEY
)

# Load a small embedding model locally
# 'all-MiniLM-L6-v2' is a good balance of size (~80MB) and quality
model = SentenceTransformer('all-MiniLM-L6-v2')

def chunking(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    background_description_chunks = []
    claims_abstract_chunks = []

    for item in data:
        serial_number = item.get("serial_number", "unknown")
        essential_raw = item.get("essential_data", "{}")
        background_summ = item.get("background_summary", "")
        description = item.get("description", "")
        claims = item.get("claims", "")

        # Skip if any critical section is None or empty
        if not essential_raw or not background_summ or not description or not claims:
            continue

        try:
            essential = ast.literal_eval(essential_raw)
        except (ValueError, SyntaxError):
            continue  # skip invalid essential_data entries

        title = essential.get("title", "")
        abstract = essential.get("abstract", "")
        date = essential.get("date", "")

        # First set: background + description
        first_text = background_summ + "\n" + description
        if first_text.strip():  # skip if empty after cleaning
            first_chunks = text_splitter.create_documents(
                [first_text],
                metadatas=[{
                    "serial_number": serial_number,
                    "publish_date": date,
                    "section": "background+description",
                    "abstract": abstract,
                    "title": title
                }]
            )
            background_description_chunks.extend(first_chunks)

        # Second set: claims + abstract
        second_text = claims + "\n" + abstract
        if second_text.strip():
            second_chunks = text_splitter.create_documents(
                [second_text],
                metadatas=[{
                    "serial_number": serial_number,
                    "publish_date": date,
                    "section": "claims+abstract",
                    "abstract": abstract,
                    "title": title
                }]
            )
            claims_abstract_chunks.extend(second_chunks)

    return background_description_chunks, claims_abstract_chunks

def embed_upsert(chunks: List, batch_size=32):
    # Skip if no chunks
    if not chunks:
        print("No chunks to embed and upsert")
        return
        
    # Process in batches to avoid memory issues
    total_chunks = len(chunks)
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1} ({len(batch)} chunks)")
        
        # Generate embeddings using local model
        texts = [chunk.page_content for chunk in batch]
        embeddings = model.encode(texts)
        
        # Ensure embeddings are converted to Python lists for JSON serialization
        embeddings = [embedding.tolist() for embedding in embeddings]
        
        # Prepare points for upsert
        points = []
        for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
            # Create a unique ID combining serial number and chunk index
            chunk_id = f"{chunk.metadata.get('serial_number', 'unknown')}_{i+j}"
            
            points.append(models.PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "content": chunk.page_content,
                    "title": chunk.metadata.get("title", ""),
                    "section": chunk.metadata.get("section", ""),
                    "publish_date": chunk.metadata.get("publish_date", ""),
                    "abstract": chunk.metadata.get("abstract", ""),
                    "serial_number": chunk.metadata.get("serial_number", "")
                }
            ))
        
        # Perform upsert
        qdrant_client.upsert(
            collection_name=COLLECTION,
            points=points
        )
        
        print(f"Successfully upserted batch with {len(points)} points")
    
    print(f"Completed upserting {total_chunks} total chunks to collection {COLLECTION}")

def initialize_collection(vector_size=384):
    """Initialize the collection if it doesn't exist"""
    collections = qdrant_client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if COLLECTION not in collection_names:
        print(f"Creating new collection: {COLLECTION}")
        qdrant_client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=vector_size,  # all-MiniLM-L6-v2 has 384 dimensions
                distance=models.Distance.COSINE
            )
        )
        print(f"Collection {COLLECTION} created successfully")
    else:
        print(f"Collection {COLLECTION} already exists")

# Example usage
def main():
    # Initialize vector database collection
    initialize_collection()
    
    # Process patent data
    json_path = "data_extraction/result.json"
    background_description_chunks, claims_abstract_chunks = chunking(json_path)
    
    print(f"Generated {len(background_description_chunks)} background/description chunks")
    print(f"Generated {len(claims_abstract_chunks)} claims/abstract chunks")
    
    # Process each chunk set separately
    embed_upsert(background_description_chunks)
    embed_upsert(claims_abstract_chunks)

if __name__ == "__main__":
    main()

    
    


