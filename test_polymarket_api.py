#!/usr/bin/env python3
"""
Simple Polymarket API Test
Tests the Polymarket API connection without requiring Google Sheets setup
"""

import sys
import logging
from datetime import datetime
from config import Config
from polymarket_client import PolymarketClient

def test_polymarket_api():
    """Test the Polymarket API connection and data fetching"""
    print("🔥 Testing Polymarket API Connection")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Initialize client
        print("\n📡 Initializing Polymarket client...")
        client = PolymarketClient()
        print(f"✅ Client initialized successfully")
        print(f"   Gamma API: {client.gamma_base_url}")
        print(f"   CLOB API: {client.clob_base_url}")
        
        # Test with configured slug
        slug = Config.POLYMARKET_EVENT_SLUG or Config.POLYMARKET_MARKET_SLUG
        if not slug:
            print("❌ No Polymarket slug configured in .env")
            return False
            
        print(f"\n🎯 Testing with slug: '{slug}'")
        
        # Test 1: Try to get event data
        print("\n1️⃣ Testing event lookup...")
        event_data = client.get_event_by_slug(slug)
        if event_data:
            print("✅ Successfully fetched event data")
            print(f"   Event ID: {event_data.get('id', 'N/A')}")
            print(f"   Slug: {event_data.get('slug', 'N/A')}")
            print(f"   Liquidity: ${event_data.get('liquidity', 0):,.2f}")
            print(f"   Volume: ${event_data.get('volume', 0):,.2f}")
        else:
            print("⚠️  Event not found, trying as market slug...")
        
        # Test 2: Try to get market data
        print("\n2️⃣ Testing market lookup...")
        market_data = client.get_market_by_slug(slug)
        if market_data:
            print("✅ Successfully fetched market data")
            print(f"   Question: {market_data.get('question', 'N/A')}")
            print(f"   Category: {market_data.get('category', 'N/A')}")
            print(f"   Active: {market_data.get('active', 'N/A')}")
            print(f"   Closed: {market_data.get('closed', 'N/A')}")
            print(f"   End Date: {market_data.get('end_date_iso', 'N/A')}")
            
            # Show token information
            if 'tokens' in market_data:
                print(f"   Tokens: {len(market_data['tokens'])} outcomes")
                for i, token in enumerate(market_data['tokens']):
                    outcome = token.get('outcome', f'Outcome {i+1}')
                    token_id = token.get('token_id', 'N/A')
                    print(f"     - {outcome} (Token ID: {token_id})")
        else:
            print("⚠️  Market not found with this slug")
        
        # Test 3: Try to get markets for event
        if event_data:
            print("\n3️⃣ Testing markets for event...")
            markets = client.get_markets_for_event(slug)
            if markets:
                print(f"✅ Found {len(markets)} markets for this event")
                for i, market in enumerate(markets[:3]):  # Show first 3
                    print(f"   {i+1}. {market.get('question', 'Unknown question')}")
                if len(markets) > 3:
                    print(f"   ... and {len(markets) - 3} more markets")
            else:
                print("⚠️  No markets found for this event")
        
        # Test 4: Get simplified price data (the main function used by the agent)
        print("\n4️⃣ Testing simplified price data (main agent function)...")
        price_data = client.get_simplified_price_data(slug)
        if price_data:
            print("✅ Successfully got simplified price data")
            print("📊 Data structure that would be written to Google Sheets:")
            print("-" * 40)
            for key, value in price_data.items():
                print(f"   {key}: {value}")
            print("-" * 40)
            print(f"   Total fields: {len(price_data)}")
        else:
            print("❌ Failed to get simplified price data")
            return False
        
        # Test 5: Try different popular market slugs if the current one doesn't work
        if not event_data and not market_data:
            print("\n5️⃣ Testing with popular market slugs...")
            test_slugs = [
                "trump-vs-harris-2024",
                "2024-presidential-election", 
                "will-trump-be-president-2025",
                "biden-democratic-nominee",
                "presidential-winner-2024"
            ]
            
            for test_slug in test_slugs:
                print(f"   Trying: {test_slug}")
                test_data = client.get_simplified_price_data(test_slug)
                if test_data:
                    print(f"   ✅ Found working market: {test_slug}")
                    print(f"   Market: {test_data.get('market_title', 'Unknown')}")
                    print(f"   Category: {test_data.get('category', 'Unknown')}")
                    break
            else:
                print("   ⚠️  None of the test slugs worked")
        
        print(f"\n🎉 Polymarket API test completed successfully!")
        print(f"✅ The agent would be able to fetch data every 10 minutes")
        print(f"✅ Data structure is ready for Google Sheets integration")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        print(f"   This might be due to:")
        print(f"   - Network connectivity issues")
        print(f"   - Invalid market slug")
        print(f"   - Polymarket API changes")
        return False

if __name__ == "__main__":
    try:
        success = test_polymarket_api()
        
        if success:
            print(f"\n🚀 Next steps:")
            print(f"   1. Set up Google Sheets credentials")
            print(f"   2. Update GOOGLE_SHEET_ID in .env")
            print(f"   3. Run 'python polymarket_agent.py' to start monitoring")
        else:
            print(f"\n🔧 Troubleshooting:")
            print(f"   1. Check your internet connection")
            print(f"   2. Try a different market slug")
            print(f"   3. Check Polymarket.com for active markets")
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)