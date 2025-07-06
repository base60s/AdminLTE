#!/usr/bin/env python3
"""
Test script for Polymarket Web Scraping Agent
This script tests the web scraping functionality with the provided URL
"""

import sys
import logging
from datetime import datetime
from config import Config
from web_scraper_client import PolymarketWebScraper
from markdown_writer import MarkdownWriter

def test_web_scraper():
    """Test the web scraping functionality"""
    print("🕸️  Testing Polymarket Web Scraper")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Test configuration
        print("\n1️⃣ Testing configuration...")
        try:
            Config.validate_config()
            print("✅ Configuration is valid")
            print(f"   URL: {Config.POLYMARKET_URL}")
            print(f"   Output: {Config.MARKDOWN_FILE_PATH}")
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            return False
        
        # Test web scraper initialization
        print("\n2️⃣ Initializing web scraper...")
        scraper = PolymarketWebScraper()
        print("✅ Web scraper initialized successfully")
        
        # Test markdown writer initialization
        print("\n3️⃣ Initializing markdown writer...")
        writer = MarkdownWriter()
        print("✅ Markdown writer initialized successfully")
        
        # Test web scraping
        print("\n4️⃣ Testing web scraping...")
        print(f"   Scraping: {Config.POLYMARKET_URL}")
        market_data = scraper.extract_market_data(Config.POLYMARKET_URL)
        
        if not market_data:
            print("❌ Failed to scrape market data")
            return False
        
        print("✅ Successfully scraped market data!")
        print("\n📊 Extracted Data:")
        print("-" * 30)
        print(f"   Title: {market_data.get('title', 'N/A')}")
        print(f"   Description: {market_data.get('description', 'N/A')[:100]}...")
        print(f"   Volume: {market_data.get('volume', 'N/A')}")
        print(f"   Liquidity: {market_data.get('liquidity', 'N/A')}")
        print(f"   Status: {market_data.get('status', 'N/A')}")
        print(f"   End Date: {market_data.get('end_date', 'N/A')}")
        
        # Show markets/outcomes
        markets = market_data.get('markets', [])
        print(f"   Markets Found: {len(markets)}")
        
        for i, market in enumerate(markets[:3], 1):  # Show first 3
            question = market.get('question', f'Market {i}')
            outcomes = market.get('outcomes', [])
            print(f"     {i}. {question}")
            print(f"        Outcomes: {len(outcomes)}")
            
            for outcome in outcomes[:3]:  # Show first 3 outcomes
                name = outcome.get('name', 'Unknown')
                price = outcome.get('price', 'N/A')
                print(f"          - {name}: {price}")
        
        # Test markdown writing
        print("\n5️⃣ Testing markdown writing...")
        success = writer.write_market_data(market_data)
        
        if not success:
            print("❌ Failed to write markdown data")
            return False
        
        print("✅ Successfully wrote data to markdown!")
        
        # Show file stats
        stats = writer.get_file_stats()
        print(f"   File: {stats.get('path', 'Unknown')}")
        print(f"   Size: {stats.get('size', 0)} bytes")
        print(f"   Entries: {stats.get('entries', 0)}")
        print(f"   Last Update: {stats.get('last_update', 'None')}")
        
        # Test end-to-end with agent
        print("\n6️⃣ Testing full agent workflow...")
        from polymarket_agent import PolymarketPriceAgent
        
        agent = PolymarketPriceAgent()
        result = agent.run_single_update()
        
        if result:
            print("✅ Full agent workflow successful!")
            
            # Show final file content preview
            try:
                with open(Config.MARKDOWN_FILE_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    preview_lines = lines[:20]  # Show first 20 lines
                    
                print("\n📄 Markdown File Preview (first 20 lines):")
                print("-" * 40)
                for line in preview_lines:
                    print(line)
                if len(lines) > 20:
                    print(f"... and {len(lines) - 20} more lines")
                    
            except Exception as e:
                print(f"⚠️  Could not read file for preview: {e}")
        else:
            print("❌ Full agent workflow failed")
            return False
        
        print(f"\n🎉 All tests passed successfully!")
        print(f"✅ Web scraping is working correctly")
        print(f"✅ Markdown writing is working correctly")
        print(f"✅ Full agent workflow is operational")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_web_scraper()
        
        if success:
            print(f"\n🚀 Next steps:")
            print(f"   1. Check the generated markdown file: {Config.MARKDOWN_FILE_PATH}")
            print(f"   2. Run 'python polymarket_agent.py' to start continuous monitoring")
            print(f"   3. The agent will update the file every {Config.UPDATE_INTERVAL_MINUTES} minutes")
        else:
            print(f"\n🔧 Troubleshooting:")
            print(f"   1. Check your internet connection")
            print(f"   2. Verify the Polymarket URL is accessible")
            print(f"   3. Check file permissions for the output directory")
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)