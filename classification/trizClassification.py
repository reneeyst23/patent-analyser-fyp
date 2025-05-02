from qdrant_client import QdrantClient
from pydantic import BaseModel, Field
from typing import List,Dict
from collections import defaultdict
import os
import json
import ast
import numpy as np
import cohere
from dotenv import load_dotenv
from LLM import LanguageModel
from prompt_template import Prompt

load_dotenv()
VECTORDB_KEY = os.getenv("VECTORDB_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# 📦 Models
class SearchResult(BaseModel):
    """
    Pydantic model for the base model from the RAG knowledgebase
    """
    text: str
    score: float
    topic: str

class TRIZPrinciple(BaseModel):
    principles: Dict[int, str] = Field(...)

class PatentClassifier:
    """
    Patent Classifier that will instantiate in main.py
    Input:
        init LLM model connection
        init QdrantDB connection
        init Cohere reranker connection
    """
    def __init__(self, model: LanguageModel):
        self.model = model
        self.qdrant_client = QdrantClient(url=QDRANT_URL, api_key=VECTORDB_KEY)
        self.cohere_client = cohere.Client(COHERE_KEY)

    def _get_weight_for_key(self, key: str) -> float:
        """
        function to get weight for each type of extracted problem
        primary = 10x
        secondary = 5x
        combined = 1x
        """
        return {"primary": 10.0, "secondary": 5.0}.get(key, 1.0)

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        seen = set()
        unique = []
        for r in results:
            if r.text not in seen:
                seen.add(r.text)
                unique.append(r)
        return unique

    def _min_max_normalize(self, arr: np.ndarray) -> np.ndarray:
        arr = np.array(arr, dtype=float)
        min_val, max_val = np.min(arr), np.max(arr)
        return (arr - min_val) / (max_val - min_val) if max_val > min_val else np.zeros_like(arr)

    def _search_vector_db(self, collection_name: str, topics: List[str], problem_dict: Dict[str, List[str]], point_limit: int) -> List[SearchResult]:
        results = []
        limit = point_limit // max(1, len(problem_dict))
        for key, texts in problem_dict.items():
            weight = self._get_weight_for_key(key)
            for text in texts:
                encoded = self.model.embed(text)
                hits = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=encoded,
                    with_payload=True,
                    limit=limit
                )
                for hit in hits:
                    topic=hit.payload["topic"]
                    if topic in topics or hit.payload["discipline"] in topics:
                        results.append(SearchResult(
                            text=hit.payload["text"],
                            score=hit.score * weight,
                            topic=topic
                        ))
                    else:
                        continue
        return results

    def _rerank_results(self, topics: List[str], results: List[SearchResult]) -> List[SearchResult]:
        query = " ".join(topics)
        documents = [r.text for r in results]
        rerank = self.cohere_client.rerank(model="rerank-english-v3.0", query=query, documents=documents)
        rerank_scores = [r.relevance_score for r in rerank.results]
        norm_scores = self._min_max_normalize([r.score for r in results])
        combined = 0.7 * np.array(rerank_scores) + 0.3 * norm_scores
        return [r for (r, _) in sorted(zip(results, combined), key=lambda x: x[1], reverse=True)]

    def retrieve_context(self, point_limit: int, collection_name: str, topics: List[str], problem_dict: Dict[str, List[str]]) -> str:
        results = self._search_vector_db(collection_name, topics, problem_dict, point_limit)
        if not results:
            return ""

        deduped = self._deduplicate_results(results)
        reranked = self._rerank_results(topics, deduped)

        grouped = defaultdict(list)
        for r in reranked:
            if len(grouped[r.topic]) < 8:
                grouped[r.topic].append(r.text)

        flat_results = [text for topic in grouped for text in grouped[topic]]
        return "\n".join(flat_results)

    def classify_patent(self, abstract: str, claims: str) -> TRIZPrinciple:
        extraction_prompt = Prompt.PROBLEM_EXTRACTION.value.format(claims=claims)
        topic_prompt = Prompt.topic_prompt.value.format(abstract=abstract)
        analysis_prompt = Prompt.PROBLEM_ANALYSIS.value
        rule_prompt = Prompt.RULE_CREATION.value
        final_prompt = Prompt.FINAL_CLASSIFICATION.value

        problems_raw = self.model.chat(extraction_prompt, 3)
        problems_dict = ast.literal_eval(problems_raw.strip("```python\n").strip("\n```"))

        topic_list = ast.literal_eval(self.model.chat(topic_prompt, 0).strip("```python\n").strip("\n```"))

        context = self.retrieve_context(50, "allenAI_chemData", topic_list, problems_dict)
        analysis = self.model.chat(analysis_prompt.format(problems=problems_dict, reasoning_trace=context), 5)
        dynamic_rule = self.model.chat(rule_prompt.format(analysis=analysis), 2)

        final_output = self.model.chat(final_prompt.format(dynamic_rule=dynamic_rule, claims=claims), 0)
        raw = final_output.strip().strip('```python').strip('```')
        return raw

    def format_result(self, result: TRIZPrinciple, serial_code: str) -> str:
        return json.dumps({
            "SerialCode": serial_code,
            "Results": result.dict()
        }, indent=2)