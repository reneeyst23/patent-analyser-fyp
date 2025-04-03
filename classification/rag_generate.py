from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.dataclasses import Document
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter
from haystack import Pipeline
from haystack.components.embedders import HuggingFaceAPIDocumentEmbedder
from pathlib import Path
from haystack.utils import Secret
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from together import Together
from haystack.components.embedders import HuggingFaceAPITextEmbedder



# Initialize document store (Qdrant) with embedding_dim=384
document_store = QdrantDocumentStore(
    ":memory:",
    index="Document",
    embedding_dim=384,  # bge-small-en-v1.5 uses 384 dimensions
    recreate_index=True,
)

# Initialize components
converter = PyPDFToDocument()
cleaner = DocumentCleaner()
splitter = DocumentSplitter(split_by="sentence", split_length=5)
embedder = HuggingFaceAPIDocumentEmbedder(
    api_type="serverless_inference_api",
    api_params={"model": "BAAI/bge-small-en-v1.5"},
    token=Secret.from_token("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")
)
writer = DocumentWriter(document_store=document_store)

# Create a single pipeline that handles everything
pipeline = Pipeline()
pipeline.add_component("converter", converter)
pipeline.add_component("cleaner", cleaner)
pipeline.add_component("splitter", splitter)
pipeline.add_component("embedder", embedder)
pipeline.add_component("writer", writer)

# Connect the pipeline properly
pipeline.connect("converter", "cleaner")
pipeline.connect("cleaner", "splitter")
pipeline.connect("splitter", "embedder")
pipeline.connect("embedder", "writer")

# Run the pipeline to index documents
pipeline.run({
    "converter": {"sources": [Path("World Hist orld History Since 1500, John Rankin, Constanze Weise.pdf")]}
})

# Initialize the retriever with the same embedding_dim=384
retriever = QdrantEmbeddingRetriever(document_store=document_store)

query="People notable in Shia Faction"

# Retrieve documents using the query embedding
query_embedder = HuggingFaceAPITextEmbedder(
    api_type="serverless_inference_api",
    api_params={"model": "BAAI/bge-small-en-v1.5"},
    token=Secret.from_token("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")
)

# Generate a query embedding (example with a 384-dimensional vector)
query_text = "Who win ww2?"
query_embedding = query_embedder.run(query_text)
results = retriever.run(query_embedding=query_embedding["embedding"])

# RAG template for Together API prompt
template = """
Given the following information, answer the question.

Context: 
{context}

Question: {{ "Who win ww2  ?" }}?
"""

# Extract the content from the documents
context = "\n".join([doc.content for doc in results["documents"]])
prompt_message = template.format(context=context, query=query)
client = Together(api_key="04754ecf704467fd40c34bb371850b0b5100c9bac653b0c277f2281ef2ee0737")
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3",
    messages=[{"role": "user", "content": prompt_message}],
)

print(response.choices[0].message.content)

