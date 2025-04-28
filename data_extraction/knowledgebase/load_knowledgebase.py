import os
import polars as pl
import uuid
from qdrant_client import QdrantClient
from qdrant_client import Distance, VectorParams, PointStruct, models
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from typing import List
from classification.LLM import LanguageModel

# --- Configuration ---
COLLECTION_NAME = "knowledgebase"
QADRANT_KEY = os.getenv("VECTORDB")
OPENAI_KEY = os.getenv("OPENAI_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

class VectorDBLoader:
    def __init__(self, collection_name: str, dataset: pl.DataFrame, model: LanguageModel, api_key: str, qdrant_url: str, batch_size: int = 20):
        self.qadrant_client = QdrantClient(
            url=qdrant_url,
            api_key=api_key
        )
        self.collection_name = collection_name
        self.batch_size = batch_size
        self.model=model
        
    def embed_function(self, text: str) -> List[float]:
        """Embed function for getting the embeddings of the input text."""
        embedding = self.model.embed(text)
        return embedding
    
    def chunk_text(self, text: str, chunk_size: int = 700, chunk_overlap: int = 20):
        """Split the text into smaller chunks using the RecursiveCharacterTextSplitter."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.create_documents([text])
    
    def batching(self, iterable, batch_size: int):
        """Generator function to yield batches of a given size."""
        batch = []
        for item in iterable:
            batch.append(item)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
    
    def upload_batches(self, df: pl.DataFrame, model: LanguageModel):
        """Process the provided DataFrame and upload data in batches to Qdrant."""
        # Iterate over the rows and process text
        for batch in self.batching(df.iter_rows(named=True), self.batch_size):
            ids = []
            vectors = []
            payloads = []

            # Prepare batch data
            for row in batch:
                full_text = row["reasoning_trace"]
                chunks = self.chunk_text(full_text)

                for chunk in chunks:
                    vector = self.embed_function(chunk.page_content)
                    vectors.append(vector)
                    payloads.append({
                        "instruction_seed": row["question"],
                        "discipline": "electrical engineering",
                        "text": chunk.page_content
                    })

            # Upload batch to Qdrant
            self.qadrant_client.upsert(
                collection_name=self.collection_name,
                points=PointStruct(
                    ids=ids,
                    vectors=vectors,
                    payload=payloads
                )
            )
            print(f"✅ Successfully uploaded batch of {len(batch)} points.")

        print("All batches uploaded successfully!")
    
    def create_collection(self):
        """Create a collection in Qdrant."""
        self.qadrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.model.get_embeddingSize(),
                distance=Distance.COSINE,
                on_disk=True
            ),
            quantization_config=models.ProductQuantization(
                product=models.ProductQuantizationConfig(
                    compression=models.CompressionRatio.X16,
                    always_ram=True
                ),
            ),
        )
        print(f"Collection '{self.collection_name}' created successfully!")