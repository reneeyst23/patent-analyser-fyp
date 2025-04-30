from qdrant_client import QdrantClient, models
from pydantic import BaseModel, Field
from typing import List, Union, Dict
from contextlib import ExitStack
from prompt_template import Prompt
import os
import json
from LLM import LanguageModel
from ast import literal_eval
import ast
import numpy as np
import cohere
from collections import defaultdict

def min_max_normalize(arr):
    arr = np.array(arr, dtype=float)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val - min_val == 0:
        return np.zeros_like(arr)  # avoid division by zero
    return (arr - min_val) / (max_val - min_val)

# ✅ Output Schema
class TRIZPrinciple(BaseModel):
    principles: List[Union[int, str]] = Field(..., description="A list of TRIZ principles, allowing both integers and strings")

def retrieveContext(llm, pointLimit: int, collection_name: str, topics: list[str], problem_dict: Dict[str, List[str]]) -> str:
    co = cohere.Client("SrbWtPOb3iFAqpVe5HD2U6saj7a719TpPGRTfk35")
    VECTORDB_KEY = os.getenv("VECTORDB_KEY")

    # Initialize the Qdrant client
    qdrant_client = QdrantClient(
        url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
        api_key=VECTORDB_KEY
    )

    lst = []
    for key, value in problem_dict.items():
        for s in value:
            encoded = llm.embed(s)
            hits = qdrant_client.search(
                collection_name=collection_name,
                query_vector=encoded,
                with_payload=True,
                limit=25
            )
            for hit in hits:
                if hit.payload["topic"] in topics:
                    if key == "primary":
                        adj_score = hit.score * 10
                    elif key == "secondary":
                        adj_score = hit.score * 5
                    else:
                        adj_score = hit.score * 1
                    lst.append((hit.payload["text"], adj_score, hit.payload["topic"]))
                else:
                    continue

    if not lst:
        return ""

    # Deduplicate by text content
    seen = set()
    unique_lst = []
    for text, score, topic in lst:
        if text not in seen:
            seen.add(text)
            unique_lst.append((text, score, topic))

    # Normalize adj_scores
    normalized_adj = min_max_normalize([s[1] for s in unique_lst])

    # Rerank using Cohere
    query = " ".join(topics)
    rerank_results = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[text for text, _, _ in unique_lst]
    )
    rerank_scores = [res.relevance_score for res in rerank_results.results]
    combined_scores = 0.7 * np.array(rerank_scores) + 0.3 * normalized_adj

    reranked = sorted(
        zip(unique_lst, combined_scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    topic_groups = defaultdict(list)

    for (text, _, topic), score in reranked:
        if len(topic_groups[topic]) < 8:
            topic_groups[topic].append(text)

    # Flatten the grouped results in order of topic
    final_texts = []
    for topic in topic_groups:
        final_texts.extend(topic_groups[topic])
    
    return "\n".join(final_texts) 
    
# 🚀 Patent Classification Pipeline with CoT before vector search
def classify_patent(model: LanguageModel, abstract: str, claims: str) -> dict:

    # Step 1: Extract problems and topics
    extraction_prompt = Prompt.PROBLEM_EXTRACTION.value.format(claims=claims)
    extracted_problems = model.chat(extraction_prompt, 3)
    
    topic_prompt = Prompt.topic_prompt.value.format(abstract=abstract)
    list_string = model.chat(topic_prompt, 0)

    # Clean the list_string and convert it to an actual list
    cleaned_string = list_string.strip("```python\n").strip("\n```")
    topics_list = ast.literal_eval(cleaned_string)
    
    problems_string = extracted_problems.strip("```python\n").strip("\n```")
    problems_dict = ast.literal_eval(problems_string)
    
    extra_context=retrieveContext(model, 50, "allenAI_chemData", topics_list, problems_dict)
    
    analysis_prompt = Prompt.PROBLEM_ANALYSIS.value.format(problems=problems_dict, reasoning_trace=extra_context)
    analysis = model.chat(analysis_prompt, 5)
    
    rule_prompt = Prompt.RULE_CREATION.value.format(analysis=analysis)
    dynamic_rule=model.chat(rule_prompt, 2)
    
    classification_prompt = Prompt.FINAL_CLASSIFICATION.value.format(
        dynamic_rule=dynamic_rule,
        claims=claims
    )
    return  model.chat(classification_prompt, 0)


    

def format_answer(result: TRIZPrinciple, serial_code: str) -> str:
    """Formats the output with serial code and TRIZ results."""
    output = {
        "SerialCode": serial_code,
        "Results": result.dict()
    }
    return json.dumps(output, indent=2)

def load_resultData(model:LanguageModel, file_location: str, output_file: str):

    with open(file_location, 'r') as file:
        data = json.load(file)

    with ExitStack() as stack:
        output = stack.enter_context(open(output_file, 'w'))
        output.write('[\n')

        for idx, entry in enumerate(data):
            serial_code = entry.get("SerialCode", "")
            parsed_data = literal_eval(entry["essential_data"])
            abstract = parsed_data.get("abstract", "")
            claims = entry["claims"]
            if claims == "":
                continue
            result = classify_patent(model, abstract, claims)
            formatted_entry = format_answer(result, serial_code)

            # Proper comma separation
            if idx > 0:
                output.write(',\n')

            output.write(formatted_entry)

        output.write('\n]')
        print(f"Streamed results have been saved to {output_file}")
    


# 🧪 Example usage
if __name__ == "__main__":
    load_resultData("data_extraction/result.json", "labelled_data.json")
    
    



    
