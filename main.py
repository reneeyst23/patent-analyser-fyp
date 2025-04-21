import json
import ast
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunking(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    background_description_chunks = []
    claims_abstract_chunks = []

    for item in data:
        serial_number = item.get("serial_number", "unknown")
        essential_raw = item.get("essential_data", "{}")
        background_summ = item.get("background_summary", "")
        description = item.get("description", "")
        claims = item.get("claims", "")

        # Skip if any critical section is None or empty
        if not essential_raw or not background_summ or not description or not claims:
            continue

        try:
            essential = ast.literal_eval(essential_raw)
        except (ValueError, SyntaxError):
            continue  # skip invalid essential_data entries

        title = essential.get("title", "")
        abstract = essential.get("abstract", "")
        date = essential.get("date", "")

        # First set: background + description
        first_text = background_summ + "\n" + description
        if first_text.strip():  # skip if empty after cleaning
            first_chunks = text_splitter.create_documents(
                [first_text],
                metadatas=[{
                    "serial_number": serial_number,
                    "publish_date": date,
                    "section": "background+description",
                    "abstract": abstract,
                    "title": title
                }]
            )
            background_description_chunks.extend(first_chunks)

        # Second set: claims + abstract
        second_text = claims + "\n" + abstract
        if second_text.strip():
            second_chunks = text_splitter.create_documents(
                [second_text],
                metadatas=[{
                    "serial_number": serial_number,
                    "publish_date": date,
                    "section": "claims+abstract",
                    "abstract": abstract,
                    "title": title
                }]
            )
            claims_abstract_chunks.extend(second_chunks)

    return background_description_chunks, claims_abstract_chunks


json_path = "data_extraction/result.json"
bg_chunks, cl_chunks = chunking(json_path)
print(f"Background + Description: {len(bg_chunks)} chunks")
print(f"Claims + Abstract: {len(cl_chunks)} chunks")

json_path="data_extraction/result.json"
