import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

class GrowwScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def fetch_page_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Subphase 1.1: Data Extraction.
        Fetches the raw page HTML and extracts the embedded __NEXT_DATA__ JSON.
        This safely captures all the highly-structured factual mutual fund data.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            
            if not script_tag:
                print(f"Error: No __NEXT_DATA__ script tag found for {url}")
                return None
                
            data = json.loads(script_tag.string)
            # The mutual fund data is typically located deep in the props
            mf_data = data.get('props', {}).get('pageProps', {}).get('mfServerSideData', {})
            
            if not mf_data:
                print(f"Error: 'mfServerSideData' not found inside JSON for {url}")
                return None
                
            return mf_data
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = GrowwScraper()
    url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    data = scraper.fetch_page_json(url)
    
    if data:
        print(f"Successfully extracted {len(data)} data points for {data.get('scheme_name')}.")
        print("--- Extraction Samples ---")
        print(f"Scheme Name: {data.get('scheme_name')}")
        print(f"Expense Ratio: {data.get('expense_ratio')}")
        print(f"Min SIP Investment: {data.get('min_sip_investment')}")
        print(f"AUM: {data.get('aum')}")
    else:
        print("Extraction failed.")
