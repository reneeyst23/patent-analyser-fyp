from util import docProcessing
import os
import json

import re
# Initialize the docProcessing class
d = docProcessing()

# List all files in the directory
input_dir = "120_file"
output_dir = "output_files"

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each file
for filename in os.listdir(input_dir):
    match = re.search(r'(\d+)\.pdf$', filename)
        
    if match:
        inp= match.group(1)
        d.retrieveClaims(inp)
        res= json.dumps(d.json_temp)
    else:
        raise KeyError ("the file format isn't PDF")
    # Create a new output file for each result
    output_file = os.path.join(output_dir, f"{filename}.txt")
    with open(output_file, "w") as f:
        f.write(res)
    
    print(f"Results saved to {output_file}")

print("All files processed.")