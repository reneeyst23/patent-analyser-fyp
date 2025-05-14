from typing import Optional
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydantic import BaseModel, Field

class PatentDocument(BaseModel):
    """Pydantic model for patent document structure with proper field definitions"""
    title: Optional[str] = Field(
        default=None,
        description="Title of the patent",
        example="System and method for automated patent analysis"
    )
    inventor: Optional[str] = Field(
        default=None,
        description="Name(s) of the inventor(s)",
        example="Smith, John; Doe, Jane"
    )
    publication_date: Optional[str] = Field(
        default=None,
        description="Publication date in YYYY-MM-DD format",
        example="2023-05-15"
    )
    abstract: Optional[str] = Field(
        default=None,
        description="Patent abstract text",
        example="A system for analyzing patent documents..."
    )
    background_summary: Optional[str] = Field(
        default=None,
        description="Combined background and summary section",
        example="The field of invention relates to..."
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the invention",
        example="Referring to FIG. 1, the system comprises..."
    )
    claims: Optional[str] = Field(
        default=None,
        description="Patent claims text",
        example="1. A system comprising: a processor configured to..."
    )
    
    def to_string(self) -> str:
        """Concatenate all fields into a single formatted string."""
        parts = [
            f"Title: {self.title}" if self.title else "",
            f"Inventor(s): {self.inventor}" if self.inventor else "",
            f"Publication Date: {self.publication_date}" if self.publication_date else "",
            f"Abstract:\n{self.abstract}" if self.abstract else "",
            f"Background & Summary:\n{self.background_summary}" if self.background_summary else "",
            f"Description:\n{self.description}" if self.description else "",
            f"Claims:\n{self.claims}" if self.claims else "",
        ]
        return "\n\n".join([part for part in parts if part.strip()])

    def __str__(self):
        return self.to_string()
    
class DocProcessing:
    def __init__(self):
        self.document = PatentDocument()
        
    def printTXT(self, name: str, content: str):
        """
        Write extracted content to a TXT file.
        
        Args:
            name: Base filename (without extension)
            content: Text content to write
        """
        with open(f"{name}.txt", "w", encoding="utf-8") as file:
            file.write(content)


    def retrieveHTML(self, filename: str) -> str:
        """
        Retrieve HTML content using Selenium WebDriver.
        Navigates to USPTO site, performs a search, finds the "Text" link,
        modifies its target to '_self', clicks it, and returns the HTML of the detailed result page.
        """
        link = "https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html"
        gecko_driver_path = "/snap/bin/geckodriver"
        service = Service(gecko_driver_path)
        options = Options()

        driver = webdriver.Firefox(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        try:
            driver.get(link)

            # Step 1: Enter document number and search
            quick_lookup_input = wait.until(EC.presence_of_element_located((By.ID, "quickLookupTextInput")))
            quick_lookup_input.send_keys(filename)
            search_button = driver.find_element(By.ID, "quickLookupSearchBtn")
            search_button.click()

            # Step 2: Wait for search results to appear
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.searchResultsArea:not(.d-none)")))
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//table[@id='searchResults']//tbody/tr[not(contains(., 'No records found'))]"))
            )
            text_api_link = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/api/patents/html/') and contains(text(), 'Text')]"))
            )
            
            driver.execute_script("arguments[0].setAttribute('target', '_self');", text_api_link)
            text_api_link.click()
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            html_source = driver.page_source

        finally:
            driver.quit()

        return html_source

    def extract_section_text(self, soup: BeautifulSoup, section_title: str) -> Optional[str]:
        """
        Helper method to extract text from a specific section.
        
        Args:
            soup: BeautifulSoup object
            section_title: The section header text to find
            
        Returns:
            Extracted text or None if section not found
        """
        header = soup.find('h3', string=section_title)
        if not header:
            return None
            
        section = []
        current = header.find_next()
        while current and current.name != 'h3':
            if current.name == 'p':
                section.append(current.get_text(strip=True))
            current = current.find_next()
            
        return ' '.join(section) if section else None

    def process_document(self, filename: str) -> PatentDocument:
        """
        Main processing pipeline for a patent document.
        
        Args:
            filename: USPTO document identifier
            
        Returns:
            Populated PatentDocument instance
        """
        html = self.retrieveHTML(filename)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract metadata
        self.document.title = soup.find('h2', class_='bottom-border padding').get_text(strip=True)
        
        inventor_label = soup.find('span', string="Inventor(s)")
        if inventor_label:
            self.document.inventor = inventor_label.find_next('span').get_text(strip=True)
            
        date_label = soup.find('span', string="Publication Date")
        if date_label:
            self.document.publication_date = date_label.find_next('span').get_text(strip=True)
        
        # Extract sections
        self.document.abstract = self.extract_section_text(soup, 'Abstract')
        self.document.background_summary = self.extract_section_text(soup, 'Background/Summary')
        self.document.description = self.extract_section_text(soup, 'Description')
        
        # Claims require special handling
        claims_header = soup.find('h3', string='Claims')
        if claims_header:
            claims_section = claims_header.find_parent('section')
            self.document.claims = claims_section.get_text(separator=' ', strip=True)
        
        return self.document

        
        