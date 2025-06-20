# 📚 API Documentation - Stock Market Portfolio Manager

## 🏠 **Base URL**
```
http://localhost:8000
```

---

## 🔐 **Аутентификация**

Все API endpoints требуют аутентификации пользователя. Используйте Django session-based аутентификацию.

### Вход в систему
```http
POST /login/
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=your_password
```

### Выход из системы
```http
POST /logout/
```

---

## 👥 **Users API**

### Получить профиль текущего пользователя
```http
GET /api/users/profile/
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### Обновить профиль пользователя
```http
PUT /api/users/profile/
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith"
}
```

---

## 📊 **Portfolios API**

### Получить список портфелей пользователя
```http
GET /api/portfolios/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Main Portfolio",
    "description": "Primary investment portfolio",
    "created_at": "2024-01-15T10:30:00Z",
    "total_value": 125000.50,
    "total_profit": 15000.25,
    "profit_percentage": 13.6
  }
]
```

### Создать новый портфель
```http
POST /api/portfolios/
Content-Type: application/json

{
  "name": "New Portfolio",
  "description": "Portfolio description"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Portfolio",
  "description": "Portfolio description",
  "created_at": "2024-01-15T11:00:00Z",
  "total_value": 0.00,
  "total_profit": 0.00,
  "profit_percentage": 0.0
}
```

### Получить детали портфеля
```http
GET /api/portfolios/{portfolio_id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "My Main Portfolio",
  "description": "Primary investment portfolio",
  "created_at": "2024-01-15T10:30:00Z",
  "total_value": 125000.50,
  "total_profit": 15000.25,
  "profit_percentage": 13.6,
  "available_money": 5000.00,
  "stocks": [
    {
      "id": 1,
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "quantity": 100,
      "purchase_price": 150.00,
      "current_price": 200.02,
      "total_value": 20002.00,
      "profit_loss": 5002.00,
      "profit_percentage": 33.3
    }
  ]
}
```

### Обновить портфель
```http
PUT /api/portfolios/{portfolio_id}/
Content-Type: application/json

{
  "name": "Updated Portfolio Name",
  "description": "Updated description"
}
```

### Удалить портфель
```http
DELETE /api/portfolios/{portfolio_id}/
```

---

## 📈 **Stocks API**

### Получить список акций в портфеле
```http
GET /api/portfolios/{portfolio_id}/stocks/
```

**Response:**
```json
[
  {
    "id": 1,
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "quantity": 100,
    "purchase_price": 150.00,
    "current_price": 200.02,
    "purchase_date": "2024-01-15T10:30:00Z",
    "total_value": 20002.00,
    "profit_loss": 5002.00,
    "profit_percentage": 33.3,
    "available_quantity": 100
  }
]
```

### Добавить акцию в портфель
```http
POST /api/portfolios/{portfolio_id}/stocks/
Content-Type: application/json

{
  "ticker": "MSFT",
  "quantity": 50,
  "purchase_price": 300.00
}
```

**Response:**
```json
{
  "id": 2,
  "ticker": "MSFT",
  "company_name": "Microsoft Corporation",
  "quantity": 50,
  "purchase_price": 300.00,
  "current_price": 478.82,
  "purchase_date": "2024-01-15T11:30:00Z",
  "total_value": 23941.00,
  "profit_loss": 8941.00,
  "profit_percentage": 59.6,
  "available_quantity": 50
}
```

### Получить детали акции
```http
GET /api/portfolios/{portfolio_id}/stocks/{stock_id}/
```

### Обновить акцию
```http
PUT /api/portfolios/{portfolio_id}/stocks/{stock_id}/
Content-Type: application/json

{
  "quantity": 75,
  "purchase_price": 155.00
}
```

### Удалить акцию
```http
DELETE /api/portfolios/{portfolio_id}/stocks/{stock_id}/
```

---

## 💰 **Stock Sales API**

### Получить историю продаж акции
```http
GET /api/portfolios/{portfolio_id}/stocks/{stock_id}/sales/
```

**Response:**
```json
[
  {
    "id": 1,
    "quantity": 25,
    "sale_price": 180.00,
    "sale_date": "2024-01-20T14:30:00Z",
    "profit_loss": 750.00,
    "profit_percentage": 20.0
  }
]
```

### Продать акции
```http
POST /api/portfolios/{portfolio_id}/stocks/{stock_id}/sales/
Content-Type: application/json

{
  "quantity": 25,
  "sale_price": 180.00
}
```

**Response:**
```json
{
  "id": 2,
  "quantity": 25,
  "sale_price": 180.00,
  "sale_date": "2024-01-20T15:00:00Z",
  "profit_loss": 750.00,
  "profit_percentage": 20.0,
  "remaining_quantity": 50
}
```

---

## 🔍 **Stock Market Data API**

### Получить текущую цену акции
```http
GET /api/stocks/{ticker}/price/
```

**Response:**
```json
{
  "ticker": "AAPL",
  "price": 200.02,
  "success": true,
  "timestamp": "2024-01-20T15:30:00Z"
}
```

### Получить детальную информацию об акции
```http
GET /api/stocks/{ticker}/quote/
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 200.02,
  "change": 2.50,
  "change_percent": "1.26%",
  "volume": 45678900,
  "previous_close": 197.52,
  "open": 198.00,
  "high": 201.50,
  "low": 197.80,
  "latest_trading_day": "2024-01-20"
}
```

### Получить информацию о компании
```http
GET /api/stocks/{ticker}/overview/
```

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "description": "Apple Inc. designs, manufactures, and markets smartphones...",
  "exchange": "NMS",
  "currency": "USD",
  "country": "United States",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "market_cap": 2964684537856,
  "employees": 164000,
  "website": "https://www.apple.com"
}
```

### Поиск акций
```http
GET /api/stocks/search/?q=apple
```

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "type": "Equity",
    "region": "United States",
    "currency": "USD"
  },
  {
    "symbol": "APLE",
    "name": "Apple Hospitality REIT Inc",
    "type": "Equity",
    "region": "United States",
    "currency": "USD"
  }
]
```

---

## 📊 **Portfolio Analytics API**

### Получить сводку портфеля
```http
GET /api/portfolios/{portfolio_id}/summary/
```

**Response:**
```json
{
  "portfolio_id": 1,
  "total_invested": 100000.00,
  "current_value": 125000.50,
  "total_profit": 25000.50,
  "profit_percentage": 25.0,
  "available_money": 5000.00,
  "active_stocks": 5,
  "sold_stocks": 2,
  "top_performers": [
    {
      "ticker": "NVDA",
      "profit_percentage": 45.2
    }
  ],
  "worst_performers": [
    {
      "ticker": "TSLA",
      "profit_percentage": -5.3
    }
  ]
}
```

### Получить историю портфеля
```http
GET /api/portfolios/{portfolio_id}/history/
```

**Response:**
```json
[
  {
    "date": "2024-01-15",
    "total_value": 100000.00,
    "total_profit": 0.00
  },
  {
    "date": "2024-01-16",
    "total_value": 102500.00,
    "total_profit": 2500.00
  }
]
```

---

## ⚠️ **Error Responses**

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "ticker": ["This field is required."],
    "quantity": ["Quantity must be greater than 0."]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Please log in to access this resource"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied",
  "message": "You don't have permission to access this portfolio"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "Portfolio with id 999 does not exist"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests to stock API. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred. Please try again later."
}
```

---

## 🔧 **Rate Limiting**

- **Stock API calls**: 5 requests per minute per user
- **Portfolio operations**: 100 requests per hour per user
- **User operations**: 50 requests per hour per user

---

## 📝 **Notes**

1. **Timestamps**: Все временные метки в формате ISO 8601 (UTC)
2. **Prices**: Все цены в USD с точностью до 2 знаков после запятой
3. **Quantities**: Количество акций должно быть целым числом
4. **Caching**: Цены акций кэшируются на 1 час
5. **FIFO**: Продажи акций используют принцип FIFO (First In, First Out)

---

## 🚀 **Getting Started**

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Настройте базу данных:**
```bash
python manage.py migrate
```

3. **Создайте суперпользователя:**
```bash
python manage.py createsuperuser
```

4. **Запустите сервер:**
```bash
python manage.py runserver
```

5. **Откройте API в браузере:**
```
http://localhost:8000/api/
```

---

## 📞 **Support**

Для вопросов и поддержки:
- Email: support@stockmarket.com
- GitHub Issues: [Project Repository](https://github.com/your-repo)
- Documentation: [Full Documentation](https://docs.stockmarket.com) 