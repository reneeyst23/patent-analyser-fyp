mport json
from data_extraction.textProcessing import DocProcessing

# Initialize DocProcessing
d = DocProcessing()
text = d.retrieveHTML("20220055720")
d.essentialInfo(text)
d.section_processing(text)
print(d.json_temp)
with open('20220055720.json', 'w') as json_file:
    json.dump(d.json_temp, json_file, indent=4)

print("JSON saved as 20220055720.json")

