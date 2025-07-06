import logging
import schedule
import time
from datetime import datetime
from config import Config
from polymarket_client import PolymarketClient
from google_sheets_client import GoogleSheetsClient

class PolymarketPriceAgent:
    """Main agent class for monitoring Polymarket prices and updating Google Sheets"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        try:
            Config.validate_config()
            self.logger.info("Configuration validated successfully")
        except ValueError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
        
        # Initialize clients
        self.polymarket_client = PolymarketClient()
        self.google_sheets_client = GoogleSheetsClient()
        
        self.logger.info("Polymarket Price Agent initialized successfully")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def update_price_data(self):
        """Fetch current price data and update Google Sheets"""
        try:
            self.logger.info("Starting price data update...")
            
            # Fetch price data from Polymarket
            # Use market slug if available, otherwise use event slug
            slug = Config.POLYMARKET_MARKET_SLUG or Config.POLYMARKET_EVENT_SLUG
            price_data = self.polymarket_client.get_simplified_price_data(slug)
            
            if not price_data:
                self.logger.error("Failed to fetch price data from Polymarket")
                return False
            
            self.logger.info(f"Fetched price data: {price_data}")
            
            # Write data to Google Sheets
            success = self.google_sheets_client.write_price_data(price_data)
            
            if success:
                self.logger.info("Successfully updated Google Sheets with price data")
                return True
            else:
                self.logger.error("Failed to update Google Sheets")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during price data update: {e}")
            return False
    
    def run_scheduled_update(self):
        """Run a single scheduled update with error handling"""
        try:
            self.logger.info("Running scheduled price update...")
            start_time = datetime.now()
            
            success = self.update_price_data()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                self.logger.info(f"Scheduled update completed successfully in {duration:.2f} seconds")
            else:
                self.logger.error(f"Scheduled update failed after {duration:.2f} seconds")
                
        except Exception as e:
            self.logger.error(f"Unexpected error during scheduled update: {e}")
    
    def start_monitoring(self):
        """Start the monitoring process with scheduled updates"""
        self.logger.info(f"Starting Polymarket price monitoring...")
        self.logger.info(f"Update interval: {Config.UPDATE_INTERVAL_MINUTES} minutes")
        slug = Config.POLYMARKET_MARKET_SLUG or Config.POLYMARKET_EVENT_SLUG
        self.logger.info(f"Market/Event Slug: {slug}")
        self.logger.info(f"Google Sheet ID: {Config.GOOGLE_SHEET_ID}")
        
        # Schedule the job
        schedule.every(Config.UPDATE_INTERVAL_MINUTES).minutes.do(self.run_scheduled_update)
        
        # Run an initial update
        self.logger.info("Running initial price update...")
        self.run_scheduled_update()
        
        # Start the scheduler loop
        self.logger.info("Scheduler started. Waiting for next update...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal. Stopping agent...")
        except Exception as e:
            self.logger.error(f"Unexpected error in scheduler loop: {e}")
            raise
    
    def run_single_update(self):
        """Run a single update without scheduling (useful for testing)"""
        self.logger.info("Running single price update...")
        return self.update_price_data()
    
    def get_status(self):
        """Get current status of the agent"""
        try:
            # Check last update time from Google Sheets
            last_update = self.google_sheets_client.get_last_update_time()
            
            slug = Config.POLYMARKET_MARKET_SLUG or Config.POLYMARKET_EVENT_SLUG
            status = {
                "agent_running": True,
                "last_update": last_update.isoformat() if last_update else None,
                "market_slug": Config.POLYMARKET_MARKET_SLUG,
                "event_slug": Config.POLYMARKET_EVENT_SLUG,
                "current_slug": slug,
                "update_interval_minutes": Config.UPDATE_INTERVAL_MINUTES
            }
            
            self.logger.info(f"Agent status: {status}")
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return {"agent_running": False, "error": str(e)}


def main():
    """Main function to run the agent"""
    try:
        agent = PolymarketPriceAgent()
        
        # You can uncomment one of these options:
        
        # Option 1: Run continuous monitoring (recommended for production)
        agent.start_monitoring()
        
        # Option 2: Run a single update (useful for testing)
        # agent.run_single_update()
        
        # Option 3: Get status
        # status = agent.get_status()
        # print(f"Agent Status: {status}")
        
    except Exception as e:
        logging.error(f"Failed to start agent: {e}")
        raise


if __name__ == "__main__":
    main()