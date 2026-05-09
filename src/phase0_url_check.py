import requests
import json

URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
]

results = {}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in URLS:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        results[url] = {
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
    except Exception as e:
        results[url] = {
            "status_code": "ERROR",
            "success": False,
            "error": str(e)
        }

print(json.dumps(results, indent=4))
