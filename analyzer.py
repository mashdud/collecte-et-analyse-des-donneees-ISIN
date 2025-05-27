import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List


class FinancialAnalyzer:
    """Calculer les indicateurs de performance financière."""
    
    def calculate_performance(self, prices: pd.Series) -> float:
        
        if len(prices) < 2:
            return 0.0
        
        start_price = prices.iloc[0]
        end_price = prices.iloc[-1]
        
        return ((end_price / start_price) - 1) * 100
    
    def calculate_volatility(self, prices: pd.Series, annualize: bool = True) -> float:
        
        if len(prices) < 2:
            return 0.0
        
        returns = prices.pct_change().dropna()
        vol = returns.std()
        
        if annualize:
            # Annualisation sur la base de 252 jours de bourse par an
            vol = vol * np.sqrt(252)
        
        return vol * 100
    
    def calculate_expected_return(self, prices: pd.Series, annualize: bool = True) -> float:
       
        if len(prices) < 2:
            return 0.0
        
        returns = prices.pct_change().dropna()
        mean_return = returns.mean()
        
        if annualize:
            
            mean_return = mean_return * 252
        
        return mean_return * 100
    
    def calculate_max_drawdown(self, prices: pd.Series) -> float:
        
        if len(prices) < 2:
            return 0.0
        
        
        returns = prices.pct_change().fillna(0)
        cumulative = (1 + returns).cumprod()
        
        
        running_max = cumulative.expanding().max()
        
        
        drawdown = (cumulative / running_max) - 1
        
        
        return abs(drawdown.min()) * 100
    
    def calculate_metrics_for_period(self, df: pd.DataFrame, period_name: str) -> Dict:
        
        if df.empty or len(df) < 2:
            return {
                'Period': period_name,
                'Performance (%)': 0.0,
                'Volatility (%)': 0.0,
                'Expected Return (%)': 0.0,
                'Max Drawdown (%)': 0.0,
                'Data Points': 0,
                'Start Date': 'N/A',
                'End Date': 'N/A'
            }
        
        prices = df['price']
        
        return {
            'Period': period_name,
            'Performance (%)': round(self.calculate_performance(prices), 2),
            'Volatility (%)': round(self.calculate_volatility(prices), 2),
            'Expected Return (%)': round(self.calculate_expected_return(prices), 2),
            'Max Drawdown (%)': round(self.calculate_max_drawdown(prices), 2),
            'Data Points': len(df),
            'Start Date': df['date'].min().strftime('%Y-%m-%d'),
            'End Date': df['date'].max().strftime('%Y-%m-%d')
        }
    
    def analyze_all_periods(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        
        results = []
        
        # Define the order of periods for consistent output
        period_order = ['YTD', '3M', '6M', '1Y', '3Y']
        
        for period in period_order:
            if period in data:
                df = data[period]
                metrics = self.calculate_metrics_for_period(df, period)
                results.append(metrics)
        
        return pd.DataFrame(results)
    
    def export_results(self, results_df: pd.DataFrame, format_type: str = 'console', filename: str = None):
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_metrics_{timestamp}"
        
        if format_type == 'csv':
            filepath = f"{filename}.csv"
            results_df.to_csv(filepath, index=False)
            print(f"Results exported to {filepath}")
            
        elif format_type == 'json':
            filepath = f"{filename}.json"
            results_df.to_json(filepath, orient='records', indent=2)
            print(f"Results exported to {filepath}")
            
        elif format_type == 'console':
            print("\n" + "="*80)
            print("FINANCIAL PERFORMANCE METRICS")
            print("="*80)
            print(results_df.to_string(index=False))
            print("="*80)
        
        else:
            print(f"Unsupported format: {format_type}")
    
    def get_summary_stats(self, results_df: pd.DataFrame) -> Dict:
        
        valid_results = results_df[results_df['Data Points'] > 0]
        
        if valid_results.empty:
            return {'message': 'No valid data for analysis'}
        
        return {
            'periods_analyzed': len(valid_results),
            'best_performance': {
                'period': valid_results.loc[valid_results['Performance (%)'].idxmax(), 'Period'],
                'value': valid_results['Performance (%)'].max()
            },
            'highest_volatility': {
                'period': valid_results.loc[valid_results['Volatility (%)'].idxmax(), 'Period'],
                'value': valid_results['Volatility (%)'].max()
            },
            'max_drawdown': {
                'period': valid_results.loc[valid_results['Max Drawdown (%)'].idxmax(), 'Period'],
                'value': valid_results['Max Drawdown (%)'].max()
            }
        }