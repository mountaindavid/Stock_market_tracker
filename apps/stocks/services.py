from django.core.cache import cache
import yfinance as yf
from decimal import Decimal
from typing import Optional

class StockPriceService:
    CACHE_TIMEOUT = 1800  # 30 минут

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
        
        return None

    @staticmethod
    def get_company_overview(ticker: str):
        """Get company info from Yahoo Finance with caching and fallback."""
        cache_key = f"company_overview_{ticker.upper()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
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
        
        return None

    @staticmethod
    def get_stock_quote(ticker: str):
        """Get detailed stock quote from Yahoo Finance with caching and fallback."""
        cache_key = f"stock_quote_{ticker.upper()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            previous_close = info.get('regularMarketPreviousClose', current_price)
            change = None
            change_percent = None
            if current_price is not None and previous_close is not None:
                change = Decimal(str(current_price)) - Decimal(str(previous_close))
                if Decimal(str(previous_close)) != 0:
                    change_percent = (change / Decimal(str(previous_close))) * 100
            result = {
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
        
        return None

    @staticmethod
    def _get_demo_price(ticker: str) -> Optional[Decimal]:
        """Get demo price for fallback."""
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
            'JPM': Decimal('195.40'),
            'V': Decimal('275.60'),
            'WMT': Decimal('65.20'),
            'JNJ': Decimal('155.80'),
            'PG': Decimal('165.30'),
        }
        return demo_prices.get(ticker.upper())

    @staticmethod
    def _get_demo_company_info(ticker: str):
        """Get demo company info for fallback."""
        demo_companies = {
            'AAPL': {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'description': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services.',
                'exchange': 'NASDAQ',
                'currency': 'USD',
                'country': 'United States',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'market_cap': 2800000000000,
                'employees': 164000,
                'website': 'https://www.apple.com',
            },
            'GOOGL': {
                'symbol': 'GOOGL',
                'name': 'Alphabet Inc.',
                'description': 'Alphabet Inc. is an American multinational technology conglomerate holding company.',
                'exchange': 'NASDAQ',
                'currency': 'USD',
                'country': 'United States',
                'sector': 'Technology',
                'industry': 'Internet Content & Information',
                'market_cap': 1800000000000,
                'employees': 156500,
                'website': 'https://www.google.com',
            },
            'MSFT': {
                'symbol': 'MSFT',
                'name': 'Microsoft Corporation',
                'description': 'Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.',
                'exchange': 'NASDAQ',
                'currency': 'USD',
                'country': 'United States',
                'sector': 'Technology',
                'industry': 'Software—Infrastructure',
                'market_cap': 3000000000000,
                'employees': 221000,
                'website': 'https://www.microsoft.com',
            },
        }
        return demo_companies.get(ticker.upper(), {
            'symbol': ticker.upper(),
            'name': ticker.upper(),
            'description': 'Demo company information',
            'exchange': '',
            'currency': 'USD',
            'country': '',
            'sector': '',
            'industry': '',
            'market_cap': 0,
            'employees': 0,
            'website': '',
        })

    @staticmethod
    def _get_demo_quote(ticker: str):
        """Get demo quote for fallback."""
        demo_price = StockPriceService._get_demo_price(ticker)
        if demo_price is None:
            return None
        
        # Simulate some price movement
        import random
        change = Decimal(str(random.uniform(-5, 5)))
        change_percent = (change / demo_price) * 100
        
        return {
            'symbol': ticker.upper(),
            'price': demo_price,
            'change': change,
            'change_percent': f"{change_percent:.2f}%",
            'volume': random.randint(1000000, 50000000),
            'previous_close': demo_price - change,
            'open': demo_price + Decimal(str(random.uniform(-2, 2))),
            'high': demo_price + Decimal(str(random.uniform(0, 3))),
            'low': demo_price - Decimal(str(random.uniform(0, 3))),
            'latest_trading_day': '2025-06-20',
        } 