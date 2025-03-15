import pytesseract
import pdf2image
import json
import re
import spacy
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time


class docProcessing:
    def __init__(self):
        #self.nlp=spacy.load("en_core_web_sm")
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
        section_mapping = {
        "field": [
            "FIELD",
            "FIELD OF INVENTION",
            "FIELD OF THE INVENTION",
            "TECHNICAL FIELD"
        ],
        "background": [
            "BACKGROUND",
            "BACKGROUND OF THE INVENTION",
            "BACKGROUND OF THE DISCLOSURE",
            "DESCRIPTION OF RELATED ARTS",
            "TECHNICAL PROBLEM"
        ],
        "summary": [
            "SUMMARY",
            "SUMMARY OF THE INVENTION",
            "SUMMARY OF THE DISCLOSURE",
            "TECHNICAL SOLUTION",
            "OBJECTS AND SUMMARY OF THE INVENTION"
        ],
        "visual_desc": [
            "BRIEF DESCRIPTION OF THE DRAWINGS",
            "BRIEF DESCRIPTION OF THE SEVERAL VIEW OF THE DRAWING",
            "BRIEF DESCRIPTION OF THE INVENTION",
            "DESCRIPTION OF DRAWINGS"
        ],
        "detail_desc": [
            "DETAILED DESCRIPTION",
            "DETAILED DESCRIPTION OF THE INVENTION",
            "DESCRIPTION OF THE PREFERRED EMBODIMENTS",
            "DETAILED DESCRIPTION OF THЕ DISCLOSURE",
            "DESCRIPTION OF EMBODIMENTS",
            "DESCRIPTION OF EMBODIMENTS OF THE PRESENT INVENTION"
        ]
    }
        all_patterns = []
        pattern_to_category = {}
        
        for category, titles in section_mapping.items():
            for title in titles:
                pattern = self.nlp.make_doc(title)
                all_patterns.append(pattern)
                pattern_to_category[title] = category
        
        # Initialize the PhraseMatcher
        matcher = PhraseMatcher(self.nlp.vocab)  # Case-insensitive matching
        matcher.add("SECTION_TITLES", None, *all_patterns)
        
        # Process the text
        doc = self.nlp(text)
        matches = sorted(matcher(doc), key=lambda x: x[1])
        
        # Initialize dictionary to store sections
        for category in section_mapping.keys():
            self.json_temp[category] = ""
        
        # If no matches were found, store entire text in detail_desc
        if not matches:
            self.json_temp["detail_desc"] = doc.text.strip()
            return
        
        # Process matches
        for i, (match_id, start_match, end_match) in enumerate(matches):
            current_title = doc[start_match:end_match].text
            current_category = pattern_to_category.get(current_title.upper(), None)
            
            # If this is the last section
            if i == len(matches) - 1:
                # Get content from end of title to end of document
                content = doc[end_match:].text.strip()
                if current_category:
                    self.json_temp[current_category] = content
            else:
                # Get content from end of this title to start of next title
                next_start = matches[i+1][1]
                content = doc[end_match:next_start].text.strip()
                if current_category:
                    self.json_temp[current_category] = content
        
        # Handle first section (content before first match)
        if matches and matches[0][1] > 0:
            first_content = doc[:matches[0][1]].text.strip()
            if first_content:
                # Store content before first section in detail_desc as fallback
                self.json_temp["detail_desc"] = first_content
    
    def retrieveClaims(self, filename):
        """
        input: pdf filename
        output: json format claims
        """
        token = "eyJzdWIiOiIxZTFhNGE1OS1kN2ZmLTQ1ZjMtOTc1MC0zN2QwNWVmOWE1M2YiLCJ2ZXIiOiI5MmNhNjA2Yy04YTU5LTQ2MjUtOTBhZC0zZDBkN2UxY2I4ZWQiLCJleHAiOjB9"
        link_template = f"https://ppubs.uspto.gov/dirsearch-public/patents/html/{filename}?source=US-PGPUB&requestToken={token}"
        gecko_driver_path = "/snap/bin/geckodriver"  
        service = Service(gecko_driver_path)
        driver = webdriver.Firefox(service=service)
        
        driver.get(link_template)
        time.sleep(10)
        driver.quit()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        claims_header = soup.find('h3', text='Claims')
        if claims_header:
            claims_section = claims_header.find_parent('section')
            claims_text = claims_section.get_text(separator=' ', strip=True)
            self.json_temp["claims"]=claims_text
        else:
            raise KeyError("unable to access claims, wait for token access")
       

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
        match = re.search(r'(\d+)\.pdf$', file)
        
        if match:
            inp= match.group(1)
            self.retrieveClaims(inp)
            return json.dumps(self.json_temp)
        else:
            raise KeyError ("the file format isn't PDF")