from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Tuple, Any
from ..models import Portfolio, Stock, StockSale
from apps.stocks.services import StockPriceService


class PortfolioCalculator:
    """Service for portfolio calculations and summaries"""
    
    @staticmethod
    def calculate_portfolio_summary(portfolio: Portfolio) -> Dict[str, Any]:
        """
        Calculate complete portfolio summary including active stocks and history
        Returns dict with 'active', 'history', 'totals'
        """
        # Group stocks by ticker
        grouped = defaultdict(list)
        for stock in portfolio.stocks.all():
            grouped[stock.ticker].append(stock)

        # Split into active and history
        active = []
        history = []
        
        for ticker, purchases in grouped.items():
            ticker_summary = PortfolioCalculator.calculate_ticker_summary(ticker, purchases)
            
            if ticker_summary['remaining_qty'] > 0:
                active.append(ticker_summary)
            else:
                history.append(ticker_summary)

        # Calculate portfolio totals
        totals = PortfolioCalculator.calculate_portfolio_totals(portfolio)
        
        return {
            'active': active,
            'history': history,
            'totals': totals
        }
    
    @staticmethod
    def calculate_ticker_summary(ticker: str, purchases: List[Stock]) -> Dict[str, Any]:
        """
        Calculate summary for a specific ticker
        Returns dict with ticker data including company info and quotes
        """
        # Get company overview and quote data
        company_info = StockPriceService.get_company_overview(ticker)
        quote_info = StockPriceService.get_stock_quote(ticker)
        
        # Calculate basic metrics
        total_qty = sum(s.quantity for s in purchases)
        total_sold = sum(sum(sale.quantity for sale in stock.sales.all()) for stock in purchases)
        remaining_qty = total_qty - total_sold
        
        # Calculate profit/loss for remaining shares
        profit_data = PortfolioCalculator.calculate_profit_loss(purchases, remaining_qty)
        
        # Prepare ticker data
        ticker_data = {
            'ticker': ticker,
            'purchases': purchases,
            'total_qty': total_qty,
            'remaining_qty': remaining_qty,
            'total_sold': total_sold,
            'avg_price': profit_data['avg_price'],
            'profit': profit_data['profit'],
            'percent_profit': profit_data['percent_profit'],
            'current_value': profit_data['current_value'],
            'company_info': company_info,
            'quote_info': quote_info,
        }
        
        # Add sales data for history
        if remaining_qty == 0:
            sales_data = PortfolioCalculator.calculate_sales_summary(purchases)
            ticker_data.update(sales_data)
        
        return ticker_data
    
    @staticmethod
    def calculate_profit_loss(purchases: List[Stock], remaining_qty: int) -> Dict[str, Any]:
        """
        Calculate profit/loss for remaining shares
        Returns dict with profit, percent_profit, avg_price, current_value
        """
        remaining_lots = []
        profit = Decimal('0')
        invested = Decimal('0')
        current = Decimal('0')
        
        for stock in purchases:
            sold = sum(sale.quantity for sale in stock.sales.all())
            unsold = stock.quantity - sold
            if unsold > 0:
                remaining_lots.append((unsold, stock.purchase_price))
                invested += stock.purchase_price * unsold
                current_price = stock.current_price or stock.purchase_price
                current += current_price * unsold
                profit += (current_price - stock.purchase_price) * unsold
        
        if remaining_lots:
            avg_price = sum(q * price for q, price in remaining_lots) / sum(q for q, _ in remaining_lots)
            percent_profit = (profit / invested * 100) if invested else 0
        else:
            avg_price = Decimal('0')
            percent_profit = 0
        
        return {
            'profit': profit,
            'percent_profit': percent_profit,
            'avg_price': avg_price,
            'current_value': current
        }
    
    @staticmethod
    def calculate_sales_summary(purchases: List[Stock]) -> Dict[str, Any]:
        """
        Calculate summary for sold shares
        Returns dict with sales, profit, total_received
        """
        all_sales = []
        profit = Decimal('0')
        invested = Decimal('0')
        received = Decimal('0')
        
        for stock in purchases:
            for sale in stock.sales.all():
                all_sales.append(sale)
                invested += stock.purchase_price * sale.quantity
                received += sale.sale_price * sale.quantity
                profit += (sale.sale_price - stock.purchase_price) * sale.quantity
        
        percent_profit = ((received - invested) / invested * 100) if invested else 0
        
        return {
            'sales': all_sales,
            'profit': profit,
            'percent_profit': percent_profit,
            'total_received': received
        }
    
    @staticmethod
    def calculate_portfolio_totals(portfolio: Portfolio) -> Dict[str, Any]:
        """
        Calculate portfolio totals
        Returns dict with available_money, total_profit, percent_profit, etc.
        """
        all_stocks = portfolio.stocks.all()
        total_invested = Decimal('0')
        total_received = Decimal('0')
        total_profit = Decimal('0')
        
        for stock in all_stocks:
            for sale in stock.sales.all():
                total_invested += stock.purchase_price * sale.quantity
                total_received += sale.sale_price * sale.quantity
                total_profit += (sale.sale_price - stock.purchase_price) * sale.quantity
        
        available_money = total_received - total_invested
        percent_profit = ((total_received - total_invested) / total_invested * 100) if total_invested else 0
        
        return {
            'available_money': available_money,
            'total_profit': total_profit,
            'percent_profit': percent_profit,
            'current_value': portfolio.current_value(),
            'purchase_value': portfolio.purchase_value(),
        }
    
    @staticmethod
    def calculate_ticker_detail_summary(portfolio: Portfolio, ticker: str) -> Dict[str, Any]:
        """
        Calculate detailed summary for ticker detail page
        Returns dict with all ticker information
        """
        stocks = list(Stock.objects.filter(portfolio=portfolio, ticker=ticker).order_by('purchase_date'))
        
        if not stocks:
            return None
        
        # Get company info
        company_info = StockPriceService.get_company_overview(ticker)
        quote_info = StockPriceService.get_stock_quote(ticker)
        
        # Calculate totals
        total_qty = sum(s.quantity for s in stocks)
        total_sold = sum(sum(sale.quantity for sale in stock.sales.all()) for stock in stocks)
        remaining_qty = total_qty - total_sold
        
        # Calculate profit/loss
        profit_data = PortfolioCalculator.calculate_profit_loss(stocks, remaining_qty)
        
        # Collect all sales
        all_sales = []
        for stock in stocks:
            for sale in stock.sales.all():
                all_sales.append({
                    'sale': sale,
                    'purchase_price': stock.purchase_price,
                    'purchase_date': stock.purchase_date,
                })
        
        # Sort sales by date
        all_sales.sort(key=lambda x: x['sale'].sale_date)
        
        return {
            'portfolio': portfolio,
            'ticker': ticker,
            'stocks': stocks,
            'company_info': company_info,
            'quote_info': quote_info,
            'total_qty': total_qty,
            'remaining_qty': remaining_qty,
            'total_sold': total_sold,
            'avg_price': profit_data['avg_price'],
            'profit': profit_data['profit'],
            'percent_profit': profit_data['percent_profit'],
            'current_value': profit_data['current_value'],
            'all_sales': all_sales,
        } 