from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Portfolio, Stock
from apps.stocks.services import StockPriceService


@login_required
def add_stock(request, portfolio_id):
    """Add a stock to portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '').upper().strip()
        
        # Validate ticker
        if not ticker:
            messages.error(request, 'Ticker symbol is required.')
        elif len(ticker) > 10:
            messages.error(request, 'Ticker symbol cannot exceed 10 characters.')
        elif not ticker.replace(' ', '').isalnum():
            messages.error(request, 'Ticker symbol must contain only letters and numbers.')
        
        # Validate quantity and price
        else:
            try:
                quantity = int(request.POST.get('quantity'))
                purchase_price = float(request.POST.get('purchase_price'))
            except (TypeError, ValueError):
                messages.error(request, 'Quantity and price must be valid numbers.')
            else:
                if quantity <= 0:
                    messages.error(request, 'Quantity must be greater than 0.')
                elif quantity > 1000000:
                    messages.error(request, 'Quantity cannot exceed 1,000,000 shares.')
                elif purchase_price <= 0:
                    messages.error(request, 'Purchase price must be greater than 0.')
                elif purchase_price > 100000:
                    messages.error(request, 'Purchase price cannot exceed $100,000 per share.')
                else:
                    # Check total position value
                    total_value = quantity * purchase_price
                    if total_value > 10000000:  # $10M limit
                        messages.error(request, 'Total position value cannot exceed $10,000,000.')
                    else:
                        # Get company info from service
                        company_info = StockPriceService.get_company_overview(ticker)
                        if not company_info or not company_info.get('name'):
                            messages.error(request, f"Could not find company information for ticker '{ticker}'. Please check the symbol and try again.")
                            return redirect('portfolios:add_stock', portfolio_id=portfolio.id)
                        
                        company_name = company_info['name']

                        stock = Stock.objects.create(
                            portfolio=portfolio,
                            ticker=ticker,
                            company_name=company_name,
                            quantity=quantity,
                            purchase_price=purchase_price,
                            current_price=StockPriceService.get_stock_price(ticker)
                        )
                        messages.success(request, f'Added {quantity} shares of {company_name} ({ticker})')
                        return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)
    
    return render(request, 'portfolios/add_stock.html', {'portfolio': portfolio})


@login_required
def delete_stock(request, portfolio_id, stock_id):
    """Delete a stock from portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    stock = get_object_or_404(Stock, id=stock_id, portfolio=portfolio)
    
    stock.delete()
    messages.success(request, f'Removed {stock.ticker} from portfolio')
    return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id) 