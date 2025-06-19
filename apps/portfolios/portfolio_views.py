from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Portfolio
from .services.calculation import PortfolioCalculator
from apps.stocks.services import StockPriceService
from django.core.cache import cache


@login_required
def portfolio_list(request):
    """Show user's portfolios"""
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolios/portfolio_list.html', {'portfolios': portfolios})


@login_required
def create_portfolio(request):
    """Create a new portfolio"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Portfolio name cannot be empty.')
        elif len(name) < 2:
            messages.error(request, 'Portfolio name must be at least 2 characters long.')
        elif len(name) > 100:
            messages.error(request, 'Portfolio name cannot exceed 100 characters.')
        elif Portfolio.objects.filter(user=request.user, name__iexact=name).exists():
            messages.error(request, f'You already have a portfolio named "{name}". Please choose a different name.')
        else:
            portfolio = Portfolio.objects.create(user=request.user, name=name)
            messages.success(request, f'Portfolio "{name}" created!')
            return redirect('portfolios:portfolio_detail', portfolio_id=portfolio.id)
    
    return render(request, 'portfolios/create_portfolio.html')


@login_required
def portfolio_detail(request, portfolio_id):
    """Show portfolio details with stocks and history"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    # Force refresh prices if requested
    force_refresh = request.GET.get('refresh') == 'true'
    
    # Update current prices for all stocks
    for stock in portfolio.stocks.all():
        if force_refresh:
            # Clear cache for this ticker
            cache_key = f"stock_price_{stock.ticker.upper()}"
            cache.delete(cache_key)
            cache_key_quote = f"stock_quote_{stock.ticker.upper()}"
            cache.delete(cache_key_quote)
        
        current_price = StockPriceService.get_stock_price(stock.ticker)
        if current_price:
            stock.current_price = current_price
            stock.save()
    
    # Calculate portfolio summary using service
    summary = PortfolioCalculator.calculate_portfolio_summary(portfolio)
    
    # Calculate unrealized profit/loss
    current_value = summary['totals']['current_value']
    purchase_value = summary['totals']['purchase_value']
    unrealized_profit = current_value - purchase_value
    unrealized_percent = (unrealized_profit / purchase_value * 100) if purchase_value else 0
    
    return render(request, 'portfolios/portfolio_detail.html', {
        'portfolio': portfolio,
        'summary': summary['active'],
        'history': summary['history'],
        'available_money': summary['totals']['available_money'],
        'total_profit': summary['totals']['total_profit'],
        'percent_profit': summary['totals']['percent_profit'],
        'current_value': current_value,
        'purchase_value': purchase_value,
        'unrealized_profit': unrealized_profit,
        'unrealized_percent': unrealized_percent,
    })


@login_required
def portfolio_history(request, portfolio_id):
    """Show history of fully sold tickers for a portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    # Calculate portfolio summary and get only history
    summary = PortfolioCalculator.calculate_portfolio_summary(portfolio)
    
    return render(request, 'portfolios/portfolio_history.html', {
        'portfolio': portfolio,
        'history': summary['history'],
    })


@login_required
def delete_portfolio(request, portfolio_id):
    """Delete a portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, f'Portfolio "{portfolio.name}" deleted.')
        return redirect('portfolios:portfolio_list')
    return render(request, 'portfolios/delete_portfolio_confirm.html', {'portfolio': portfolio})


@login_required
def rename_portfolio(request, portfolio_id):
    """Rename a portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        if not new_name:
            messages.error(request, 'Portfolio name cannot be empty.')
        elif len(new_name) < 2:
            messages.error(request, 'Portfolio name must be at least 2 characters long.')
        elif len(new_name) > 100:
            messages.error(request, 'Portfolio name cannot exceed 100 characters.')
        elif new_name.lower() == portfolio.name.lower():
            messages.error(request, 'New name must be different from the current name.')
        elif Portfolio.objects.filter(user=request.user, name__iexact=new_name).exclude(pk=portfolio.id).exists():
            messages.error(request, f'You already have a portfolio named "{new_name}". Please choose a different name.')
        else:
            portfolio.name = new_name
            portfolio.save()
            messages.success(request, f'Portfolio renamed to "{new_name}" successfully!')
            return redirect('portfolios:portfolio_list')
    return render(request, 'portfolios/rename_portfolio.html', {'portfolio': portfolio}) 