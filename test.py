import json
import re
import pandas as pd
import os
from util import docProcessing

# Initialize the docProcessing object
d = docProcessing()

# Read the existing JSON file
df = pd.read_json("test_data.json")

# Initialize an empty list
js = []

# List the files in the directory
files = os.listdir("120_file")

# Iterate through files and append the results from prodConversion()
for file in files:
    js.append(d.prodConversion())

# Convert the list 'js' into JSON format and save it as a new file
with open('output_data.json', 'w') as json_file:
    json.dump(js, json_file)

print("Data has been successfully written to output_data.json.")

