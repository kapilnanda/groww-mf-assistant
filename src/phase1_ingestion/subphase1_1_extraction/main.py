import os
import json
import sys
from pathlib import Path

# Add the project root to sys.path so we can import config
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from config.settings import GROWW_HDFC_URLS
from src.phase1_ingestion.subphase1_1_extraction.scraper import GrowwScraper

def run_extraction():
    print("Starting Subphase 1.1: Data Extraction")
    scraper = GrowwScraper()
    
    # Create the raw data directory
    raw_data_dir = project_root / "data" / "raw"
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for url in GROWW_HDFC_URLS:
        print(f"Extracting data from: {url}")
        data = scraper.fetch_page_json(url)
        
        if data:
            scheme_code = data.get('scheme_code') or url.split('/')[-1]
            file_path = raw_data_dir / f"{scheme_code}.json"
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            print(f"  -> Successfully saved data to {file_path}")
            success_count += 1
        else:
            print(f"  -> Failed to extract data from {url}")
            
    print(f"Extraction complete. Successfully extracted {success_count}/{len(GROWW_HDFC_URLS)} URLs.")

if __name__ == "__main__":
    run_extraction()
