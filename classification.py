import json
import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import RecommendRequest, PointVector
from openai import OpenAI

class Classifier:
    def __init__(self, file:json):
        """
        DEVELOPER NOTE
        docExpandExtractor(), searchExtraContext(), promptEnhancerAgent() are
        auxuliary done after 1st iteration
        """
        self.client = OpenAI()
        vectordb_key=os.getenv("VECTORDB")
        openai_key=os.getenv("OPENAI_API_KEY")
        self.file=file
        self.qdrant_client = QdrantClient(
            url="https://d59b4db7-bd08-4913-81bd-f37f96afc695.us-east-1-0.aws.cloud.qdrant.io:6333", 
            api_key=vectordb_key,
        )
        self.openai_client=OpenAI(api_key=openai_key)
    def docExpandExtractor(self, abstract: str) -> dict:
        # First, identify the main topic of the abstract, and then request 100 descriptions for that topic
        prompt = f"""
        Please analyze the following abstract and identify a singular topic from it. Then, expand on this topic by providing 50 descriptive sentences related to the chosen topic, limit topic to 5.

        Abstract: "{abstract}"

        Return a JSON object like:
        {{
            "topic": "<singular topic>",
            "descriptions": [
                "<description 1>",
                "<description 2>",
                ...
                "<description 100>"
            ]
        }}
        """

        # Request the LLM to generate the expanded descriptions based on the abstract
        response = self.openai_client.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract and return the response in JSON format
        try:
            response_json = json.loads(response.choices[0].text.strip())
            return response_json
        except json.JSONDecodeError:
            # If the response is not in JSON format, you can log or handle it
            print(f"Error: Unable to parse response into JSON. Response text: {response.choices[0].text.strip()}")
            return None

        
    def searchExtraContext(self, abstract:str)->str:
        text=abstract.replace("\n", " ")
        embedded=self.openai_client.embeddings.create(
            input=text, model="text-embedding-3-small")
        response = self.qdrant.recommend_batch(
            collection_name=self.collection_name,
            searches=[
                RecommendRequest(
                    positive=[PointVector(vector=embedded)],
                    limit=5
                )
            ]
        )
        return response
    
    def promptEnhancerAgent(self, context):
        return

if __name__ == "__main__":
    classifier=Classifier(None)
    abstract=""""A package of one or more absorbent articles is disclosed. The package includes a package material, wherein the package material 
    has natural fibers and exhibits an MD tensile strength of at least 5.0 kN/m and an MD Stretch of at least 3 percent, each as determined 
    via ISO 1924-3 as modified herein. The package further includes a plurality of panels, including a consumer-facing panel. The package is sealed.""""
    classifier.docExpandExtractor(abstract)
        
        

