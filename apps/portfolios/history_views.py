from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from collections import defaultdict
from .models import Portfolio, Stock
from .services.calculation import PortfolioCalculator


@login_required
def delete_history_ticker(request, portfolio_id, ticker):
    """Delete history for a specific ticker"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    # Find all stocks for this ticker in this portfolio
    stocks = Stock.objects.filter(portfolio=portfolio, ticker=ticker)
    
    # Only allow deletion if all shares are sold
    total_qty = sum(s.quantity for s in stocks)
    total_sold = sum(sum(sale.quantity for sale in stock.sales.all()) for stock in stocks)
    
    if total_qty == total_sold:
        for stock in stocks:
            stock.sales.all().delete()
            stock.delete()
        messages.success(request, f"History for {ticker} deleted.")
    else:
        messages.error(request, f"Cannot delete {ticker}: not all shares are sold.")
    
    return redirect(reverse('portfolios:portfolio_history', args=[portfolio.id]))


@login_required
def clear_history(request, portfolio_id):
    """Clear all history for a portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        grouped = defaultdict(list)
        for stock in portfolio.stocks.all():
            grouped[stock.ticker].append(stock)
        
        deleted = 0
        for ticker, stocks in grouped.items():
            total_qty = sum(s.quantity for s in stocks)
            total_sold = sum(sum(sale.quantity for sale in stock.sales.all()) for stock in stocks)
            
            if total_qty == total_sold:
                for stock in stocks:
                    stock.sales.all().delete()
                    stock.delete()
                deleted += 1
        
        if deleted:
            messages.success(request, f"History cleared for {deleted} tickers.")
        else:
            messages.info(request, "No fully sold tickers to delete.")
        
        return redirect(reverse('portfolios:portfolio_history', args=[portfolio.id]))
    
    # GET: show confirmation
    return render(request, 'portfolios/clear_history_confirm.html', {'portfolio': portfolio})


@login_required
def ticker_detail(request, portfolio_id, ticker):
    """Show detailed history for a specific ticker"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    # Use service to calculate ticker detail summary
    summary = PortfolioCalculator.calculate_ticker_detail_summary(portfolio, ticker)
    
    if not summary:
        messages.error(request, f'No stocks found for ticker {ticker}')
        return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)
    
    return render(request, 'portfolios/ticker_detail.html', summary) 