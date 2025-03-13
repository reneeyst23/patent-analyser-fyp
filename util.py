import pytesseract
import pdf2image
import json
import re
import spacy
import selenium
from bs4 import BeautifulSoup



class docProcessing:
    def __init__(self):
        self.nlp=spacy.load("en_core_web_sm")
        self.json_temp={
            "essential_data":"",
            "patent_cover":"",
            "background":"",
            "summary":"",
            "visual_desc": "",
            "detail_desc":"",
            "claims":""
        }
    def pdfConversion(self, file: str):
        """
        Input: PDF patent docs
        Output: converted txt file
        """
        pages = pdf2image.convert_from_path(file)
        text = ""
        for page in pages:
            page_text = pytesseract.image_to_string(page)
            page_text=page_text.replace("\n", " ")
            text += page_text + "\n"
        self.printTXT(file, text)

    def essentialInfo(self, stdment:str) -> list:
        """
        Parse patent text and extract specific fields.
        Args:
            text (str): The patent text to parse.
        Returns:
            dict: A dictionary containing the extracted fields.
        """
        result = {}


        title_match = re.search(r"\(54\)\s+([^\n]+)", stdment)
        if title_match:
            result["title"] = title_match.group(1).strip()
        
        applicant_match = re.search(r"\(71\) Applicant\s+([^\n]+)", stdment)
        result["applicant"]=applicant_match.group(1).strip()

        pub_date_match = re.search(r"Pub\. Date:\s+([^\n]+)", stdment)
        if pub_date_match:
            result["pub_date"] = pub_date_match.group(1).strip()
            
        abstract_match = re.search(r"(?:Abstract|\(57\)\s*ABSTRACT)[\s:\-]*([\s\S]*?)(?=\n\s*\n|\Z)", stdment)
        if abstract_match:
            result["abstract"] = abstract_match.group(1).strip()
        
        self.json["essential_data"]=result
        
    def printTXT(self, name:str, strings):
        """
        Input: text string
        Output: txt file
        """
        txt_name = f"{name}_txt"
        with open(txt_name, "a") as txt:
            txt.write(strings)
            
        
    def section_processing(self, text: str):
        """
        Process the text and extract sections based on titles.
        Args:
            text (str): The text containing section titles and content.
        Returns:
            None: The extracted sections are stored in `self.json_temp`.
        """
        # Define the section titles to match
        section_titles = [
            "FIELD",
            "BACKGROUND",
            "SUMMARY", 
            "SUMMARY OF INVENTION", 
            "DESCRIPTION OF DRAWINGS", 
            "DESCRIPTION OF EMBODIMENTS", 
            "DETAILED DESCRIPTION"
        ]
        
        # Initialize the PhraseMatcher
        matcher = PhraseMatcher(self.nlp.vocab)
        patterns = [self.nlp.make_doc(title) for title in section_titles]
        matcher.add("SECTION_TITLES", patterns)
        
        # Process the text
        doc = self.nlp(text)
        matches = sorted(matcher(doc), key=lambda x: x[1])
        
        prev_title = None
        prev_end = 0
        
        # Iterate through the matches to extract sections
        for match_id, start_match, end_match in matches:
            section_title = doc[start_match:end_match].text
            
            # Extract text between section titles and assign it to the correct field
            if prev_end != 0:
                section_content = doc[prev_end:start_match].text.strip()
                
                if prev_title in ["FIELD", "FIELD OF INVENTION"]:
                    self.json_temp["field"] = section_content
                elif prev_title in ["SUMMARY", "SUMMARY OF INVENTION"]:
                    self.json_temp["summary"] = section_content
                elif prev_title == "BACKGROUND":
                    self.json_temp["background"] = section_content
                elif prev_title == "DESCRIPTION OF DRAWINGS":
                    self.json_temp["visual_desc"] = section_content
                elif prev_title in ["DETAILED DESCRIPTION", "DESCRIPTION OF EMBODIMENTS"]:
                    self.json_temp["detail_desc"] = section_content
            
            # Update the previous section title and end position
            prev_title = section_title
            prev_end = end_match

            if section_title in ["DETAILED DESCRIPTION", "DESCRIPTION OF EMBODIMENTS"]:
                self.json_temp["detail_desc"] = doc[end_match:].text
    
    def retrieveClaims(self, filename:str):
        link_template= f"https://ppubs.uspto.gov/dirsearch-public/patents/html/{filename}?source=US-PGPUB&requestToken={token}"
        driver = webdriver.Chrome(executable_path="/path/to/chromedriver")
        driver.get(link)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        claims_header = soup.find('h3', text='Claims')
        if claims_header:
            claims_section = claims_header.find_parent('section')
            claims_text = claims_section.get_text(separator=' ', strip=True)
            self.json_temp["claims"]=claims_text
        else:
            print("No 'Claims' section found.")
        

    def prodConversion(self, file:str):
        """
        Input: PDF patent docs
        Output: converted txt file
        """
        remain=""
        pages = pdf2image.convert_from_path(file)
        for x in range(len(pages)):
            page_text = pytesseract.image_to_string(pages[x]).replace('\n', ' ').strip()
            if x == 0:
                self.saveCover(pages[0])
                self.essentialInfo(page_text[0])
            else:
                remain += page_text
        self.section_processing(remain)
        return json.dumps(self.json_temp)