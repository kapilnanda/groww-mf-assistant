import os
import json
from pathlib import Path

def clean_data():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    raw_data_dir = project_root / "data" / "raw"
    cleaned_data_dir = project_root / "data" / "cleaned"
    cleaned_data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Starting Subphase 1.2: Data Cleaning")
    
    for file_path in raw_data_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Extract only facts, excluding subjective text
        scheme_name = data.get('scheme_name', 'Unknown Scheme')
        nav_date = data.get('nav_date', 'Unknown Date')
        
        # Build clean factual sections
        sections = {
            "Core Details": {
                "Fund Name": scheme_name,
                "Fund House": data.get('fund_house', 'N/A'),
                "Fund Manager": data.get('fund_manager', 'N/A'),
                "Category": f"{data.get('category', '')} - {data.get('sub_category', '')}".strip(" -"),
                "Benchmark": data.get('benchmark_name', 'N/A'),
                "AUM (Assets Under Management)": f"₹{data.get('aum', 'N/A')} Crores",
                "Latest NAV": f"₹{data.get('nav', 'N/A')} (As of {nav_date})"
            },
            "Fees and Constraints": {
                "Expense Ratio": f"{data.get('expense_ratio', 'N/A')}%",
                "Exit Load": data.get('exit_load', 'N/A').replace('\n', ' '),
                "Lock-in Period": data.get('lock_in', 'No Lock-in'),
                "Minimum SIP Investment": f"₹{data.get('min_sip_investment', 'N/A')}",
                "Minimum Lumpsum Investment": f"₹{data.get('min_investment_amount', 'N/A')}"
            }
        }

        # Extract Returns
        for stat in data.get('stats', []):
            if stat.get('type') == 'FUND_RETURN':
                sections["Return Statistics"] = {
                    "1Y Return": f"{stat.get('stat_1y', 'N/A')}%",
                    "3Y Return": f"{stat.get('stat_3y', 'N/A')}%",
                    "5Y Return": f"{stat.get('stat_5y', 'N/A')}%",
                    "All Time Return": f"{stat.get('stat_all', 'N/A')}%"
                }
                break

        # Extract Holdings (Top 10)
        holdings = data.get('holdings', [])
        if holdings:
            sections["Top Holdings"] = {
                item.get('company_name'): f"{item.get('corpus_per')}%" 
                for item in holdings[:10]
            }
        
        cleaned_doc = {
            "scheme_code": data.get('scheme_code', file_path.stem),
            "source_url": f"https://groww.in/mutual-funds/{data.get('search_id', '')}",
            "last_updated": nav_date,
            "sections": sections
        }
        
        out_path = cleaned_data_dir / file_path.name
        with open(out_path, "w", encoding="utf-8") as out_f:
            json.dump(cleaned_doc, out_f, indent=4, ensure_ascii=False)
            
        print(f"  -> Cleaned {scheme_name}")

if __name__ == "__main__":
    clean_data()
