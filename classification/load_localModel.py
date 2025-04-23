from trizClassification import load_resultData
from LLM import Openai, FriendliAI
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

openai_model = Openai()
r3_7b=FriendliAI("FRIENDLI_TOKEN")

load_resultData(openai_model, "classification/result.json", "classified_serialNumber.json")
