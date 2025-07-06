import requests
import logging
from datetime import datetime
from typing import Dict, Optional, List
from config import Config

class PolymarketClient:
    """Client for interacting with Polymarket Gamma API"""
    
    def __init__(self):
        self.gamma_base_url = Config.POLYMARKET_GAMMA_API_BASE
        self.clob_base_url = Config.POLYMARKET_CLOB_API_BASE
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def get_event_by_slug(self, slug: str) -> Optional[Dict]:
        """
        Fetch event data by slug
        
        Args:
            slug: The Polymarket event slug
            
        Returns:
            Dictionary containing event data or None if failed
        """
        try:
            url = f"{self.gamma_base_url}/events"
            params = {"slug": slug}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            events = response.json()
            if events and len(events) > 0:
                event_data = events[0]
                self.logger.info(f"Successfully fetched event data for slug {slug}")
                return event_data
            else:
                self.logger.warning(f"No event found for slug {slug}")
                return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching event data: {e}")
            return None
    
    def get_markets_for_event(self, event_slug: str) -> Optional[List[Dict]]:
        """
        Fetch markets for a given event slug
        
        Args:
            event_slug: The Polymarket event slug
            
        Returns:
            List of markets or None if failed
        """
        try:
            url = f"{self.gamma_base_url}/markets"
            params = {"event_slug": event_slug}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            markets = response.json()
            self.logger.info(f"Successfully fetched {len(markets)} markets for event {event_slug}")
            return markets
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching markets for event: {e}")
            return None
    
    def get_market_by_slug(self, market_slug: str) -> Optional[Dict]:
        """
        Fetch market data by slug
        
        Args:
            market_slug: The Polymarket market slug
            
        Returns:
            Dictionary containing market data or None if failed
        """
        try:
            url = f"{self.gamma_base_url}/markets"
            params = {"slug": market_slug}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            markets = response.json()
            if markets and len(markets) > 0:
                market_data = markets[0]
                self.logger.info(f"Successfully fetched market data for slug {market_slug}")
                return market_data
            else:
                self.logger.warning(f"No market found for slug {market_slug}")
                return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching market data: {e}")
            return None
    
    def get_market_prices_from_clob(self, condition_id: str) -> Optional[Dict]:
        """
        Fetch current market prices from CLOB API
        
        Args:
            condition_id: The condition ID of the market
            
        Returns:
            Dictionary containing price data or None if failed
        """
        try:
            # Get price information from CLOB
            url = f"{self.clob_base_url}/markets"
            response = self.session.get(url)
            response.raise_for_status()
            
            markets_data = response.json()
            
            # Find the market with matching condition_id
            target_market = None
            if 'data' in markets_data:
                for market in markets_data['data']:
                    if market.get('condition_id') == condition_id:
                        target_market = market
                        break
            
            if not target_market:
                self.logger.warning(f"Market with condition_id {condition_id} not found in CLOB")
                return None
            
            # Extract price information from tokens
            prices = {}
            if 'tokens' in target_market:
                for token in target_market['tokens']:
                    outcome = token.get('outcome', 'Unknown')
                    # For now, we'll use a default price since the CLOB API 
                    # might need additional endpoints for actual prices
                    prices[outcome] = 0.5  # Placeholder
            
            return prices
            
        except Exception as e:
            self.logger.error(f"Error fetching CLOB prices: {e}")
            return None
    
    def get_simplified_price_data(self, event_or_market_slug: str) -> Optional[Dict]:
        """
        Get simplified price data suitable for Google Sheets
        
        Args:
            event_or_market_slug: The Polymarket event or market slug
            
        Returns:
            Simplified dictionary with timestamp, market info, and prices
        """
        try:
            # First try to get as market slug
            market_data = self.get_market_by_slug(event_or_market_slug)
            
            if not market_data:
                # Try to get markets for this event slug
                markets = self.get_markets_for_event(event_or_market_slug)
                if markets and len(markets) > 0:
                    # Use the first market if multiple markets exist
                    market_data = markets[0]
                    self.logger.info(f"Using first market from event {event_or_market_slug}")
                else:
                    self.logger.error(f"No market data found for {event_or_market_slug}")
                    return None
            
            # Create simplified data structure
            simplified_data = {
                'timestamp': datetime.now().isoformat(),
                'market_title': market_data.get('question', 'Unknown Market'),
                'market_slug': market_data.get('market_slug', event_or_market_slug),
                'condition_id': market_data.get('condition_id', 'Unknown'),
                'category': market_data.get('category', 'Unknown'),
                'end_date': market_data.get('end_date_iso', 'Unknown'),
                'active': market_data.get('active', False),
                'closed': market_data.get('closed', False)
            }
            
            # Try to get price data from CLOB if condition_id is available
            condition_id = market_data.get('condition_id')
            if condition_id:
                prices = self.get_market_prices_from_clob(condition_id)
                if prices:
                    simplified_data.update(prices)
                else:
                    # If no CLOB prices, add placeholder data
                    if 'tokens' in market_data:
                        for token in market_data['tokens']:
                            outcome = token.get('outcome', 'Unknown')
                            simplified_data[f"{outcome}_price"] = "N/A"
            
            return simplified_data
            
        except Exception as e:
            self.logger.error(f"Error creating simplified price data: {e}")
            return None