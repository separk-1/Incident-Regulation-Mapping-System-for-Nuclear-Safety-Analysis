"""
Data collection module for the Knowledge Graph-based Incident-Regulation Mapping System.
This module contains crawlers for collecting Licensee Event Reports (LER) and NRC Regulations.
"""

from .ler_crawler import LERCrawler
from .regulation_crawler import NRCRegulationCrawler

__all__ = [
    'LERCrawler',
    'NRCRegulationCrawler',
]

# Version of the data module
__version__ = '0.1.0'

# Define common paths and configurations that might be used across crawlers
DEFAULT_RAW_DATA_PATH = 'data/raw'
DEFAULT_LER_PATH = f'{DEFAULT_RAW_DATA_PATH}/ler'
DEFAULT_REGULATIONS_PATH = f'{DEFAULT_RAW_DATA_PATH}/regulations'

# Define common utility functions if needed
def get_data_path(data_type: str) -> str:
    """
    Get the appropriate data path based on data type.
    
    Args:
        data_type (str): Type of data ('ler' or 'regulations')
    
    Returns:
        str: Path to the data directory
    
    Raises:
        ValueError: If data_type is not recognized
    """
    if data_type.lower() == 'ler':
        return DEFAULT_LER_PATH
    elif data_type.lower() == 'regulations':
        return DEFAULT_REGULATIONS_PATH
    else:
        raise ValueError(f"Unknown data type: {data_type}")