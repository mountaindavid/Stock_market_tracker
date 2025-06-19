# Security Guidelines

## Environment Variables

Все чувствительные данные хранятся в файле `.env`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False  # В продакшене
ALLOWED_HOSTS=your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stock_db

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your-api-key-here

# Cache
REDIS_URL=redis://127.0.0.1:6379/1

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

## Production Security Checklist

### 1. Environment Variables
- [ ] Установить `DEBUG=False`
- [ ] Использовать сильный `SECRET_KEY`
- [ ] Настроить `ALLOWED_HOSTS`
- [ ] Использовать HTTPS в `CSRF_TRUSTED_ORIGINS`

### 2. Database Security
- [ ] Использовать отдельного пользователя БД
- [ ] Ограничить права доступа
- [ ] Регулярно делать бэкапы
- [ ] Использовать SSL соединение

### 3. API Security
- [ ] Ограничить API ключи
- [ ] Мониторить использование API
- [ ] Использовать rate limiting

### 4. HTTPS
- [ ] Установить SSL сертификат
- [ ] Включить `SECURE_SSL_REDIRECT = True`
- [ ] Установить `SESSION_COOKIE_SECURE = True`

### 5. Monitoring
- [ ] Настроить логирование
- [ ] Мониторить ошибки
- [ ] Настроить алерты

## Development Security

### 1. Never commit .env files
```bash
# .gitignore
.env
.env.local
.env.production
```

### 2. Use strong passwords
- Минимум 8 символов
- Комбинация букв, цифр, символов

### 3. Regular updates
- Обновлять Django
- Обновлять зависимости
- Проверять уязвимости

## API Rate Limiting

Alpha Vantage API имеет лимиты:
- Free tier: 5 requests per minute
- Premium: 500+ requests per minute

Используйте кэширование для оптимизации.

## Logging

Логи сохраняются в папке `logs/`:
- `django.log` - общие логи Django
- Настроены уровни INFO и DEBUG
- Ротация логов включена 