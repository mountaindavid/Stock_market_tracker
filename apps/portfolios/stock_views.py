from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Portfolio, Stock


@login_required
def add_stock(request, portfolio_id):
    """Add a stock to portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '').upper().strip()
        company_name = request.POST.get('company_name', '').strip()
        
        # Validate ticker
        if not ticker:
            messages.error(request, 'Ticker symbol is required.')
        elif len(ticker) > 10:
            messages.error(request, 'Ticker symbol cannot exceed 10 characters.')
        elif not ticker.replace(' ', '').isalnum():
            messages.error(request, 'Ticker symbol must contain only letters and numbers.')
        
        # Validate company name
        elif not company_name:
            messages.error(request, 'Company name is required.')
        elif len(company_name) < 2:
            messages.error(request, 'Company name must be at least 2 characters long.')
        elif len(company_name) > 200:
            messages.error(request, 'Company name cannot exceed 200 characters.')
        
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
                        stock = Stock.objects.create(
                            portfolio=portfolio,
                            ticker=ticker,
                            company_name=company_name,
                            quantity=quantity,
                            purchase_price=purchase_price
                        )
                        messages.success(request, f'Added {quantity} shares of {ticker}')
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