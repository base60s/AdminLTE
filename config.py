import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Polymarket Price Agent"""
    
    # Google Sheets Configuration
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'Polymarket Prices')
    
    # Polymarket Configuration
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
        
        if not cls.GOOGLE_SHEET_ID:
            missing_configs.append('GOOGLE_SHEET_ID')
        
        if not cls.POLYMARKET_EVENT_SLUG and not cls.POLYMARKET_MARKET_SLUG:
            missing_configs.append('POLYMARKET_EVENT_SLUG or POLYMARKET_MARKET_SLUG')
        
        if not os.path.exists(cls.GOOGLE_CREDENTIALS_FILE):
            missing_configs.append(f'Google credentials file: {cls.GOOGLE_CREDENTIALS_FILE}')
        
        if missing_configs:
            raise ValueError(f"Missing required configuration: {', '.join(missing_configs)}")
        
        return True