from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .services import StockPriceService


@login_required
def search_stocks(request):
    """Search for stocks by company name or symbol"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    results = StockPriceService.search_stocks(query)
    return JsonResponse({'results': results})


@login_required
def stock_info(request, ticker):
    """Get detailed information about a stock"""
    ticker = ticker.upper()
    
    # Get current quote
    quote = StockPriceService.get_stock_quote(ticker)
    
    # Get company overview
    overview = StockPriceService.get_company_overview(ticker)
    
    context = {
        'ticker': ticker,
        'quote': quote,
        'overview': overview,
    }
    
    return render(request, 'stocks/stock_info.html', context)


@login_required
def get_stock_price(request, ticker):
    """API endpoint to get current stock price"""
    ticker = ticker.upper()
    price = StockPriceService.get_stock_price(ticker)
    
    if price:
        return JsonResponse({
            'ticker': ticker,
            'price': float(price),
            'success': True
        })
    else:
        return JsonResponse({
            'ticker': ticker,
            'success': False,
            'error': 'Could not fetch price'
        }, status=400)
