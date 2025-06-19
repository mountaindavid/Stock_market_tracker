from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('search/', views.search_stocks, name='search_stocks'),
    path('info/<str:ticker>/', views.stock_info, name='stock_info'),
    path('price/<str:ticker>/', views.get_stock_price, name='get_stock_price'),
] 