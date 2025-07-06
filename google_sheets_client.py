import logging
from datetime import datetime
from typing import Dict, List, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config

class GoogleSheetsClient:
    """Client for interacting with Google Sheets API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service = None
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.sheet_name = Config.GOOGLE_SHEET_NAME
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account credentials"""
        try:
            # Define the scope for Google Sheets API
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Load service account credentials
            credentials = Credentials.from_service_account_file(
                Config.GOOGLE_CREDENTIALS_FILE, 
                scopes=scopes
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Successfully authenticated with Google Sheets API")
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Google Sheets API: {e}")
            raise
    
    def create_headers_if_needed(self, headers: List[str]) -> bool:
        """
        Create headers in the sheet if they don't exist
        
        Args:
            headers: List of header names
            
        Returns:
            True if headers were created or already exist, False otherwise
        """
        try:
            # Check if sheet exists and has headers
            existing_data = self.get_sheet_data(range_name=f"{self.sheet_name}!1:1")
            
            if not existing_data or not existing_data[0]:
                # No headers exist, create them
                self.logger.info("Creating headers in the sheet")
                return self.write_row_data([headers], range_name=f"{self.sheet_name}!A1")
            else:
                # Headers exist, check if they match
                existing_headers = existing_data[0]
                if set(existing_headers) != set(headers):
                    self.logger.warning("Existing headers don't match expected headers")
                    # You might want to update headers or handle this differently
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating headers: {e}")
            return False
    
    def get_sheet_data(self, range_name: str) -> Optional[List[List]]:
        """
        Get data from a specific range in the sheet
        
        Args:
            range_name: The range to read (e.g., "Sheet1!A1:C10")
            
        Returns:
            List of lists containing the data, or None if failed
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
            
        except HttpError as e:
            self.logger.error(f"Error reading sheet data: {e}")
            return None
    
    def write_row_data(self, data: List[List], range_name: str = None) -> bool:
        """
        Write row data to the sheet
        
        Args:
            data: List of lists where each inner list is a row
            range_name: Optional range to write to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not range_name:
                range_name = f"{self.sheet_name}!A:Z"
            
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.logger.info(f"Successfully wrote {len(data)} rows to sheet")
            return True
            
        except HttpError as e:
            self.logger.error(f"Error writing to sheet: {e}")
            return False
    
    def append_row_data(self, data: List[List]) -> bool:
        """
        Append row data to the end of the sheet
        
        Args:
            data: List of lists where each inner list is a row
            
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f"{self.sheet_name}!A:Z",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            self.logger.info(f"Successfully appended {len(data)} rows to sheet")
            return True
            
        except HttpError as e:
            self.logger.error(f"Error appending to sheet: {e}")
            return False
    
    def write_price_data(self, price_data: Dict) -> bool:
        """
        Write price data to the Google Sheet
        
        Args:
            price_data: Dictionary containing price data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare headers based on the price data keys
            headers = list(price_data.keys())
            
            # Create headers if needed
            if not self.create_headers_if_needed(headers):
                return False
            
            # Prepare the row data
            row_data = [list(price_data.values())]
            
            # Append the data
            return self.append_row_data(row_data)
            
        except Exception as e:
            self.logger.error(f"Error writing price data: {e}")
            return False
    
    def get_last_update_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last update from the sheet
        
        Returns:
            DateTime of last update or None if no data exists
        """
        try:
            # Assuming timestamp is in the first column
            data = self.get_sheet_data(f"{self.sheet_name}!A:A")
            
            if data and len(data) > 1:  # Skip header row
                last_timestamp_str = data[-1][0] if data[-1] else None
                if last_timestamp_str:
                    try:
                        return datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
                    except ValueError:
                        self.logger.warning(f"Could not parse timestamp: {last_timestamp_str}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting last update time: {e}")
            return None