import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class MarkdownWriter:
    """Client for writing market data to markdown files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_path = Config.MARKDOWN_FILE_PATH
        self.max_entries = Config.MAX_MARKDOWN_ENTRIES
        
    def write_market_data(self, market_data: Dict) -> bool:
        """
        Write market data to markdown file
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Read existing content if file exists
            existing_content = self._read_existing_content()
            
            # Generate new entry
            new_entry = self._format_market_data(market_data)
            
            # Combine with existing content
            updated_content = self._combine_content(existing_content, new_entry)
            
            # Write to file
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.logger.info(f"Successfully wrote market data to {self.file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing market data to markdown: {e}")
            return False
    
    def _read_existing_content(self) -> str:
        """Read existing markdown content"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            self.logger.warning(f"Could not read existing content: {e}")
            return ""
    
    def _format_market_data(self, market_data: Dict) -> str:
        """Format market data as markdown"""
        try:
            timestamp = market_data.get('timestamp', datetime.now().isoformat())
            title = market_data.get('title', 'Unknown Market')
            url = market_data.get('url', 'No URL')
            description = market_data.get('description', 'No description')
            volume = market_data.get('volume', 'Unknown')
            liquidity = market_data.get('liquidity', 'Unknown')
            end_date = market_data.get('end_date', 'Unknown')
            status = market_data.get('status', 'Unknown')
            markets = market_data.get('markets', [])
            
            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                formatted_time = timestamp
            
            # Start building markdown
            markdown = f"""
## 📊 Market Update - {formatted_time}

### 🎯 Market Information
- **Title:** {title}
- **URL:** [{url}]({url})
- **Status:** {status}
- **End Date:** {end_date}
- **Volume:** {volume}
- **Liquidity:** {liquidity}

### 📝 Description
{description}

"""
            
            # Add markets and prices
            if markets:
                markdown += "### 💰 Market Prices\n\n"
                
                for i, market in enumerate(markets, 1):
                    question = market.get('question', f'Market {i}')
                    outcomes = market.get('outcomes', [])
                    
                    markdown += f"#### {question}\n\n"
                    
                    if outcomes:
                        markdown += "| Outcome | Price | Probability |\n"
                        markdown += "|---------|-------|-------------|\n"
                        
                        for outcome in outcomes:
                            name = outcome.get('name', 'Unknown')
                            price = outcome.get('price')
                            
                            if price is not None:
                                try:
                                    price_val = float(price)
                                    if price_val <= 1:  # Assume it's already a probability
                                        probability = f"{price_val:.1%}"
                                        price_display = f"${price_val:.2f}"
                                    else:  # Assume it's in cents
                                        probability = f"{price_val:.1f}%"
                                        price_display = f"{price_val}¢"
                                except:
                                    probability = "N/A"
                                    price_display = str(price)
                            else:
                                probability = "N/A"
                                price_display = "N/A"
                            
                            markdown += f"| {name} | {price_display} | {probability} |\n"
                        
                        markdown += "\n"
                    else:
                        markdown += "*No price data available*\n\n"
            else:
                markdown += "### ⚠️ No Market Data Found\n\n"
                markdown += "Could not extract market prices from the webpage.\n\n"
            
            markdown += "---\n\n"
            
            return markdown
            
        except Exception as e:
            self.logger.error(f"Error formatting market data: {e}")
            return f"\n## Error - {datetime.now().isoformat()}\nFailed to format market data: {e}\n\n---\n\n"
    
    def _combine_content(self, existing_content: str, new_entry: str) -> str:
        """Combine existing content with new entry"""
        try:
            # Create header if file is empty
            if not existing_content.strip():
                header = self._create_header()
                content = header + new_entry
            else:
                # Add new entry at the top (after header)
                lines = existing_content.split('\n')
                
                # Find where to insert (after the main header)
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('# ') and i == 0:
                        # Found main header, insert after any description
                        insert_index = i + 1
                        # Skip description lines
                        while (insert_index < len(lines) and 
                               not lines[insert_index].startswith('##') and
                               lines[insert_index].strip()):
                            insert_index += 1
                        break
                
                # Insert new entry
                lines.insert(insert_index, new_entry)
                content = '\n'.join(lines)
            
            # Limit number of entries if specified
            if self.max_entries > 0:
                content = self._limit_entries(content)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error combining content: {e}")
            return f"{existing_content}\n{new_entry}"
    
    def _create_header(self) -> str:
        """Create markdown file header"""
        return f"""# 🔥 Polymarket Price Monitor

*Automated monitoring of Polymarket prediction markets*

**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Update Interval:** {Config.UPDATE_INTERVAL_MINUTES} minutes

"""
    
    def _limit_entries(self, content: str) -> str:
        """Limit the number of entries in the file"""
        try:
            lines = content.split('\n')
            header_lines = []
            entry_starts = []
            
            # Find header and entry boundaries
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    header_lines.append(i)
                elif line.startswith('## 📊 Market Update'):
                    entry_starts.append(i)
            
            # If we have too many entries, keep only the most recent
            if len(entry_starts) > self.max_entries:
                # Find where to cut off
                cutoff_index = entry_starts[self.max_entries]
                
                # Keep everything before the cutoff
                kept_lines = lines[:cutoff_index]
                
                # Add a note about truncated entries
                kept_lines.append("---")
                kept_lines.append(f"*Older entries truncated (showing last {self.max_entries} updates)*")
                kept_lines.append("")
                
                content = '\n'.join(kept_lines)
            
            return content
            
        except Exception as e:
            self.logger.warning(f"Error limiting entries: {e}")
            return content
    
    def get_last_update_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last update
        
        Returns:
            DateTime of last update or None if no data exists
        """
        try:
            if not os.path.exists(self.file_path):
                return None
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for the most recent timestamp
            import re
            pattern = r'## 📊 Market Update - (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC)'
            matches = re.findall(pattern, content)
            
            if matches:
                # Parse the most recent timestamp
                time_str = matches[0]
                return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S UTC')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting last update time: {e}")
            return None
    
    def get_file_stats(self) -> Dict:
        """Get statistics about the markdown file"""
        try:
            if not os.path.exists(self.file_path):
                return {
                    'exists': False,
                    'size': 0,
                    'entries': 0,
                    'last_update': None
                }
            
            # Get file size
            file_size = os.path.getsize(self.file_path)
            
            # Count entries
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            entries = len(re.findall(r'## 📊 Market Update', content))
            
            return {
                'exists': True,
                'size': file_size,
                'entries': entries,
                'last_update': self.get_last_update_time(),
                'path': self.file_path
            }
            
        except Exception as e:
            self.logger.error(f"Error getting file stats: {e}")
            return {
                'exists': False,
                'error': str(e)
            }