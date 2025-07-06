import requests
import logging
from datetime import datetime
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import re
import json
from config import Config

class PolymarketWebScraper:
    """Client for scraping Polymarket website data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
    def extract_market_data(self, url: str) -> Optional[Dict]:
        """
        Extract market data from Polymarket webpage
        
        Args:
            url: The Polymarket market/event URL
            
        Returns:
            Dictionary containing market data or None if failed
        """
        try:
            self.logger.info(f"Scraping market data from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic market information
            market_data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'markets': self._extract_markets(soup),
                'volume': self._extract_volume(soup),
                'liquidity': self._extract_liquidity(soup),
                'end_date': self._extract_end_date(soup),
                'status': self._extract_status(soup)
            }
            
            self.logger.info(f"Successfully extracted market data: {market_data['title']}")
            return market_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching webpage: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing market data: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the main title/question from the page"""
        try:
            # Try multiple selectors for title
            selectors = [
                'h1',
                '[data-testid="event-title"]',
                '.event-title',
                'title'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and len(title) > 5:  # Reasonable title length
                        return title
            
            # Fallback to page title
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text(strip=True)
                
            return "Unknown Market"
            
        except Exception as e:
            self.logger.warning(f"Could not extract title: {e}")
            return "Unknown Market"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract market description"""
        try:
            # Look for description in various places
            selectors = [
                '[data-testid="event-description"]',
                '.event-description',
                '.description',
                'meta[name="description"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        return element.get('content', '').strip()
                    else:
                        desc = element.get_text(strip=True)
                        if desc and len(desc) > 10:
                            return desc
            
            return "No description available"
            
        except Exception as e:
            self.logger.warning(f"Could not extract description: {e}")
            return "No description available"
    
    def _extract_markets(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract individual markets within the event"""
        try:
            markets = []
            
            # Look for market containers
            market_selectors = [
                '[data-testid*="market"]',
                '.market-card',
                '.market-item',
                '.outcome-card'
            ]
            
            for selector in market_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        market = self._parse_market_element(element)
                        if market:
                            markets.append(market)
                    break
            
            # If no structured markets found, look for price elements
            if not markets:
                markets = self._extract_prices_fallback(soup)
            
            return markets
            
        except Exception as e:
            self.logger.warning(f"Could not extract markets: {e}")
            return []
    
    def _parse_market_element(self, element) -> Optional[Dict]:
        """Parse individual market element"""
        try:
            market = {}
            
            # Extract question/title
            question_selectors = ['h2', 'h3', '.question', '.market-title']
            for selector in question_selectors:
                q_elem = element.select_one(selector)
                if q_elem:
                    market['question'] = q_elem.get_text(strip=True)
                    break
            
            # Extract outcomes and prices
            outcomes = []
            
            # Look for outcome buttons or cards
            outcome_selectors = [
                '.outcome-button',
                '.bet-button',
                '[data-testid*="outcome"]',
                '.price-button'
            ]
            
            for selector in outcome_selectors:
                outcome_elements = element.select(selector)
                if outcome_elements:
                    for outcome_elem in outcome_elements:
                        outcome = self._parse_outcome_element(outcome_elem)
                        if outcome:
                            outcomes.append(outcome)
                    break
            
            if outcomes:
                market['outcomes'] = outcomes
                return market
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error parsing market element: {e}")
            return None
    
    def _parse_outcome_element(self, element) -> Optional[Dict]:
        """Parse individual outcome element"""
        try:
            outcome = {}
            
            # Extract outcome name
            text = element.get_text(strip=True)
            
            # Try to extract price (look for percentage or decimal)
            price_match = re.search(r'(\d+(?:\.\d+)?)[¢%]?', text)
            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', text)
            
            if percentage_match:
                outcome['price'] = float(percentage_match.group(1)) / 100
                outcome['name'] = re.sub(r'\d+(?:\.\d+)?%', '', text).strip()
            elif price_match:
                price_val = float(price_match.group(1))
                # If it's cents (¢), convert to dollars
                if '¢' in text:
                    price_val = price_val / 100
                # If it's a large number, assume it's cents
                elif price_val > 100:
                    price_val = price_val / 100
                outcome['price'] = price_val
                outcome['name'] = re.sub(r'\d+(?:\.\d+)?[¢%]?', '', text).strip()
            
            # If no price found, try to extract just the name
            if 'name' not in outcome:
                outcome['name'] = text
                outcome['price'] = None
            
            return outcome if outcome.get('name') else None
            
        except Exception as e:
            self.logger.warning(f"Error parsing outcome: {e}")
            return None
    
    def _extract_prices_fallback(self, soup: BeautifulSoup) -> List[Dict]:
        """Fallback method to extract prices"""
        try:
            markets = []
            
            # Look for any elements containing prices
            price_elements = soup.find_all(text=re.compile(r'\d+[¢%]|\d+\.\d+'))
            
            if price_elements:
                market = {
                    'question': 'Market Prices',
                    'outcomes': []
                }
                
                for i, price_elem in enumerate(price_elements[:10]):  # Limit to 10
                    parent = price_elem.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        outcome = self._parse_outcome_element(parent)
                        if outcome:
                            market['outcomes'].append(outcome)
                
                if market['outcomes']:
                    markets.append(market)
            
            return markets
            
        except Exception as e:
            self.logger.warning(f"Error in fallback price extraction: {e}")
            return []
    
    def _extract_volume(self, soup: BeautifulSoup) -> str:
        """Extract trading volume"""
        try:
            # Look for volume indicators
            volume_patterns = [
                r'Volume[:\s]*\$?([\d,]+(?:\.\d+)?[KMB]?)',
                r'Total volume[:\s]*\$?([\d,]+(?:\.\d+)?[KMB]?)',
                r'\$?([\d,]+(?:\.\d+)?[KMB]?)\s*volume'
            ]
            
            page_text = soup.get_text()
            
            for pattern in volume_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return f"${match.group(1)}"
            
            return "Volume not found"
            
        except Exception as e:
            self.logger.warning(f"Could not extract volume: {e}")
            return "Volume not found"
    
    def _extract_liquidity(self, soup: BeautifulSoup) -> str:
        """Extract liquidity information"""
        try:
            # Look for liquidity indicators
            liquidity_patterns = [
                r'Liquidity[:\s]*\$?([\d,]+(?:\.\d+)?[KMB]?)',
                r'Total liquidity[:\s]*\$?([\d,]+(?:\.\d+)?[KMB]?)',
                r'\$?([\d,]+(?:\.\d+)?[KMB]?)\s*liquidity'
            ]
            
            page_text = soup.get_text()
            
            for pattern in liquidity_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return f"${match.group(1)}"
            
            return "Liquidity not found"
            
        except Exception as e:
            self.logger.warning(f"Could not extract liquidity: {e}")
            return "Liquidity not found"
    
    def _extract_end_date(self, soup: BeautifulSoup) -> str:
        """Extract market end date"""
        try:
            # Look for date patterns
            date_patterns = [
                r'Ends[:\s]*([\w\s,]+\d{4})',
                r'Closes[:\s]*([\w\s,]+\d{4})',
                r'End date[:\s]*([\w\s,]+\d{4})'
            ]
            
            page_text = soup.get_text()
            
            for pattern in date_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            return "End date not found"
            
        except Exception as e:
            self.logger.warning(f"Could not extract end date: {e}")
            return "End date not found"
    
    def _extract_status(self, soup: BeautifulSoup) -> str:
        """Extract market status"""
        try:
            page_text = soup.get_text().lower()
            
            if 'closed' in page_text or 'ended' in page_text:
                return "Closed"
            elif 'active' in page_text or 'live' in page_text:
                return "Active"
            else:
                return "Unknown"
                
        except Exception as e:
            self.logger.warning(f"Could not extract status: {e}")
            return "Unknown"