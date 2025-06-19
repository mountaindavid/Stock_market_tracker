from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.portfolios.models import Stock
from apps.stocks.services import StockPriceService


class Command(BaseCommand):
    help = 'Update current prices for all stocks in all portfolios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh by clearing cache',
        )

    def handle(self, *args, **options):
        force_refresh = options['force']
        
        if force_refresh:
            self.stdout.write('Clearing price cache...')
            # Clear all stock price related cache
            for stock in Stock.objects.all():
                cache_key = f"stock_price_{stock.ticker.upper()}"
                cache.delete(cache_key)
                cache_key_quote = f"stock_quote_{stock.ticker.upper()}"
                cache.delete(cache_key_quote)
        
        self.stdout.write('Updating stock prices...')
        
        updated_count = 0
        error_count = 0
        
        for stock in Stock.objects.all():
            try:
                current_price = StockPriceService.get_stock_price(stock.ticker)
                if current_price:
                    old_price = stock.current_price
                    stock.current_price = current_price
                    stock.save()
                    updated_count += 1
                    
                    if old_price != current_price:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'{stock.ticker}: ${old_price} → ${current_price}'
                            )
                        )
                    else:
                        self.stdout.write(
                            f'{stock.ticker}: ${current_price} (no change)'
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'{stock.ticker}: Failed to get price')
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'{stock.ticker}: Error - {e}')
                )
                error_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Price update completed: {updated_count} updated, {error_count} errors'
            )
        ) 