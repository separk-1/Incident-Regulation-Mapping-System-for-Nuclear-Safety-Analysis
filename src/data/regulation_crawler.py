import requests
from bs4 import BeautifulSoup
import json
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional
import time

class NRCRegulationCrawler:
    """Crawler for NRC regulations"""
    
    def __init__(self):
        self.base_url = "https://www.nrc.gov/reading-rm/doc-collections/cfr/part050"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Set up logging
        self._setup_logging()
        
        # Set up data directories
        self.data_dir = Path('data/raw/regulations')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('regulation_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def collect_regulations(self) -> List[Dict]:
        """Main method to collect NRC regulations"""
        try:
            self.logger.info("Starting NRC regulation collection")
            
            # Get main page
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Failed to access NRC website: {response.status_code}")
            
            # Parse regulations
            soup = BeautifulSoup(response.text, 'html.parser')
            regulations = self._parse_regulations(soup)
            
            # Save data
            output_file = self.data_dir / 'nrc_regulations.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(regulations, f, indent=2)
            
            self.logger.info(f"Saved {len(regulations)} regulations to {output_file}")
            
            return regulations
            
        except Exception as e:
            self.logger.error(f"Error during regulation collection: {str(e)}")
            raise
    
    def _parse_regulations(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse regulations from main page"""
        regulations = []
        
        # Find regulation sections
        sections = soup.find_all('div', class_='regtext')
        for section in sections:
            try:
                # Extract section number
                section_num = section.find('h2')
                if not section_num:
                    continue
                section_num = section_num.text.strip()
                
                # Extract title
                title = section.find('h3')
                title = title.text.strip() if title else ''
                
                # Extract content
                content = section.find('div', class_='regtext')
                content = content.text.strip() if content else ''
                
                # Extract references
                references = self._extract_references(section)
                
                regulation = {
                    'section_number': section_num,
                    'title': title,
                    'content': content,
                    'references': references,
                    'categories': self._extract_categories(content),
                    'requirements': self._extract_requirements(content)
                }
                
                regulations.append(regulation)
                
                # Add delay to avoid overwhelming the server
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error parsing section {section_num if 'section_num' in locals() else 'unknown'}: {str(e)}")
                continue
        
        return regulations
    
    def _extract_references(self, section: BeautifulSoup) -> List[str]:
        """Extract references from regulation section"""
        references = []
        ref_elements = section.find_all('a', class_='reference')
        for ref in ref_elements:
            ref_text = ref.text.strip()
            if ref_text:
                references.append(ref_text)
        return references
    
    def _extract_categories(self, content: str) -> List[str]:
        """Extract categories from regulation content"""
        categories = []
        category_keywords = [
            'safety', 'security', 'emergency', 'operation', 'maintenance',
            'training', 'quality assurance', 'reporting', 'inspection'
        ]
        
        for keyword in category_keywords:
            if re.search(rf'\b{keyword}\b', content.lower()):
                categories.append(keyword)
        
        return list(set(categories))  # Remove duplicates
    
    def _extract_requirements(self, content: str) -> List[str]:
        """Extract requirements from regulation content"""
        requirements = []
        sentences = re.split(r'[.!?]+', content)
        
        requirement_keywords = ['must', 'shall', 'required', 'necessary', 'mandatory']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in requirement_keywords):
                requirements.append(sentence)
        
        return requirements

if __name__ == "__main__":
    # Create and run crawler
    crawler = NRCRegulationCrawler()
    try:
        regulations = crawler.collect_regulations()
        print(f"Successfully collected {len(regulations)} regulations")
    except Exception as e:
        print(f"Error: {str(e)}")