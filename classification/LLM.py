from abc import ABC, abstractmethod
from openai import OpenAI
from together import Together
from typing import Union, List, Dict
import os

class LanguageModel(ABC):
    @abstractmethod
    def chat(self, messages: Union[List[Dict[str, str]], str]) -> str:
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

class Openai(LanguageModel):
    def __init__(self, key:str):
        OPENAI_KEY = os.getenv(key)
        if not OPENAI_KEY:
            raise ValueError("API key for OpenAI not found in environment variables.")
        self.client = OpenAI(api_key=OPENAI_KEY)
        
    def chat(self, messages: Union[List[dict], str], model: str = "gpt-4o") -> str:
        if isinstance(messages, str):
            messages = [
                {"role": "system", "content": "You are a TRIZ expert."},
                {"role": "user", "content": messages}
            ]
        result = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return result.choices[0].message.content.strip()

    def embed(self, text: str, model:str="text-embedding-ada-002") -> list[float]:
        embedding = self.client.embeddings.create(
            input=text,
            model=model
        )
        return embedding.data[0].embedding
    
class togetherAI(LanguageModel):
    def __init__(self, api_key:str):
        self.api_key=api_key
        self.client=Together(api_key=self.api_key)
        
    def chat(self, messages: Union[List[dict], str], model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B") -> str:
        if isinstance(messages, str):
            messages = [
                {"role": "system", "content": "You are a TRIZ expert."},
                {"role": "user", "content": messages}
            ]
        response = self.client.chat.completions.create(model=model, 
                    messages=messages)
        return(response.choices[0].message.content)
    
    def embed(self, text: str, model:str="text-embedding-ada-002") -> list[float]:
        embedder=Openai("OPENAI_KEY")
        return embedder.embed(text, model)
        



        
