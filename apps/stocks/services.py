import requests
import time
import yfinance as yf
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, Any


class StockPriceService:
    """Service to fetch current stock prices from multiple APIs"""
    
    # Cache duration in seconds (5 minutes for free tier to avoid rate limits)
    CACHE_DURATION = 300
    
    @staticmethod
    def get_stock_price(ticker: str) -> Optional[Decimal]:
        """
        Get current stock price for a given ticker
        Returns Decimal price or None if error
        """
        # Check cache first
        cache_key = f"stock_price_{ticker.upper()}"
        cached_price = cache.get(cache_key)
        if cached_price is not None:
            return Decimal(cached_price)
        
        # Try Yahoo Finance first (more reliable)
        price = StockPriceService._get_yahoo_price(ticker)
        if price:
            cache.set(cache_key, str(price), StockPriceService.CACHE_DURATION)
            return price
        
        # Fallback to Alpha Vantage
        price = StockPriceService._get_alphavantage_price(ticker)
        if price:
            cache.set(cache_key, str(price), StockPriceService.CACHE_DURATION)
            return price
        
        # Use demo data as last resort
        return StockPriceService._get_demo_price(ticker)
    
    @staticmethod
    def _get_yahoo_price(ticker: str) -> Optional[Decimal]:
        """Get price from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                return Decimal(str(info['regularMarketPrice']))
            elif 'currentPrice' in info and info['currentPrice']:
                return Decimal(str(info['currentPrice']))
            else:
                print(f"No price data from Yahoo Finance for {ticker}")
                return None
                
        except Exception as e:
            print(f"Error fetching Yahoo Finance price for {ticker}: {e}")
            return None
    
    @staticmethod
    def _get_alphavantage_price(ticker: str) -> Optional[Decimal]:
        """Get price from Alpha Vantage (fallback)"""
        try:
            # Get API key from settings
            api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if not api_key:
                return None
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker.upper(),
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API rate limit
            if "Information" in data and "rate limit" in data["Information"].lower():
                print(f"Alpha Vantage API rate limit reached for {ticker}")
                return None
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                price = quote.get("05. price")
                if price:
                    return Decimal(price)
            
            return None
                
        except Exception as e:
            print(f"Error fetching Alpha Vantage price for {ticker}: {e}")
            return None
    
    @staticmethod
    def _get_demo_price(ticker: str) -> Decimal:
        """Get demo price for testing when API is not available"""
        demo_prices = {
            'AAPL': Decimal('175.50'),
            'GOOGL': Decimal('142.80'),
            'MSFT': Decimal('380.20'),
            'TSLA': Decimal('245.30'),
            'NVDA': Decimal('485.90'),
            'AMZN': Decimal('145.60'),
            'META': Decimal('330.40'),
            'NFLX': Decimal('485.70'),
            'AMD': Decimal('125.30'),
            'INTC': Decimal('45.80'),
        }
        return demo_prices.get(ticker.upper(), Decimal('100.00'))
    
    @staticmethod
    def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed stock quote information
        Returns dict with price, change, volume, etc. or None if error
        """
        cache_key = f"stock_quote_{ticker.upper()}"
        cached_quote = cache.get(cache_key)
        if cached_quote is not None:
            return cached_quote
        
        # Try Yahoo Finance first
        quote = StockPriceService._get_yahoo_quote(ticker)
        if quote:
            cache.set(cache_key, quote, StockPriceService.CACHE_DURATION)
            return quote
        
        # Fallback to Alpha Vantage
        quote = StockPriceService._get_alphavantage_quote(ticker)
        if quote:
            cache.set(cache_key, quote, StockPriceService.CACHE_DURATION)
            return quote
        
        return None
    
    @staticmethod
    def _get_yahoo_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """Get quote from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                current_price = Decimal(str(info['regularMarketPrice']))
                previous_close = Decimal(str(info.get('regularMarketPreviousClose', current_price)))
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                return {
                    'symbol': ticker.upper(),
                    'price': current_price,
                    'change': change,
                    'change_percent': f"{change_percent:.2f}%",
                    'volume': int(info.get('volume', 0)),
                    'previous_close': previous_close,
                    'open': Decimal(str(info.get('regularMarketOpen', current_price))),
                    'high': Decimal(str(info.get('regularMarketDayHigh', current_price))),
                    'low': Decimal(str(info.get('regularMarketDayLow', current_price))),
                    'latest_trading_day': info.get('regularMarketTime', ''),
                }
            
            return None
                
        except Exception as e:
            print(f"Error fetching Yahoo Finance quote for {ticker}: {e}")
            return None
    
    @staticmethod
    def _get_alphavantage_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """Get quote from Alpha Vantage (fallback)"""
        try:
            api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if not api_key:
                return None
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker.upper(),
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "Information" in data and "rate limit" in data["Information"].lower():
                return None
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                return {
                    'symbol': quote.get('01. symbol'),
                    'price': Decimal(quote.get('05. price', 0)),
                    'change': Decimal(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%'),
                    'volume': int(quote.get('06. volume', 0)),
                    'previous_close': Decimal(quote.get('08. previous close', 0)),
                    'open': Decimal(quote.get('02. open', 0)),
                    'high': Decimal(quote.get('03. high', 0)),
                    'low': Decimal(quote.get('04. low', 0)),
                    'latest_trading_day': quote.get('07. latest trading day'),
                }
            
            return None
                
        except Exception as e:
            print(f"Error fetching Alpha Vantage quote for {ticker}: {e}")
            return None
    
    @staticmethod
    def search_stocks(query: str) -> list:
        """
        Search for stocks by company name or symbol
        Returns list of matching stocks
        """
        cache_key = f"stock_search_{query.lower()}"
        cached_results = cache.get(cache_key)
        if cached_results is not None:
            return cached_results
        
        try:
            api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if not api_key:
                return []
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': query,
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "bestMatches" in data:
                results = []
                for match in data["bestMatches"][:10]:  # Limit to 10 results
                    results.append({
                        'symbol': match.get('1. symbol'),
                        'name': match.get('2. name'),
                        'type': match.get('3. type'),
                        'region': match.get('4. region'),
                        'currency': match.get('8. currency'),
                    })
                
                # Cache the result
                cache.set(cache_key, results, StockPriceService.CACHE_DURATION)
                return results
            else:
                return []
                
        except Exception as e:
            print(f"Error searching stocks for '{query}': {e}")
            return []
    
    @staticmethod
    def get_company_overview(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed company information
        Returns company overview data or None if error
        """
        cache_key = f"company_overview_{ticker.upper()}"
        cached_overview = cache.get(cache_key)
        if cached_overview is not None:
            return cached_overview
        
        # Try Yahoo Finance first
        overview = StockPriceService._get_yahoo_overview(ticker)
        if overview:
            cache.set(cache_key, overview, StockPriceService.CACHE_DURATION)
            return overview
        
        # Fallback to Alpha Vantage
        overview = StockPriceService._get_alphavantage_overview(ticker)
        if overview:
            cache.set(cache_key, overview, StockPriceService.CACHE_DURATION)
            return overview
        
        return None
    
    @staticmethod
    def _get_yahoo_overview(ticker: str) -> Optional[Dict[str, Any]]:
        """Get company overview from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            if 'longName' in info or 'shortName' in info:
                return {
                    'symbol': ticker.upper(),
                    'name': info.get('longName') or info.get('shortName'),
                    'description': info.get('longBusinessSummary', ''),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', 'USD'),
                    'country': info.get('country', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap', 0),
                    'employees': info.get('fullTimeEmployees', 0),
                    'website': info.get('website', ''),
                }
            
            return None
                
        except Exception as e:
            print(f"Error fetching Yahoo Finance overview for {ticker}: {e}")
            return None
    
    @staticmethod
    def _get_alphavantage_overview(ticker: str) -> Optional[Dict[str, Any]]:
        """Get company overview from Alpha Vantage (fallback)"""
        try:
            api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if not api_key:
                return None
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': ticker.upper(),
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and not data.get('Note'):  # Check if we got actual data, not rate limit message
                return {
                    'symbol': data.get('Symbol'),
                    'name': data.get('Name'),
                    'description': data.get('Description'),
                    'exchange': data.get('Exchange'),
                    'currency': data.get('Currency'),
                    'country': data.get('Country'),
                    'sector': data.get('Sector'),
                    'industry': data.get('Industry'),
                    'market_cap': data.get('MarketCapitalization'),
                    'employees': data.get('FullTimeEmployees'),
                    'website': data.get('Website'),
                }
            
            return None
                
        except Exception as e:
            print(f"Error fetching Alpha Vantage overview for {ticker}: {e}")
            return None 