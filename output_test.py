import polars as pl
import json

# Read the JSON file into a Polars DataFrame
df = pl.read_json("classified_serialNumber_temp1_fewShot_gpt.json")

# Filter rows where the 'principles' list inside the 'Results' struct is non-empty
filtered_df = df.filter(pl.col("Results").struct.field("principles").list.len() > 0)
json_data = filtered_df.to_dicts()

# Add metadata to the JSON structure
metadata = {
    "created_at": "2025-04-23",
    "source": "model=gpt-40, temp=1, multi-shot (knowledgebase), limited knowledgebase",
    "description": "Filtered data with TRIZ principles numbers extracted"
}

# Combine metadata and data
output_data = {
    "metadata": metadata,
    "data": json_data
}

# Write the output to a JSON file
with open("classified_result.json", "w") as f:
    json.dump(output_data, f, indent=4)

print("JSON file with metadata saved as 'filtered_data_with_metadata.json'")










