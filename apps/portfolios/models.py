from django.db import models
from django.conf import settings


class Portfolio(models.Model):
    """User's stock portfolio"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    def total_value(self):
        """Calculate total portfolio value: value of all current shares + available money (realized profit/loss)"""
        # Value of all currently held (unsold) shares
        stocks = self.stocks.all()
        current_value = sum(stock.available_quantity() * (stock.current_price or stock.purchase_price) for stock in stocks)
        # Calculate available money (realized profit/loss)
        total_invested = 0
        total_received = 0
        for stock in stocks:
            for sale in stock.sales.all():
                total_invested += stock.purchase_price * sale.quantity
                total_received += sale.sale_price * sale.quantity
        available_money = total_received - total_invested
        return current_value + available_money

    def current_value(self):
        """Sum of all unsold shares at current (market) price"""
        return sum(stock.available_quantity() * (stock.current_price or stock.purchase_price) for stock in self.stocks.all())

    def purchase_value(self):
        """Sum of all unsold shares at their purchase price"""
        return sum(stock.available_quantity() * stock.purchase_price for stock in self.stocks.all())


class Stock(models.Model):
    """Individual stock in a portfolio"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='stocks')
    ticker = models.CharField(max_length=10)  # e.g., AAPL, GOOGL
    company_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ticker} - {self.quantity} shares"
    
    def available_quantity(self):
        sold = sum(sale.quantity for sale in self.sales.all())
        return self.quantity - sold

    @property
    def total_purchase_value(self):
        """Total purchase value for this stock lot"""
        return self.quantity * self.purchase_price

    @property
    def current_value(self):
        """Current value of this stock lot"""
        current_price = self.current_price or self.purchase_price
        return self.quantity * current_price

    @property
    def profit_loss(self):
        """Profit/loss for this stock lot"""
        current_price = self.current_price or self.purchase_price
        return (current_price - self.purchase_price) * self.quantity


class StockSale(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sell {self.quantity} of {self.stock.ticker} at {self.sale_price}"

    @property
    def total_sale_value(self):
        """Total sale value"""
        return self.quantity * self.sale_price

    @property
    def profit(self):
        """Profit from this sale"""
        return (self.sale_price - self.stock.purchase_price) * self.quantity
