import os
import re
import requests



def extract_into_set(file_path, patent_ids):
    pattern = r"\b\d{11}\b"
    with open(file_path, 'r') as file:
        text = file.read()
        matches = re.findall(pattern, text)
        for match in matches:
            patent_ids.add(match)
    return patent_ids

file_path = 'id_document_patent.txt'

s = set()
def check(s):
    user_name = input("Enter your name: ")
    file_name = f"{user_name}_patentids.txt"
    query = input("What's your query list: ")
    with open(file_name, 'a') as outfile:
        outfile.write(f"{query}:\n")
    while True:
        user_input = input("Enter a string (or type 'STOP' to quit): ")
        if user_input.strip().upper() == "STOP" or user_input.strip() == "":
            print("Exiting the program...")
            break

        if user_input not in s and user_input is not None:
            s.add(user_input)
            with open(file_name, 'a') as outfile:
                outfile.write(f"{user_input}\n")
            print(f"'{user_input}' has been saved to {file_name}")
        else:
            print(f"'{user_input}' is in the set. Try again!")

def download_pdf(collection: set, fold_name):
    # Create the folder if it doesn't exist
    os.makedirs(fold_name, exist_ok=True)
    
    # The token and base URL for downloading
    token = "eyJzdWIiOiJmMjRkODZmYS01YzY0LTQ5MTYtOGEzMC1iMTk3NTZhODMwMTUiLCJ2ZXIiOiJiYjFkYWY0OS1lODZmLTQ3MmEtOTI1Yi02MzRhYjZmZGU2OTgiLCJleHAiOjB9"
    base_url = "https://ppubs.uspto.gov/dirsearch-public/print/downloadBasicPdf/{query}?requestToken={token}"
    
    # Loop through the collection of patent numbers
    for x in collection:
        # Extract the patent number using regex (assuming it's an 11-digit number)
        y = re.findall(r"\b\d{11}\b", x)
        
        if y:  # Proceed only if a patent number was found
            patent_number = y[0]
            
            # Construct the output file path
            output_file = os.path.join(fold_name, f"{patent_number}.pdf")
            
            # Check if the file already exists
            if os.path.exists(output_file):
                print(f"{patent_number}.pdf already exists. Skipping download.")
                continue  # Skip downloading if the file already exists
            
            # Construct the download URL
            download_url = base_url.format(query=patent_number, token=token)
            
            # Send a GET request to download the PDF
            response = requests.get(download_url)
            
            if response.status_code == 200:
                # Write the content to the output file
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {patent_number} to {output_file}")
            else:
                print(f"Failed to download {patent_number}. Status code: {response.status_code}")

file_count = len([f for f in os.listdir('120_file') if os.path.isfile(os.path.join('120_file', f))])
print(f"There are {file_count} files in the folder.")