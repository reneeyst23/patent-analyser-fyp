from openai import OpenAI
from qdrant_client import QdrantClient
from pydantic import BaseModel, Field
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import pandas as pd

VECTORDB_KEY = os.getenv("VECTORDB")
OPENAI_KEY = os.getenv("OPENAI_KEY")

qdrant_client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
    api_key=VECTORDB_KEY
)

result=pd.load_csv("data_extraction/result.json")


