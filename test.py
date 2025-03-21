import os
import re
import json
from util import DocProcessing

lst = os.listdir("/mnt/d/fit3164/patent-analyser-fyp/120_file")
res = []

for l in lst:
    try:
        d = DocProcessing()
        # Extract the 11-digit code using regex
        code_match = re.search(r"\d{11}", l)
        if code_match:
            code = code_match.group(0)
            
            # Retrieve the HTML content for the extracted code
            text = d.retrieveHTML(code)
            
            d.essentialInfo(text)
            # Process the sections from the retrieved HTML
            d.section_processing(text)
            
            # Append the processed data to the result list
            res.append(d.json_temp)

    except Exception as e:
        print(f"Error processing file {l}: {e}")
        # Append the partially processed result if any before the error
        res.append(d.json_temp)
        continue  # Continue processing the next file

# Save the result to a JSON file
with open('result.json', 'w') as json_file:
    json.dump(res, json_file, indent=4)

print("Processing complete. Result saved to 'result.json'.")


Error processing file 20230378766.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240088669.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240117977.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240146639.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240258616.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240330345.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240352347.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240367207.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20240368407.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20250072413.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20250074851.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20250075222.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
Error processing file 20250078096.pdf: cannot access local variable 'paragraphs' where it is not associated with a value
