#!/usr/bin/env python3
"""
Quick script to explore available Polymarket markets
"""

import requests
import json

def explore_markets():
    """Explore what markets are available"""
    print("🔍 Exploring Polymarket Markets")
    print("=" * 40)
    
    try:
        # Get recent markets
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            "limit": 10,
            "active": True,
            "closed": False
        }
        
        print(f"🌐 Fetching from: {url}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        markets = response.json()
        print(f"✅ Found {len(markets)} markets")
        
        print("\n📊 Available Active Markets:")
        print("-" * 40)
        
        for i, market in enumerate(markets[:5], 1):
            title = market.get('question', 'Unknown')
            slug = market.get('market_slug', market.get('slug', 'No slug'))
            category = market.get('category', 'Unknown')
            active = market.get('active', False)
            closed = market.get('closed', True)
            
            print(f"{i}. {title}")
            print(f"   Slug: {slug}")
            print(f"   Category: {category}")
            print(f"   Active: {active}, Closed: {closed}")
            print()
            
            # Show this market's token structure if available
            if 'tokens' in market:
                tokens = market['tokens']
                print(f"   Outcomes ({len(tokens)} tokens):")
                for token in tokens:
                    outcome = token.get('outcome', 'Unknown')
                    token_id = token.get('token_id', 'N/A')
                    print(f"     - {outcome} (ID: {token_id})")
                print()
        
        # Try one of these markets with our agent
        if markets:
            test_market = markets[0]
            test_slug = test_market.get('market_slug', test_market.get('slug'))
            
            if test_slug:
                print(f"🧪 Testing our agent with market: {test_slug}")
                
                # Now test with our client
                from polymarket_client import PolymarketClient
                client = PolymarketClient()
                
                price_data = client.get_simplified_price_data(test_slug)
                if price_data:
                    print("✅ Agent successfully fetched data!")
                    print("📊 Sample data:")
                    for key, value in list(price_data.items())[:6]:
                        print(f"   {key}: {value}")
                else:
                    print("❌ Agent failed to fetch data")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_markets()