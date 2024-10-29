import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
from pathlib import Path
import os
import time
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import random
from src.config.config import config

class LERCrawler:
    """Crawler for Licensee Event Reports using Selenium"""
    
    def __init__(self):
        self.base_url = "https://lersearch.inl.gov/LERSearchCriteria.aspx"
        
        # Set up logging
        self._setup_logging()
        
        # Set up data directories
        self.data_dir = Path('data/raw/ler')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Chrome options
        self.chrome_options = self._setup_chrome_options()
        
        # Initialize Chrome driver with automatic ChromeDriver management
        self.service = Service(ChromeDriverManager().install())
        
        self.logger.info("LER Crawler initialized")
    
    def _setup_chrome_options(self) -> Options:
        """Setup Chrome options"""
        options = Options()
        
        arguments = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--window-size=1920,1080',
            '--start-maximized',
            # '--headless'  # 디버깅을 위해 주석 처리
        ]
        
        for arg in arguments:
            options.add_argument(arg)
        
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ler_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _random_sleep(self, min_seconds: float = 1, max_seconds: float = 3):
        """Random sleep to avoid detection"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def _wait_and_find_element(self, driver: webdriver.Chrome, by: By, value: str, timeout: int = 10):
        """Wait for element and return it when found"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            self.logger.error(f"Error finding element {value}: {str(e)}")
            driver.save_screenshot(str(self.data_dir / f'error_finding_{value}.png'))
            raise
    
    def _set_date_range(self, driver: webdriver.Chrome):
        """Set date range"""
        try:
            # Start Date
            start_month = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_DropDownEventStartMonth")
            Select(start_month).select_by_visible_text("Jan")
            self._random_sleep()
            
            start_day = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_DropDownEventStartDay")
            Select(start_day).select_by_visible_text("1")
            self._random_sleep()
            
            start_year = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_DropDownEventStartYear")
            Select(start_year).select_by_visible_text("2019")
            self._random_sleep()
            
            # End Date
            end_month = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_DropDownEventEndMonth")
            Select(end_month).select_by_visible_text("Dec")
            self._random_sleep()
            
            end_day = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_DropDownEventEndDay")
            Select(end_day).select_by_visible_text("31")
            self._random_sleep()
            
            end_year = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_DropDownEventEndYear")
            Select(end_year).select_by_visible_text("2023")
            
            self.logger.info("Date range set successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting date range: {str(e)}")
            driver.save_screenshot(str(self.data_dir / 'error_date_range.png'))
            raise

    def _set_reactor_and_vendor(self, driver: webdriver.Chrome):
        """Set reactor type and vendor"""
        try:
            # Select PWR
            pwr_checkbox = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_CheckBoxReactorTypePWR")
            if not pwr_checkbox.is_selected():
                pwr_checkbox.click()
                self._random_sleep()
            
            # Select Westinghouse
            we_checkbox = self._wait_and_find_element(
                driver, By.ID, "ContentPlaceHolderMainPageContent_CheckBoxWE")
            if not we_checkbox.is_selected():
                we_checkbox.click()
                self._random_sleep()
            
            self.logger.info("Reactor type and vendor set successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting reactor type and vendor: {str(e)}")
            driver.save_screenshot(str(self.data_dir / 'error_reactor_vendor.png'))
            raise

    def _set_nrc_regions(self, driver: webdriver.Chrome):
        """Set NRC regions"""
        try:
            regions = ["I", "II", "III", "IV"]
            for i, region in enumerate(regions):
                region_checkbox = self._wait_and_find_element(
                    driver, By.ID, f"ContentPlaceHolderMainPageContent_CheckBoxListNRCRegion_{i}")
                if not region_checkbox.is_selected():
                    region_checkbox.click()
                    self._random_sleep()
            
            self.logger.info("NRC regions set successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting NRC regions: {str(e)}")
            driver.save_screenshot(str(self.data_dir / 'error_regions.png'))
            raise

    def _set_operating_modes(self, driver: webdriver.Chrome):
        """Set operating modes"""
        try:
            modes = [
                "Power Operation", "Hot Shutdown", "Refueling",
                "Startup", "Cold Shutdown", "Other", "Hot Standby"
            ]
            
            for i, mode in enumerate(modes):
                mode_checkbox = self._wait_and_find_element(
                    driver, By.ID, f"ContentPlaceHolderMainPageContent_CheckBoxListOperatingMode_{i}")
                if not mode_checkbox.is_selected():
                    mode_checkbox.click()
                    self._random_sleep()
            
            self.logger.info("Operating modes set successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting operating modes: {str(e)}")
            driver.save_screenshot(str(self.data_dir / 'error_modes.png'))
            raise

    def _get_pdf_links(self, driver: webdriver.Chrome) -> List[Tuple[str, str]]:
        """Get all PDF download links and their file names from search results"""
        try:
            # 모든 PDF 아이콘 이미지를 찾음
            pdf_elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='pdf.gif']")
            self.logger.info(f"Found {len(pdf_elements)} PDF links")
            
            # PDF 링크와 파일명 수집
            pdf_links = []
            for pdf_element in pdf_elements:
                try:
                    # PDF 링크의 부모 앵커 태그 찾기
                    link = pdf_element.find_element(By.XPATH, "./..")
                    href = link.get_attribute("href")
                    
                    # LER 번호 찾기 (파일명으로 사용)
                    row = link.find_element(By.XPATH, "./../../..")
                    ler_number = row.find_elements(By.TAG_NAME, "td")[1].text.strip()
                    
                    pdf_links.append((href, f"{ler_number}.pdf"))
                    
                except Exception as e:
                    self.logger.error(f"Error getting link from PDF element: {str(e)}")
                    continue
            
            return pdf_links
            
        except Exception as e:
            self.logger.error(f"Error finding PDF links: {str(e)}")
            return []

    def _download_pdf(self, url: str, filename: str) -> bool:
        """Download PDF file"""
        try:
            # PDF 저장 디렉토리 생성
            pdf_dir = self.data_dir / 'pdfs'
            pdf_dir.mkdir(parents=True, exist_ok=True)
            
            # 파일 다운로드
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                pdf_path = pdf_dir / filename
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"Successfully downloaded {filename}")
                return True
            else:
                self.logger.error(f"Failed to download {filename}: Status code {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading {filename}: {str(e)}")
            return False

    def collect_ler_data(self) -> pd.DataFrame:
        """Main method to collect LER data"""
        driver = None
        try:
            self.logger.info("Starting LER data collection")
            
            driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            driver.maximize_window()
            
            # Navigate to page
            driver.get(self.base_url)
            self._random_sleep(5, 7)
            
            # Take screenshot of initial page
            driver.save_screenshot(str(self.data_dir / 'initial_page.png'))
            self.logger.info("Accessed LER search page")
            
            try:
                # Set search criteria
                self._set_date_range(driver)
                self._set_reactor_and_vendor(driver)
                self._set_nrc_regions(driver)
                self._set_operating_modes(driver)
                
                # Take screenshot before search
                driver.save_screenshot(str(self.data_dir / 'before_search.png'))
                
                # Click search button
                search_button = self._wait_and_find_element(
                    driver, By.ID, "ContentPlaceHolderMainPageContent_Button_SearchTop")
                search_button.click()
                self.logger.info("Search initiated")
                
                # Wait for results to load (specifically waiting for PDF icons)
                try:
                    WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='pdf.gif']"))
                    )
                    self.logger.info("Search results loaded")
                except TimeoutException:
                    self.logger.error("Timeout waiting for search results")
                    driver.save_screenshot(str(self.data_dir / 'timeout_results.png'))
                    raise
                
                # Save results page screenshot
                driver.save_screenshot(str(self.data_dir / 'search_results.png'))
                
                # Get all PDF links
                pdf_links = self._get_pdf_links(driver)
                
                # Download PDFs
                successful_downloads = 0
                if pdf_links:
                    self.logger.info(f"Found {len(pdf_links)} PDF links")
                    for url, filename in pdf_links:
                        if self._download_pdf(url, filename):
                            successful_downloads += 1
                        self._random_sleep(1, 2)  # 다운로드 간 딜레이
                    
                    self.logger.info(f"Successfully downloaded {successful_downloads} of {len(pdf_links)} PDFs")
                else:
                    self.logger.warning("No PDF links found")
                
                # Parse results page for data
                results = self._parse_search_results(driver.page_source)
                
                # Create DataFrame
                df = pd.DataFrame(results)
                
                # Save results to CSV
                output_file = self.data_dir / 'ler_data_filtered.csv'
                df.to_csv(output_file, index=False)
                self.logger.info(f"Saved {len(df)} records to {output_file}")
                
                return df
                
            except Exception as e:
                self.logger.error(f"Error during search process: {str(e)}")
                driver.save_screenshot(str(self.data_dir / 'error_search.png'))
                raise
                
        except Exception as e:
            self.logger.error(f"Error in data collection: {str(e)}")
            if driver:
                driver.save_screenshot(str(self.data_dir / 'error_final.png'))
            raise
            
        finally:
            if driver:
                driver.quit()

    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results from page source"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        try:
            table = soup.find('table', id='ContentPlaceHolderMainPageContent_GridViewSearchResults')
            if table:
                # Process rows
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if len(cols) >= 7:
                        try:
                            result = {
                                'report_number': cols[1].text.strip(),
                                'accession_number': cols[2].text.strip(),
                                'event_date': cols[3].text.strip(),
                                'plant': cols[4].text.strip(),
                                'title': cols[5].text.strip()
                            }
                            results.append(result)
                        except Exception as e:
                            self.logger.error(f"Error processing row: {str(e)}")
                            continue
                
                self.logger.info(f"Parsed {len(results)} results")
            
        except Exception as e:
            self.logger.error(f"Error parsing results: {str(e)}")
            
        return results

if __name__ == "__main__":
    try:
        crawler = LERCrawler()
        df = crawler.collect_ler_data()
        print(f"Successfully collected {len(df)} LER records")
    except Exception as e:
        print(f"Error: {str(e)}")