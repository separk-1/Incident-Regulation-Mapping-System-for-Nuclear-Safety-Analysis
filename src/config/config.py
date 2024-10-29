from pathlib import Path
import yaml
from typing import Dict, Any
import logging
import os
from dotenv import load_dotenv

class Config:
    """Configuration management for the project"""
    
    def __init__(self):
        # Load .env file
        load_dotenv()
        
        # Set up base paths
        self.ROOT_DIR = Path(__file__).parent.parent.parent
        self.CONFIG_DIR = self.ROOT_DIR / 'src' / 'config'
        self.DATA_DIR = self.ROOT_DIR / 'data'
        self.RAW_DATA_DIR = self.DATA_DIR / 'raw'
        self.PROCESSED_DATA_DIR = self.DATA_DIR / 'processed'
        
        # Create directories if they don't exist
        self.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load Neo4j configuration
        self.NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
        self.NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')
        
        # Load LER search configuration
        self.ler_search_config = self._load_ler_search_config()
    
    def _load_ler_search_config(self) -> Dict[str, Any]:
        """Load LER search configuration from YAML file"""
        config_path = self.CONFIG_DIR / 'ler_search_config.yaml'
        try:
            # Explicitly specify UTF-8 encoding
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Error loading LER search config: {str(e)}")
            raise
    
    @property
    def ler_iframe_id(self) -> str:
        """Get iframe ID for LER search page"""
        return self.ler_search_config['iframe']['id']
    
    @property
    def ler_iframe_wait_time(self) -> int:
        """Get iframe wait time in seconds"""
        return self.ler_search_config['iframe']['wait_time']
    
    @property
    def ler_form_ids(self) -> Dict[str, str]:
        """Get form IDs and references"""
        return self.ler_search_config['form_references']
    
    @property
    def ler_date_range(self) -> Dict[str, Dict[str, str]]:
        """Get LER search date range settings"""
        return self.ler_search_config['date_range']
    
    @property
    def ler_reactor_types(self) -> Dict[str, bool]:
        """Get reactor type settings"""
        return self.ler_search_config['reactor_types']
    
    @property
    def ler_vendors(self) -> Dict[str, bool]:
        """Get vendor settings"""
        return self.ler_search_config['vendors']
    
    @property
    def ler_nrc_regions(self) -> Dict[str, bool]:
        """Get NRC region settings"""
        return self.ler_search_config['nrc_regions']
    
    @property
    def ler_operating_modes(self) -> Dict[str, bool]:
        """Get operating mode settings"""
        return self.ler_search_config['operating_modes']
    
    @property
    def ler_search_options(self) -> Dict[str, Any]:
        """Get search options"""
        return self.ler_search_config['search_options']

# Create singleton instance
config = Config()