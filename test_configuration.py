#!/usr/bin/env python3
"""
Test script for Polymarket Price Monitoring Agent
This script helps verify that your configuration is working correctly.
"""

import sys
import logging
from config import Config
from polymarket_client import PolymarketClient
from google_sheets_client import GoogleSheetsClient

def test_configuration():
    """Test the agent configuration"""
    print("🧪 Testing Polymarket Agent Configuration")
    print("=" * 50)
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    success = True
    
    # Test 1: Configuration validation
    print("\n1️⃣ Testing configuration validation...")
    try:
        Config.validate_config()
        print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        success = False
    
    # Test 2: Polymarket API connection
    print("\n2️⃣ Testing Polymarket API connection...")
    try:
        client = PolymarketClient()
        
        # Determine which slug to use
        slug = Config.POLYMARKET_MARKET_SLUG or Config.POLYMARKET_EVENT_SLUG
        if not slug:
            print("❌ No Polymarket slug configured")
            success = False
        else:
            print(f"   Using slug: {slug}")
            
            # Try to fetch data
            data = client.get_simplified_price_data(slug)
            if data:
                print("✅ Successfully fetched Polymarket data")
                print(f"   Market: {data.get('market_title', 'Unknown')}")
                print(f"   Category: {data.get('category', 'Unknown')}")
                print(f"   Active: {data.get('active', 'Unknown')}")
                
                # Show available price fields
                price_fields = [k for k in data.keys() if k.endswith('_price') or k in ['Yes', 'No']]
                if price_fields:
                    print(f"   Price fields: {', '.join(price_fields)}")
                else:
                    print("   ⚠️  No price data available (this is normal for some markets)")
            else:
                print("❌ Failed to fetch Polymarket data")
                success = False
                
    except Exception as e:
        print(f"❌ Polymarket API test failed: {e}")
        success = False
    
    # Test 3: Google Sheets connection
    print("\n3️⃣ Testing Google Sheets connection...")
    try:
        sheets_client = GoogleSheetsClient()
        
        # Try to read existing data
        data = sheets_client.get_sheet_data(f"{Config.GOOGLE_SHEET_NAME}!A1:A1")
        print("✅ Successfully connected to Google Sheets")
        
        if data:
            print(f"   Sheet has existing data (first cell: {data[0][0] if data[0] else 'empty'})")
        else:
            print("   Sheet appears to be empty (this is normal for a new sheet)")
            
    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
        success = False
    
    # Test 4: End-to-end test
    print("\n4️⃣ Testing end-to-end data flow...")
    if success:
        try:
            # Fetch data from Polymarket
            slug = Config.POLYMARKET_MARKET_SLUG or Config.POLYMARKET_EVENT_SLUG
            price_data = client.get_simplified_price_data(slug)
            
            if price_data:
                # Try to write to Google Sheets (but don't actually write)
                print("✅ End-to-end test would succeed")
                print("   Data structure looks good for Google Sheets")
                
                # Show what would be written
                print("   Sample data that would be written:")
                for key, value in list(price_data.items())[:5]:  # Show first 5 items
                    print(f"      {key}: {value}")
                if len(price_data) > 5:
                    print(f"      ... and {len(price_data) - 5} more fields")
            else:
                print("❌ End-to-end test failed: no data to write")
                success = False
                
        except Exception as e:
            print(f"❌ End-to-end test failed: {e}")
            success = False
    else:
        print("⏭️  Skipping end-to-end test due to previous failures")
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your configuration is ready.")
        print("\nNext steps:")
        print("- Run 'python polymarket_agent.py' to start monitoring")
        print("- Check the log file for detailed output")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("- Verify your .env file configuration")
        print("- Check your Google credentials file")
        print("- Ensure your Polymarket slug is correct")
        print("- See README_POLYMARKET_AGENT.md for detailed setup instructions")
    
    return success

if __name__ == "__main__":
    try:
        success = test_configuration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        sys.exit(1)