from util import docProcessing
import re
d= docProcessing()

pattern = re.compile(r"(\d+)\.pdf\.txt")

# Example filename
path = "20240112227.pdf.txt"

# Extract the code from the filename
match = pattern.search(path)
if match:
    code = match.group(1)  # Extract the numeric part (e.g., "20240112227")
    print(f"Extracted code: {code}")

    # Call the retrieveClaims function with the extracted code
    d.retrieveClaims(code)
    d.json_temp["code"]=code
    print(d.json_temp)
else:
    print("No code found in the filename.")
