from openai import OpenAI
from qdrant_client import QdrantClient
from pydantic import BaseModel, Field
from typing import List
from prompt_template import Prompt
import os
import json

# ✅ Output Schema
class TRIZPrinciple(BaseModel):
    uuid: str = Field(description="Serial number of patent")
    principles: List[str] = Field(..., description="A list of TRIZ principles")

# 🔐 Load API keys
VECTORDB_KEY = os.getenv("VECTORDB")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# ✅ Initialize Clients
openai_client = OpenAI(api_key=OPENAI_KEY)
qdrant_client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
    api_key=VECTORDB_KEY
)

# 🚀 Patent Classification Pipeline with CoT before vector search
def classify_patent(abstract: str, claims: str) -> tuple[TRIZPrinciple, str, str]:
    # 🔍 CoT Step: Extract main problem first
    extraction_prompt = Prompt.PROBLEM_EXTRACTION.value.format(claims=claims)
    extraction_result = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a TRIZ expert."},
            {"role": "user", "content": extraction_prompt}
        ]
    )
    extracted_problems = extraction_result.choices[0].message.content.strip()

    # 🔍 CoT Step: Analyze the extracted problems into dimensions
    analysis_prompt = Prompt.PROBLEM_ANALYSIS.value.format(problems=extracted_problems)
    analysis_result = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a TRIZ expert."},
            {"role": "user", "content": analysis_prompt}
        ]
    )
    analysis_dimensions = analysis_result.choices[0].message.content.strip()

    # 🧠 Step 1: Embed the analysis to guide vector search
    embedding = openai_client.embeddings.create(
        input=analysis_dimensions,
        model="text-embedding-ada-002"
    ).data[0].embedding

    # 📚 Step 2: Search vector DB using semantic dimensions
    hits = qdrant_client.search(
        collection_name="knowledgebase",
        query_vector=embedding,
        limit=5
    )
    extra_contexts = "\n\n".join(hit.payload.get("text", "") for hit in hits)

    # 📘 Step 3: Create TRIZ rule
    rule_prompt = Prompt.RULE_CREATION.value.format(extra_contexts=extra_contexts)
    rule_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in TRIZ principles."},
            {"role": "user", "content": rule_prompt}
        ]
    )
    dynamic_rule = rule_response.choices[0].message.content.strip()

    # 🧪 Step 4: Classify with rule
    classification_prompt = Prompt.FINAL_CLASSIFICATION.value.format(
        dynamic_rule=dynamic_rule,
        abstract=abstract,
        claims=claims
    )
    classification_result = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a TRIZ expert."},
            {"role": "user", "content": classification_prompt}
        ]
    )
    result = classification_result

    return result, dynamic_rule


# 🧪 Example usage
if __name__ == "__main__":
    abstract = """A package of one or more absorbent articles is disclosed. The package includes a package material, wherein the package material 
has natural fibers and exhibits an MD tensile strength of at least 5.0 kN/m and an MD Stretch of at least 3 percent, each as determined 
via ISO 1924-3 as modified herein. The package further includes a plurality of panels, including a consumer-facing panel. The package is sealed."""
    
    claims = """"Claims 1 . A package of one or more absorbent articles, the package comprising a package material, wherein the package material comprises 
    natural fibers and exhibits an MD tensile strength of at least 5.0 kN/m and an MD Stretch of at least 3 percent, each as determined via ISO 1924-3 as 
    modified herein, wherein the package comprises a plurality of panels, including a consumer-facing panel, and wherein the package is sealed. 
    2 . The package of claim 1, wherein the package material exhibits an MD tensile strength of at least 5 kN/m. 
    3 . The package of claim 1, wherein the package material exhibits an MD tensile strength of between 5 kN/m and 8.5 kN/m. 
    4 . The package of claim 1, wherein the package material exhibits a CD tensile strength of between 3 kN/m and 6.5 kN/m. 
    5 . The package of claim 1, wherein the package material exhibits an MD stretch at break of between 3 and 6.5 percent. 
    6 . The package of claim 1, wherein the package material exhibits an MD stretch at break of at least 3 percent. 
    7 . The package of claim 1, wherein the package material exhibits a CD stretch at break of between 4 and 10 percent. 
    8 . The package of claim 1, wherein the package material has a caliper of between 50 to 110 cm. 
    9 . The package of claim 1, wherein the package material has a basis weight of between 60 and 120 gsm, as measured by the grammage test of ISO 536 as modified herein. 
    10 . The package of claim 1, wherein the package material comprises between 50 and 100 percent by weight of natural fibers. 
    11 . The package of claim 1, wherein the package material is recyclable and the package material exhibits a recyclable percentage of at least at least 80 percent, as determined by the Repulpability Test method. 
    12 . The package of claim 11, wherein the package material is recyclable and the package material exhibits a recyclable percentage of between from about 80 percent to about 99.9 percent. 
    13 . The package of claim 1, wherein the one or more absorbent articles comprise at least one of feminine hygiene pads, diapers, incontinence pads, diaper pants, adult incontinence briefs. 
    14 . The package of claim 1, wherein the one or more absorbent articles comprises diapers and the plurality of panels further comprise a bottom panel and wherein the bottom panel comprises a pinch bottom configuration or a Totani style configuration. 
    15 . The package of claim 1, wherein the one or more absorbent articles comprises feminine hygiene articles and the plurality of panels further comprise a bottom panel, and wherein the bottom panel comprises a block bottom configuration or cross-bottom configuration. 
    16 . The package of claim 1, wherein the package material is recyclable, and the package material exhibits an overall pass test outcome, as determined via the Repulpability Test method. 
    17 . The package of claim 1, wherein the one or more absorbent articles exhibit an in-bag stack height of from between 70 mm to about 150 mm. 18 . The package of claim 1, wherein the package material comprises a single ply of material such that the one or more absorbent articles therein contact an inner surface of the package material.
    19 . The package of claim 1, wherein the package material does not comprise a barrier layer. 20 . The package of claim 1, wherein the package material comprises a barrier layer."
    """
    result, dynamic_rule = classify_patent(abstract, claims)
    print(f"Classification Result: {result}")
    print(f"Dynamic Rule: {dynamic_rule}")



    
