# Password Reset Setup Guide

## Overview

Система сброса пароля позволяет пользователям восстанавливать доступ к аккаунту, если они забыли пароль. Система работает через email и использует безопасные токены.

## Features

- ✅ Запрос сброса пароля по email
- ✅ Безопасные токены с ограниченным временем действия (1 час)
- ✅ Красивые и адаптивные формы
- ✅ Валидация email и паролей
- ✅ Защита от перебора (CSRF protection)

## How It Works

1. **Запрос сброса**: Пользователь вводит email на странице `/users/password-reset/`
2. **Отправка email**: Система генерирует уникальный токен и отправляет ссылку на email
3. **Подтверждение**: Пользователь переходит по ссылке и устанавливает новый пароль
4. **Вход**: Пользователь может войти с новым паролем

## Email Configuration

### Development (Console Backend)

Для разработки emails выводятся в консоль Django:

```bash
# В .env файле
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (SMTP Backend)

Для продакшена настройте SMTP:

```bash
# В .env файле
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Gmail Setup

1. Включите двухфакторную аутентификацию
2. Создайте пароль приложения
3. Используйте пароль приложения в `EMAIL_HOST_PASSWORD`

### Other Email Providers

- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **SendGrid**: `smtp.sendgrid.net:587`

## Security Features

- **Токены**: Используются Django's `default_token_generator`
- **Время жизни**: Токены действительны 1 час
- **CSRF защита**: Все формы защищены от CSRF атак
- **Валидация**: Проверка существования email без раскрытия информации
- **Безопасные URL**: Используется base64 кодирование для ID пользователя

## Usage

### For Users

1. Перейдите на страницу входа
2. Нажмите "Forgot your password?"
3. Введите email
4. Проверьте email и перейдите по ссылке
5. Установите новый пароль

### For Developers

```python
# Проверка работы в Django shell
python manage.py shell

from django.contrib.auth import get_user_model
from apps.users.views import password_reset

User = get_user_model()
user = User.objects.get(email='test@example.com')
```

## Templates

- `password_reset_form.html` - Форма запроса сброса
- `password_reset_confirm.html` - Форма установки нового пароля
- `password_reset_email.html` - Шаблон email

## URLs

- `/users/password-reset/` - Запрос сброса пароля
- `/users/reset/<uidb64>/<token>/` - Подтверждение сброса

## Testing

1. Создайте пользователя
2. Перейдите на страницу сброса пароля
3. Введите email пользователя
4. Проверьте консоль Django (в development режиме)
5. Скопируйте ссылку из консоли
6. Перейдите по ссылке и установите новый пароль

## Troubleshooting

### Email не отправляется
- Проверьте настройки SMTP
- Убедитесь, что `EMAIL_HOST_PASSWORD` правильный
- Проверьте логи Django

### Токен недействителен
- Токены действительны только 1 час
- Пользователь должен быть активен
- Проверьте правильность URL

### Ошибки валидации
- Пароль должен соответствовать требованиям Django
- Email должен существовать в базе данных

## Production Checklist

- [ ] Настроить SMTP backend
- [ ] Использовать HTTPS
- [ ] Настроить `DEFAULT_FROM_EMAIL`
- [ ] Протестировать на реальном email
- [ ] Настроить мониторинг ошибок email
- [ ] Добавить rate limiting для запросов сброса 