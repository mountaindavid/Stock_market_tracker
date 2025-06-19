# Import all views from separate modules for better organization
from .portfolio_views import (
    portfolio_list,
    create_portfolio,
    portfolio_detail,
    portfolio_history,
    delete_portfolio,
    rename_portfolio,
)

from .stock_views import (
    add_stock,
    delete_stock,
)

from .sale_views import (
    sell_stock,
    sell_ticker,
)

from .history_views import (
    delete_history_ticker,
    clear_history,
    ticker_detail,
)
