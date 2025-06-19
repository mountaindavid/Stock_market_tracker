from django.urls import path
from . import views

app_name = 'portfolios'

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('create/', views.create_portfolio, name='create_portfolio'),
    path('<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('<int:portfolio_id>/ticker/<str:ticker>/', views.ticker_detail, name='ticker_detail'),
    path('<int:portfolio_id>/add-stock/', views.add_stock, name='add_stock'),
    path('<int:portfolio_id>/delete-stock/<int:stock_id>/', views.delete_stock, name='delete_stock'),
    path('<int:portfolio_id>/sell-ticker/<str:ticker>/', views.sell_ticker, name='sell_ticker'),
    path('<int:portfolio_id>/history/', views.portfolio_history, name='portfolio_history'),
    path('<int:portfolio_id>/history/delete/<str:ticker>/', views.delete_history_ticker, name='delete_history_ticker'),
    path('<int:portfolio_id>/history/clear/', views.clear_history, name='clear_history'),
    path('<int:portfolio_id>/delete/', views.delete_portfolio, name='delete_portfolio'),
    path('<int:portfolio_id>/rename/', views.rename_portfolio, name='rename_portfolio'),
] 