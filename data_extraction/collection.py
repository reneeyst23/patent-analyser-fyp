import os
import re
import requests



def extract_into_set(folder_path, id):
    """
    Extracts patent IDs from all PDF files in the specified folder and adds them to the provided set.

    Args:
        folder_path (str): The path to the folder containing PDF files.
        patent_ids (set): A set to store the extracted patent IDs.

    Returns:
        set: The updated set of patent IDs.
    """
    pattern = r"\b\d{11}\b"

    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):  # Only process PDF files
            code = os.path.splitext(filename)[0]
            id.add(code)
    return id

def check(s:set):
    """
    Check the name of files is already inside the list or not, take notes if its not there

    Args:
        s(set)
    Returns:
        a new txt file to go through function download_pdf()
    """
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
            


def download_pdf(collection, fold_name):
    """
    Check the name of files is already inside the list or not, take notes if its not there
    Args:
        collection(list or set): containing IDs of patents documents
        fold_name(folder name): folder name to create
    Returns:
        folder containing the all the pdf files
    """
    # Create the folder if it doesn't exist
    os.makedirs(fold_name, exist_ok=True)
    
    # The token and base URL for downloading (UPDATE THE TOKEN WHEN YOU NEED)
    token = "eyJzdWIiOiJkMGVjYWVjNC1iNTg1LTQ3MTYtYjcyZC1lMzk3YmY2Y2FkNTIiLCJ2ZXIiOiJkNjQ1N2EyMS1mZWRlLTQzNDgtOGQ1NC00N2E0OThhYjdiZmEiLCJleHAiOjB9"
    base_url = "https://ppubs.uspto.gov/dirsearch-public/print/downloadBasicPdf/{query}?requestToken={token}"

    for x in collection:
        y = re.findall(r"\b\d{11}\b", x)
        if y:  # Proceed only if a patent number was found
            patent_number = y[0]
            output_file = os.path.join(fold_name, f"{patent_number}.pdf")
            if os.path.exists(output_file):
                print(f"{patent_number}.pdf already exists. Skipping download.")
                continue 
            
            # Construct the download URL
            download_url = base_url.format(query=patent_number, token=token)
            
            # Send a GET request to download the PDF
            response = requests.get(download_url)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {patent_number} to {output_file}")
            else:
                print(f"Failed to download {patent_number}. Status code: {response.status_code}")
                
s = set()  # Correct way to initialize a set in Python
s = extract_into_set("120_file", s)

