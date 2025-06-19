from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Portfolio, Stock, StockSale


@login_required
def sell_stock(request, portfolio_id, stock_id):
    """Sell a specific stock"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    stock = get_object_or_404(Stock, id=stock_id, portfolio=portfolio)
    available = stock.available_quantity()
    
    if available <= 0:
        messages.error(request, 'No shares available to sell.')
        return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            sale_price = float(request.POST.get('sale_price'))
        except (TypeError, ValueError):
            messages.error(request, 'Quantity and price must be valid numbers.')
        else:
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than 0.')
            elif quantity > available:
                messages.error(request, f'You can only sell up to {available} shares.')
            elif sale_price <= 0:
                messages.error(request, 'Sale price must be greater than 0.')
            elif sale_price > 100000:
                messages.error(request, 'Sale price cannot exceed $100,000 per share.')
            else:
                StockSale.objects.create(stock=stock, quantity=quantity, sale_price=sale_price)
                messages.success(request, f'Sold {quantity} shares of {stock.ticker} at ${sale_price}')
                return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)
    
    return render(request, 'portfolios/sell_stock.html', {'stock': stock, 'portfolio': portfolio, 'available': available})


@login_required
def sell_ticker(request, portfolio_id, ticker):
    """Sell shares of a specific ticker using FIFO"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    stocks = list(Stock.objects.filter(portfolio=portfolio, ticker=ticker).order_by('purchase_date'))  # FIFO
    available = sum(stock.available_quantity() for stock in stocks)
    
    if available <= 0:
        messages.error(request, f'No shares of {ticker} available to sell.')
        return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            sale_price = float(request.POST.get('sale_price'))
        except (TypeError, ValueError):
            messages.error(request, 'Quantity and price must be valid numbers.')
            return render(request, 'portfolios/sell_ticker.html', {'ticker': ticker, 'portfolio': portfolio, 'available': available})
        
        if quantity <= 0 or sale_price <= 0:
            messages.error(request, 'Quantity and price must be positive.')
            return render(request, 'portfolios/sell_ticker.html', {'ticker': ticker, 'portfolio': portfolio, 'available': available})
        
        if quantity > available:
            messages.error(request, f'You can sell up to {available} shares.')
            return render(request, 'portfolios/sell_ticker.html', {'ticker': ticker, 'portfolio': portfolio, 'available': available})
        
        # FIFO selling logic
        qty_left = quantity
        for stock in stocks:
            stock_avail = stock.available_quantity()
            if stock_avail <= 0:
                continue
            sell_qty = min(qty_left, stock_avail)
            StockSale.objects.create(stock=stock, quantity=sell_qty, sale_price=sale_price)
            qty_left -= sell_qty
            if qty_left == 0:
                break
        
        messages.success(request, f'Sold {quantity} shares of {ticker} at ${sale_price}')
        return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)
    
    return render(request, 'portfolios/sell_ticker.html', {'ticker': ticker, 'portfolio': portfolio, 'available': available}) 