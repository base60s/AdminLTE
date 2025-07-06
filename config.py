import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Polymarket Price Agent"""
    
    # Markdown Output Configuration
    MARKDOWN_FILE_PATH = os.getenv('MARKDOWN_FILE_PATH', './data/polymarket_monitor.md')
    MAX_MARKDOWN_ENTRIES = int(os.getenv('MAX_MARKDOWN_ENTRIES', 50))
    
    # Polymarket Configuration
    POLYMARKET_URL = os.getenv('POLYMARKET_URL')
    
    # Legacy API configuration (not used in web scraping mode)
    POLYMARKET_EVENT_SLUG = os.getenv('POLYMARKET_EVENT_SLUG')
    POLYMARKET_MARKET_SLUG = os.getenv('POLYMARKET_MARKET_SLUG')
    POLYMARKET_GAMMA_API_BASE = 'https://gamma-api.polymarket.com'
    POLYMARKET_CLOB_API_BASE = 'https://clob.polymarket.com'
    
    # Agent Configuration
    UPDATE_INTERVAL_MINUTES = int(os.getenv('UPDATE_INTERVAL_MINUTES', 10))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'polymarket_agent.log')
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        missing_configs = []
        
        if not cls.POLYMARKET_URL:
            missing_configs.append('POLYMARKET_URL')
        
        # Validate that the markdown file path directory can be created
        try:
            os.makedirs(os.path.dirname(cls.MARKDOWN_FILE_PATH), exist_ok=True)
        except Exception as e:
            missing_configs.append(f'Cannot create markdown file directory: {e}')
        
        if missing_configs:
            raise ValueError(f"Missing required configuration: {', '.join(missing_configs)}")
        
        return True