import logging
import schedule
import time
from datetime import datetime
from config import Config
from web_scraper_client import PolymarketWebScraper
from markdown_writer import MarkdownWriter

class PolymarketPriceAgent:
    """Main agent class for monitoring Polymarket prices and writing to markdown files"""
    
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
        self.polymarket_scraper = PolymarketWebScraper()
        self.markdown_writer = MarkdownWriter()
        
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
        """Fetch current price data and update markdown file"""
        try:
            self.logger.info("Starting price data update...")
            
            # Get the URL to scrape
            url = Config.POLYMARKET_URL
            if not url:
                self.logger.error("No Polymarket URL configured")
                return False
            
            # Scrape price data from Polymarket webpage
            market_data = self.polymarket_scraper.extract_market_data(url)
            
            if not market_data:
                self.logger.error("Failed to scrape price data from Polymarket")
                return False
            
            self.logger.info(f"Scraped market data: {market_data.get('title', 'Unknown')}")
            
            # Write data to markdown file
            success = self.markdown_writer.write_market_data(market_data)
            
            if success:
                self.logger.info("Successfully updated markdown file with price data")
                return True
            else:
                self.logger.error("Failed to update markdown file")
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
        self.logger.info(f"Target URL: {Config.POLYMARKET_URL}")
        self.logger.info(f"Output file: {Config.MARKDOWN_FILE_PATH}")
        
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
            # Check last update time from markdown file
            last_update = self.markdown_writer.get_last_update_time()
            file_stats = self.markdown_writer.get_file_stats()
            
            status = {
                "agent_running": True,
                "last_update": last_update.isoformat() if last_update else None,
                "target_url": Config.POLYMARKET_URL,
                "output_file": Config.MARKDOWN_FILE_PATH,
                "update_interval_minutes": Config.UPDATE_INTERVAL_MINUTES,
                "file_stats": file_stats
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