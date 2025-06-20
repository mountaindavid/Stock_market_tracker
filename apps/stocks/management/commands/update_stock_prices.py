from django.core.management.base import BaseCommand
from django.db import transaction
from apps.portfolios.models import Stock
from apps.stocks.services import StockPriceService


class Command(BaseCommand):
    help = 'Update current stock prices for all stocks in portfolios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all prices, ignoring cache',
        )
        parser.add_argument(
            '--ticker',
            type=str,
            help='Update prices for specific ticker only',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting stock price update...')
        
        # Get all unique tickers from portfolios
        if options['ticker']:
            tickers = [options['ticker'].upper()]
            self.stdout.write(f'Updating prices for ticker: {options["ticker"]}')
        else:
            tickers = Stock.objects.values_list('ticker', flat=True).distinct()
            self.stdout.write(f'Found {len(tickers)} unique tickers to update')
        
        updated_count = 0
        error_count = 0
        
        for ticker in tickers:
            try:
                self.stdout.write(f'Fetching price for {ticker}...')
                
                # Get current price
                current_price = StockPriceService.get_stock_price(ticker)
                
                if current_price is not None:
                    # Update all stocks with this ticker
                    stocks_to_update = Stock.objects.filter(ticker=ticker)
                    updated_stocks = stocks_to_update.update(current_price=current_price)
                    
                    updated_count += updated_stocks
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {updated_stocks} stocks for {ticker} at ${current_price}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Could not fetch price for {ticker}')
                    )
                    error_count += 1
                
                # Rate limiting is now handled by StockPriceService
                # No need for manual sleep here
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating {ticker}: {e}')
                )
                error_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Price update completed. Updated: {updated_count}, Errors: {error_count}'
            )
        ) 