from django.core.cache import cache
import yfinance as yf
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, Any
from collections import deque
from threading import Lock
import random


class StockPriceService:
    """Service to fetch current stock prices from multiple APIs"""
    
    # Cache duration in seconds (1 hour to further reduce API calls)
    CACHE_DURATION = 3600
    
    # Request queue for rate limiting
    _request_times = deque(maxlen=100)  # Keep last 100 request times
    _request_lock = Lock()
    
    # Rate limiting: max 5 requests per minute for Yahoo Finance
    MAX_REQUESTS_PER_MINUTE = 5
    MIN_REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE  # 12 seconds
    
    @staticmethod
    def _rate_limit():
        """Implement rate limiting for API requests"""
        with StockPriceService._request_lock:
            current_time = time.time()
            
            # Remove old requests (older than 1 minute)
            while StockPriceService._request_times and current_time - StockPriceService._request_times[0] > 60:
                StockPriceService._request_times.popleft()
            
            # Check if we're at the rate limit
            if len(StockPriceService._request_times) >= StockPriceService.MAX_REQUESTS_PER_MINUTE:
                # Wait until we can make another request
                sleep_time = 60 - (current_time - StockPriceService._request_times[0]) + 1
                if sleep_time > 0:
                    print(f"Rate limit reached. Waiting {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    current_time = time.time()
            
            # Add current request time
            StockPriceService._request_times.append(current_time)
    
    @staticmethod
    def get_stock_price(ticker: str) -> Optional[Decimal]:
        """Get current stock price from Yahoo Finance with caching and fallback."""
        cache_key = f"stock_price_{ticker.upper()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Decimal(str(cached))
        
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            if price is not None:
                cache.set(cache_key, str(price), StockPriceService.CACHE_TIMEOUT)
                return Decimal(str(price))
        except Exception as e:
            print(f"YF error for {ticker}: {e}")
        
        # No fallback - return None if no data available
        return None
    
    @staticmethod
    def _get_yahoo_price(ticker: str) -> Optional[Decimal]:
        """Get price from Yahoo Finance with rate limiting"""
        try:
            # Apply rate limiting
            StockPriceService._rate_limit()
            
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            result = {
                'symbol': ticker.upper(),
                'name': info.get('longName') or info.get('shortName') or ticker.upper(),
                'description': info.get('longBusinessSummary', ''),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', ''),
                'country': info.get('country', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
            }
            cache.set(cache_key, result, StockPriceService.CACHE_TIMEOUT)
            return result
        except Exception as e:
            print(f"YF company info error for {ticker}: {e}")
        
        # Fallback to demo data
        demo_info = StockPriceService._get_demo_company_info(ticker)
        if demo_info:
            cache.set(cache_key, demo_info, StockPriceService.CACHE_TIMEOUT)
            return demo_info
        return None

    @staticmethod
    def get_stock_quote(ticker: str):
        """Get detailed stock quote from Yahoo Finance with caching and fallback."""
        cache_key = f"stock_quote_{ticker.upper()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            # Get API key from settings
            api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if not api_key or api_key == 'demo':
                return None
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker.upper(),
                'price': Decimal(str(current_price)) if current_price is not None else None,
                'change': change,
                'change_percent': f"{change_percent:.2f}%" if change_percent is not None else None,
                'volume': info.get('volume'),
                'previous_close': Decimal(str(previous_close)) if previous_close is not None else None,
                'open': info.get('regularMarketOpen'),
                'high': info.get('regularMarketDayHigh'),
                'low': info.get('regularMarketDayLow'),
                'latest_trading_day': info.get('regularMarketTime'),
            }
            cache.set(cache_key, result, StockPriceService.CACHE_TIMEOUT)
            return result
        except Exception as e:
            print(f"YF quote error for {ticker}: {e}")
        
        # Fallback to demo data
        demo_quote = StockPriceService._get_demo_quote(ticker)
        if demo_quote:
            cache.set(cache_key, demo_quote, StockPriceService.CACHE_TIMEOUT)
            return demo_quote
        return None

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
        """Get quote from Yahoo Finance with rate limiting"""
        try:
            # Apply rate limiting
            StockPriceService._rate_limit()
            
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
            if not api_key or api_key == 'demo':
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
        
        try:
            api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if not api_key or api_key == 'demo':
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
        """Get company overview from Yahoo Finance with rate limiting"""
        try:
            # Apply rate limiting
            StockPriceService._rate_limit()
            
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
            if not api_key or api_key == 'demo':
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
