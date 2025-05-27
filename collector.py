import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class DataCollector:
    """Collecte de données financières à partir de diverses API."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
            "Referer": "https://www.justetf.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
    
    def fetch_da(self, url: str, retries: int = 3, timeout: int = 15) -> Optional[Dict]:
       
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Failed to fetch data after {retries} attempts")
                    return None
    
    def get_period_dates(self) -> Dict[str, Tuple[datetime, datetime]]:
        
        end_date = datetime.now()
        start_of_year = datetime(end_date.year, 1, 1)
        
        return {
            "YTD": (start_of_year, end_date),
            "3M": (end_date - timedelta(days=90), end_date),
            "6M": (end_date - timedelta(days=180), end_date),
            "1Y": (end_date - timedelta(days=365), end_date),
            "3Y": (end_date - timedelta(days=1095), end_date)
        }
    
    def parse_justetf_data(self, raw_data: Dict) -> pd.DataFrame:
       
       
        if not raw_data or 'series' not in raw_data:
            print("No  data found in response")
            return pd.DataFrame()
        
        # Obtenir le prix de base à partir de la réponse
        base_price = 100.0  
        if 'price' in raw_data and isinstance(raw_data['price'], dict) and 'raw' in raw_data['price']:
            base_price = raw_data['price']['raw']
        elif 'latestQuote' in raw_data and isinstance(raw_data['latestQuote'], dict) and 'raw' in raw_data['latestQuote']:
            base_price = raw_data['latestQuote']['raw']
        
        # Convertir les changements de pourcentage en prix absolus
        data = []
        for item in raw_data['series']:
            if 'date' in item and 'value' in item:
                
                if isinstance(item['value'], dict) and 'raw' in item['value']:
                    pct_change = item['value']['raw']
                elif isinstance(item['value'], (int, float)):
                    pct_change = item['value']
                else:
                    pct_change = 0.0
                
                # Calculate absolute price from percentage change
                price = base_price * (1 + pct_change / 100.0)
                
                data.append({
                    'date': pd.to_datetime(item['date']),
                    'price': price,
                    'pct_change': pct_change
                })
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        return df.sort_values('date').reset_index(drop=True)
    
    def collect_justetf_data(self, instrument_id: str) -> Dict[str, pd.DataFrame]:
        
        periods = self.get_period_dates()
        results = {}
        
        print(f"Collecting data for instrument: {instrument_id}")
        
        for period_name, (start_date, end_date) in periods.items():
            url = self._build_justetf_url(instrument_id, start_date, end_date)
            
            print(f"Fetching {period_name} data ({start_date.date()} to {end_date.date()})...")
            raw_data = self.fetch_da(url)
            
            if raw_data:
                df = self.parse_justetf_data(raw_data)
                if not df.empty:
                    results[period_name] = df
                    print(f"✓ {period_name}: {len(df)} data points, price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
                else:
                    print(f"✗ {period_name}: Failed to parse data")
                    results[period_name] = pd.DataFrame()
            else:
                print(f"✗ {period_name}: Failed to fetch data")
                results[period_name] = pd.DataFrame()
        
        return results
    
    def _build_justetf_url(self, instrument_id: str, start_date: datetime, end_date: datetime) -> str:
      
        return (
            f"https://www.justetf.com/api/etfs/{instrument_id}/performance-chart"
            f"?locale=fr&currency=EUR&valuesType=RELATIVE_CHANGE&reduceData=false"
            f"&includeDividends=true&features=DIVIDENDS"
            f"&dateFrom={start_date.strftime('%Y-%m-%d')}"
            f"&dateTo={end_date.strftime('%Y-%m-%d')}"
        )
    
    def get_availaable_periods(self, data: Dict[str, pd.DataFrame]) -> list:
        
        return [period for period, df in data.items() if not df.empty]