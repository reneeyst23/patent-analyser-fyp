from abc import ABC, abstractmethod
from openai import OpenAI
from together import Together
from typing import Union, List, Dict
from dotenv import load_dotenv
import os

load_dotenv()


class LanguageModel(ABC):
    @abstractmethod
    def chat(self, messages: Union[List[Dict[str, str]], str], temp: int) -> str:
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass
    
    @abstractmethod
    def get_embeddingSize(self) -> int:
        pass

class Openai(LanguageModel):
    def __init__(self, key: str):
        OPENAI_KEY = os.getenv(key)
        if not OPENAI_KEY:
            raise ValueError("API key for OpenAI not found in environment variables.")
        self.client = OpenAI(api_key=OPENAI_KEY)
        self.tools=[]

    def chat(self, messages: Union[List[Dict[str, str]], str], temp: int, model: str = "gpt-4o") -> str:
        if isinstance(messages, str):
            messages = [
                {"role": "system", "content": "You are a TRIZ expert."},
                {"role": "user", "content": messages}
            ]
        result = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp / 10.0
        )
        return result.choices[0].message.content.strip()

    def embed(self, text: str, model: str = "text-embedding-ada-002") -> list[float]:
        embedding = self.client.embeddings.create(
            input=text,
            model=model
        )
        return embedding.data[0].embedding
    
    def get_embeddingSize(self):
        return 1536
        

class TogetherAI(LanguageModel):
    def __init__(self, api_key: str):
        TOGETHER_KEY = os.getenv(api_key)
        if not TOGETHER_KEY:
            raise ValueError("API key for TogetherAI not found in environment variables.")
        self.client = Together(api_key=TOGETHER_KEY)

    def chat(self, messages: Union[List[Dict[str, str]], str], temp: int, model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B") -> str:
        if isinstance(messages, str):
            messages = [
                {"role": "system", "content": "You are a TRIZ expert."},
                {"role": "user", "content": messages}
            ]
        result = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp / 10.0
        )
        return result.choices[0].message.content.strip()

    def embed(self, text: str, model: str = "togethercomputer/m2-bert-80M-8k-retrieval") -> list[float]:
        """Embed using Together API directly (assuming the Together API supports embedding)."""
        embedding = self.client.embeddings.create(
            input=text,
            model=model
        )
        return embedding.data[0].embedding
        
        
        



        
