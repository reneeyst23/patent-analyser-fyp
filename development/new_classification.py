from openai import OpenAI
from qdrant_client import QdrantClient
from pydantic import BaseModel, Field
from typing import List
import uuid
import os
import json

# 🧠 Output schema
class TRIZPrinciple(BaseModel):
    uuid: str = Field(description="Serial number of patent")
    principles: List[str] = Field(..., description="A list of TRIZ principles")

# 🔐 Load keys
VECTORDB_KEY = os.getenv("VECTORDB")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# ✅ Setup clients
openai_client = OpenAI(api_key=OPENAI_KEY)
qdrant_client = QdrantClient(
    url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333",
    api_key=VECTORDB_KEY
)

# 🚀 Core pipeline
def classify_patent(abstract: str, claims: str) -> tuple[TRIZPrinciple, str]:
    # Step 1: Embed the abstract
    embedding = openai_client.embeddings.create(
        input=abstract,
        model="text-embedding-ada-002"
    ).data[0].embedding

    # Step 2: Search for relevant TRIZ context
    hits = qdrant_client.search(
        collection_name="knowledgebase",
        query_vector=embedding,
        limit=5
    )
    extra_contexts = "\n\n".join(hit.payload.get("text", "") for hit in hits)

    # Step 3: Create a rule based on the extra contexts
    rule_prompt = f"""
    You are an expert in patent classification and TRIZ principles. 
    CAPPED AROUND 200 WORDS
    Based on the following contexts, create a dynamic rule on 40 principles, focus on practical description, focus to have a lot of principles if possible:

    Relevant TRIZ background knowledge:
    {extra_contexts}
    """

    # API Call to OpenAI to generate the dynamic rule
    rule_creation = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in patent classification and TRIZ principles."},
            {"role": "user", "content": rule_prompt}
        ]
    )
    
    dynamic_rule = rule_creation.choices[0].message.content
    
    # Step 4: Create a full prompt for classification using the dynamic rule
    full_prompt = f"""
    You are a TRIZ expert. Based on the abstract and claims below, classify the invention using TRIZ 40 principles.

    Dynamic Rule:
    {dynamic_rule}

    Patent Abstract:
    {abstract}

    Patent Claims:
    {claims}

    Output a JSON object with the following fields:
    - uuid: a unique identifier for this patent
    - principles: a list of TRIZ principles detected in the claims
    """

    # Step 5: Use GPT-4 to classify based on the rule
    completion = openai_client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in patent classification and TRIZ principles."},
            {"role": "user", "content": full_prompt}
        ],
        response_format=TRIZPrinciple
    )

    # Step 6: Parse and return result as Pydantic model
    return (completion, dynamic_rule)

# 🧪 Example usage
if __name__ == "__main__":
    abstract = """A package of one or more absorbent articles is disclosed. The package includes a package material, wherein the package material 
has natural fibers and exhibits an MD tensile strength of at least 5.0 kN/m and an MD Stretch of at least 3 percent, each as determined 
via ISO 1924-3 as modified herein. The package further includes a plurality of panels, including a consumer-facing panel. The package is sealed."""
    
    claims = """"Claims 1 . A package of one or more absorbent articles, the package comprising a package material, wherein the package material comprises natural fibers and exhibits an MD tensile strength of at least 5.0 kN/m and an MD Stretch of at least 3 percent, each as determined via ISO 1924-3 as modified herein, wherein the package comprises a plurality of panels, including a consumer-facing panel, and wherein the package is sealed."""
    
    result, dynamic_rule = classify_patent(abstract, claims)
    print(f"Classification Result: {result.model_dump_json(indent=2)}")
    print(f"Dynamic Rule: {dynamic_rule}")
    
#principles\":[\"35. Parameter Changes\",\"3. Local Quality\",\"40. Composite Materials\"]}"
"""
1. **Flexible Membranes (Principle 30)**: 
    Utilize flexible or inflatable membranes as the primary filtration medium instead of rigid filters. 
    These membranes can expand or collapse, facilitating easier cleaning and less material usage. 
    This approach offers a lightweight and adaptable filter structure that can conform to various shapes and sizes, 
    increasing design flexibility and efficiency.

2. **Porous Materials (Principle 31)**: Integrate porous materials like ceramic or activated carbon into the flexible membrane structure. 
These materials allow for effective filtration by trapping contaminants while permitting water flow. The porosity can be fine-tuned to target 
specific particle sizes, enhancing the filter's eco-efficiency by minimizing pollutants without requiring chemical additives.

**Combination Application**: A water filter could incorporate a collapsible, flexible membrane lined with a porous material. 
In scenarios of high filtration demand, the membrane expands to increase surface area, enhancing filtration capacity. 
This design not only reduces material use but also supports environmental sustainability by lowering toxicity levels in treated water.
"""

#[\"35: Parameter changes\",\"10: Preliminary action\",\"6: Universality\"]}"
"""
1. **Flexible Membrane (30):** Use flexible membranes as water filters to replace rigid filter structures. These membranes can be constructed as thin films, conserving material while isolating contaminants from water through filtration.

2. **Porous Materials (31):** Incorporate porous materials to aid in water purification. Materials like ceramic and carbon can serve to filter water efficiently, utilizing their inherent porosity to trap impurities.

3. **Local Quality (3):** Optimize filter design by introducing varying textures or materials in specific areas of the filter. This non-uniform design can enhance efficiency by targeting specific contaminants more effectively within the system.  

4. **Mechanical Vibration (18):** Use controlled mechanical oscillations or ultrasonic vibrations to improve the separation of impurities, promoting better penetration and interaction of water with the filter materials.

5. **Asymmetry (4):** Design filter components with asymmetric features to optimize flow dynamics, minimizing energy use while maximizing filtration efficiency.
"""



    
