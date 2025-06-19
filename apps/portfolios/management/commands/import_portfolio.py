from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime
from apps.portfolios.models import Portfolio, Stock
from apps.stocks.services import StockPriceService

User = get_user_model()


class Command(BaseCommand):
    help = 'Import portfolio data from raw stock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            required=True,
            help='Email of the user to create portfolio for',
        )
        parser.add_argument(
            '--portfolio-name',
            type=str,
            default='My Portfolio',
            help='Name for the new portfolio',
        )

    def handle(self, *args, **options):
        user_email = options['user_email']
        portfolio_name = options['portfolio_name']
        
        # Get or create user
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {user_email} does not exist')
            )
            return
        
        # Create portfolio
        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            name=portfolio_name,
            defaults={'name': portfolio_name}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created portfolio: {portfolio_name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Portfolio {portfolio_name} already exists')
            )
        
        # Raw portfolio data
        portfolio_data = [
            ('TSLA', 9, Decimal('269.25')),
            ('META', 30, Decimal('173.57')),
            ('GOOGL', 70, Decimal('111.96')),
            ('AAPL', 47, Decimal('160.94')),
            ('MSFT', 38, Decimal('263.55')),
            ('VOO', 18, Decimal('377.13')),
            ('JNJ', 20, Decimal('166.13')),
            ('PFE', 140, Decimal('49.00')),
            ('JPM', 57, Decimal('116.00')),
            ('STX', 105, Decimal('72.97')),
            ('ABBV', 50, Decimal('139.15')),
            ('C', 150, Decimal('48.18')),
            ('LEG', 170, Decimal('38.51')),
        ]
        
        added_count = 0
        updated_count = 0
        
        for ticker, quantity, purchase_price in portfolio_data:
            # Get current price and company info
            current_price = StockPriceService.get_stock_price(ticker)
            company_info = StockPriceService.get_company_overview(ticker)
            
            company_name = company_info.get('name', ticker) if company_info else ticker
            
            # Create stock
            stock, created = Stock.objects.get_or_create(
                portfolio=portfolio,
                ticker=ticker.upper(),
                purchase_price=purchase_price,
                defaults={
                    'company_name': company_name,
                    'quantity': quantity,
                    'current_price': current_price,
                    'purchase_date': datetime.now(),
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Added {ticker}: {quantity} shares @ ${purchase_price}'
                    )
                )
                added_count += 1
            else:
                # Update existing stock
                stock.quantity = quantity
                stock.purchase_price = purchase_price
                stock.current_price = current_price
                stock.company_name = company_name
                stock.save()
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Updated {ticker}: {quantity} shares @ ${purchase_price}'
                    )
                )
                updated_count += 1
        
        # Calculate portfolio summary
        total_value = portfolio.current_value()
        total_purchase = portfolio.purchase_value()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nPortfolio Summary:'
                f'\n- Total stocks: {added_count + updated_count}'
                f'\n- Added: {added_count}'
                f'\n- Updated: {updated_count}'
                f'\n- Current value: ${total_value:.2f}'
                f'\n- Purchase value: ${total_purchase:.2f}'
                f'\n- Profit/Loss: ${(total_value - total_purchase):.2f}'
            )
        ) 