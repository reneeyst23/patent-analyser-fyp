import re
import json

# Load the text from a file
with open("kb.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Use regular expression to find all TRIZ entries
pattern = re.compile(
    r"\*\*\s*(.*?)\s*\((\d{1,2})\):\*\*\s*(.*?)(?=Examples?:\s)(?:Examples?:\s)(.*?)(?=\n\*|\Z)", 
    re.DOTALL
)
matches = pattern.findall(text)

# Structure the matches into a list of dictionaries
principles = []
for name, number, description, example in matches:
    principles.append({
        "number": int(number.strip()),
        "name": name.strip(),
        "description": description.strip().replace("\n", " "),
        "Example": example.strip().replace("\n", " ")
    })

# Write the structured data to JSON
with open("triz_principles0.json", "w", encoding="utf-8") as json_file:
    json.dump(principles, json_file, indent=4, ensure_ascii=False)

principles[:2]