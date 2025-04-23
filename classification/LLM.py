from abc import ABC, abstractmethod
from openai import OpenAI
from friendli import Friendli
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
    def __init__(self):
        OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_KEY:
            raise ValueError("API key for OpenAI not found in environment variables.")
        self.client = OpenAI(api_key=OPENAI_KEY)  # Initialize OpenAI client with API key
        
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


class FriendliAI(LanguageModel):
    def __init__(self, API_KEY: str, modelChoice: str = "pulux9fal3aw"):
        self.client = Friendli()
        self.modelChoice = modelChoice

    def chat(self, messages: Union[List[dict], str]) -> str:
        if isinstance(messages, str):
            messages=[
            {"role": "system", "content": "You are a TRIZ expert."},
            {"role": "user", "content": messages}
        ]
        completion = self.client.chat.completions.create(
            model="meta-llama-3.3-70b-instruct",
            messages=messages,
            stream=False,
        )
        return (completion.choices[0].message.content)

    def embed(self, text: str) -> list[float]:
        return OpenAI("OPENAI_API_KEY").embed(text)

        
