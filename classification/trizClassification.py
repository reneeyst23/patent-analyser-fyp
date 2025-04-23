from qdrant_client import QdrantClient
from pydantic import BaseModel, Field
from typing import List, Union
from contextlib import ExitStack
from prompt_template import Prompt
import os
import json
from LLM import LanguageModel
from ast import literal_eval
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Output Schema
class TRIZPrinciple(BaseModel):
    principles: List[Union[int, str]] = Field(..., description="A list of TRIZ principles, allowing both integers and strings")

def retrieveContext(embeddings:list[float], pointLimit:int, collection_name:str)->str:
    VECTORDB_KEY = os.getenv("VECTORDB_KEY")
    qdrant_client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
    api_key=VECTORDB_KEY
)
    hits = qdrant_client.search(
        collection_name=collection_name,
        query_vector=embeddings,
        limit=pointLimit
    )
    extra_contexts = "\n\n".join(hit.payload.get("text", "") for hit in hits)
    return extra_contexts
    
# 🚀 Patent Classification Pipeline with CoT before vector search
def classify_patent(model:LanguageModel, abstract: str, claims: str) -> TRIZPrinciple:
    # 🔍 CoT Step: Extract main problem first
    extraction_prompt = Prompt.PROBLEM_EXTRACTION.value.format(claims=claims)
    extracted_problems=model.chat(extraction_prompt)
    print(extracted_problems)
    # 🔍 CoT Step: Analyze the extracted problems into dimensions
    analysis_prompt = Prompt.PROBLEM_ANALYSIS.value.format(problems=extracted_problems)
    analysis_dimensions = model.chat(analysis_prompt)
    print(analysis_dimensions)

    # 🧠 Step 1: Embed the analysis to guide vector search
    embedding=model.embed(analysis_dimensions)
    print(embedding)
    
    # 📚 Step 2: Search vector DB using semantic dimensions
    extra_contexts=retrieveContext(embedding, 5, "knowledgebase")

    # 📘 Step 3: Create TRIZ rule
    rule_prompt = Prompt.RULE_CREATION.value.format(extra_contexts=extra_contexts)
    dynamic_rule=model.chat(rule_prompt)

    # 🧪 Step 4: Classify with rule
    classification_prompt = Prompt.FINAL_CLASSIFICATION.value.format(
        dynamic_rule=dynamic_rule,
        abstract=abstract,
        claims=claims
    )
    json_string = model.chat(classification_prompt)
    json_data = json_string.strip("```json\n").strip("\n```")
    parsed_output = TRIZPrinciple.model_validate_json(json_data)
    return parsed_output

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
    
    



    
