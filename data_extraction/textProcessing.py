import json
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

class DocProcessing:
    def __init__(self):
        self.json_temp = {
            "title":"",
            "inventor":"",
            "abstract":"",
            "background_summary": "",
            "description": "",
            "claims": "",
        }
        
    def printTXT(self, name: str, strings: str):
        """
        Write extracted strings to a TXT file.
        """
        txt_name = f"{name}.txt"
        with open(txt_name, "w") as file:
            file.write(strings)

    def retrieveHTML(self, filename: str) -> str:
        """
        Retrieve HTML content using Selenium WebDriver.
        """
        token = "eyJzdWIiOiJiNmU0NDU0My02NjRlLTQwYzUtYjZhMC1hMmI1ZmM2N2ZiZTciLCJ2ZXIiOiJlMTNhODNiOC00NGY4LTQ5ZDUtYmY2ZS05MDBkNmU5YzQwOGEiLCJleHAiOjB9"
        link_template = f"https://ppubs.uspto.gov/dirsearch-public/patents/html/{filename}?source=US-PGPUB&requestToken={token}"
        gecko_driver_path = "/snap/bin/geckodriver"
        service = Service(gecko_driver_path)
        
        options=Options()
        options.headless=True
        
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(link_template)
        time.sleep(3)
        html_source = driver.page_source
        driver.quit()
        return html_source

    def retrieveClaims(self, page: str):
        """
        Extract claims section from HTML content.
        """
        soup = BeautifulSoup(page, 'html.parser')
        claims_header = soup.find('h3', text='Claims')
        if claims_header:
            claims_section = claims_header.find_parent('section')
            claims_text = claims_section.get_text(separator=' ', strip=True)
            self.json_temp["claims"] = claims_text
        else:
            raise KeyError("Unable to access claims. Please ensure proper token access.")

    def essentialInfo(self, page: str) -> dict:
        """
        Extract essential patent information from the HTML content.
        """
        soup = BeautifulSoup(page, 'html.parser')

        # Extract abstract
        abstract_h = soup.find('h3', text='Abstract')
        abstract_text = abstract_h.find_next('p').text.strip() if abstract_h else None

        # Extract title
        h2_tag = soup.find('h2', class_='bottom-border padding')
        title = h2_tag.text.strip() if h2_tag else None

        # Extract inventor name
        inventor_label = soup.find('span', string="Inventor(s)")
        inventor_name = inventor_label.find_next('span').text.strip() if inventor_label else None

        # Extract publication date
        date_label = soup.find('span', string="Publication Date")
        publication_date = date_label.find_next('span').text.strip() if date_label else None

        # Populate essential data
        result = {
            'title': title,
            'inventor': inventor_name,
            'date': publication_date,
            'abstract': abstract_text
        }
        self.json_temp["title"]=title
        self.json_temp["inventor"]=inventor_name
        self.date["date"]=publication_date
        self.abstract["abstract"]=abstract_text
        
        return result

    def section_processing(self, page: str):
        """
        Extract background, summary, description, and claims sections from the HTML content.
        """
        soup = BeautifulSoup(page, 'html.parser')

        # Extract Background/Summary
        backsum_header = soup.find('h3', text='Background/Summary')
        if backsum_header:
            paragraphs = []
            current_element = backsum_header.find_next()
            while current_element and current_element.name != 'h3':
                if current_element.name == 'p':
                    paragraphs.append(current_element.text.strip())
                current_element = current_element.find_next()
                
        background_summary = ' '.join(paragraphs)
        self.json_temp["background_summary"]=background_summary
        description_header = soup.find('h3', text='Description')
        if description_header:
            desc = description_header.find_next('p').text.strip()
            self.json_temp["description"] = desc
            
        self.retrieveClaims(page)


        
        