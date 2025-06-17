import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_ADS_API_KEY")

GOOGLE_ADS_URL = "https://googleads.googleapis.com/v14/customers/YOUR_CUSTOMER_ID/googleAds:search"

def fetch_google_ads_data():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    query = {"query": "SELECT campaign.id, campaign.name, metrics.clicks, metrics.conversions FROM campaign"}
    
    response = requests.post(GOOGLE_ADS_URL, headers=headers, json=query)
    return response.json()