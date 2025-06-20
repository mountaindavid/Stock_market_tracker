# CI/CD Setup Guide - Подробное руководство

## 🎯 Что такое CI/CD?

### **CI (Continuous Integration) - Непрерывная интеграция**
- **Цель**: Автоматическое тестирование кода при каждом изменении
- **Когда**: При каждом push, pull request
- **Что делает**: Запускает тесты, проверяет качество кода, собирает отчеты

### **CD (Continuous Deployment) - Непрерывное развертывание**
- **Цель**: Автоматическое развертывание приложения
- **Когда**: После успешного прохождения тестов
- **Что делает**: Разворачивает приложение на сервер

## 📁 Структура CI/CD файлов

```
.github/
└── workflows/
    ├── ci.yml          # Основной CI workflow (тестирование)
    ├── test.yml        # Расширенное тестирование
    └── deploy.yml      # Развертывание (опционально)
pytest.ini             # Конфигурация pytest
.flake8                # Конфигурация проверки качества кода
requirements.txt       # Зависимости включая инструменты тестирования
```

## 🔧 Как работают GitHub Actions

### **1. Триггеры (когда запускается)**
```yaml
on:
  push:
    branches: [ main ]           # При push в main ветку
  pull_request:
    branches: [ main ]           # При создании PR в main
```

### **2. Jobs (задачи)**
```yaml
jobs:
  test:                         # Название задачи
    runs-on: ubuntu-latest      # На какой ОС запускать
    steps:                      # Шаги выполнения
      - name: Step 1            # Название шага
        run: command            # Команда для выполнения
```

### **3. Services (сервисы)**
```yaml
services:
  postgres:                     # Запуск PostgreSQL для тестов
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres
```

## 🧪 Подробный разбор CI workflow (ci.yml)

### **Шаг 1: Checkout code**
```yaml
- name: Checkout code
  uses: actions/checkout@v4
```
**Что делает**: Клонирует ваш репозиторий в виртуальную машину GitHub

### **Шаг 2: Setup Python**
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: "3.11"
    cache: 'pip'
```
**Что делает**: 
- Устанавливает Python 3.11
- Кэширует pip для ускорения установки зависимостей

### **Шаг 3: Install dependencies**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pytest pytest-django coverage flake8
```
**Что делает**:
- Обновляет pip
- Устанавливает зависимости из requirements.txt
- Устанавливает инструменты тестирования

### **Шаг 4: Setup environment**
```yaml
- name: Setup environment
  run: |
    echo "DEBUG=True" >> $GITHUB_ENV
    echo "SECRET_KEY=test-secret-key-for-ci" >> $GITHUB_ENV
    echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db" >> $GITHUB_ENV
```
**Что делает**: Создает переменные окружения для тестов

### **Шаг 5: Wait for database**
```yaml
- name: Wait for database
  run: |
    while ! pg_isready -h localhost -p 5432 -U postgres; do
      echo "Waiting for database..."
      sleep 2
    done
```
**Что делает**: Ждет, пока PostgreSQL будет готов к подключению

### **Шаг 6: Run migrations**
```yaml
- name: Run migrations
  run: |
    python manage.py migrate
```
**Что делает**: Применяет миграции к тестовой базе данных

### **Шаг 7: Run linting**
```yaml
- name: Run linting
  run: |
    flake8 apps/ stock_market/ --max-line-length=120 --ignore=E501,W503
```
**Что делает**: Проверяет качество кода (стиль, ошибки)

### **Шаг 8: Run tests**
```yaml
- name: Run tests
  run: |
    python manage.py test --verbosity=2 --parallel
```
**Что делает**: Запускает все тесты Django

### **Шаг 9: Generate coverage report**
```yaml
- name: Generate coverage report
  run: |
    coverage run --source='.' manage.py test
    coverage report
    coverage xml
```
**Что делает**: 
- Измеряет покрытие кода тестами
- Генерирует отчеты

## 🚀 Подробный разбор Deploy workflow (deploy.yml)

### **Условия запуска**
```yaml
concurrency:
  group: production
  cancel-in-progress: false
```
**Что делает**: Гарантирует, что только одно развертывание выполняется одновременно

### **Зависимости**
```yaml
needs: test
```
**Что делает**: Запускает развертывание только после успешного прохождения тестов

### **Шаг 1-4: Подготовка**
- Checkout code
- Setup Python
- Install dependencies
- Collect static files

### **Шаг 5: Build Docker image**
```yaml
- name: Build Docker image
  run: |
    docker build -t stock-market-app:${{ github.sha }} .
    docker tag stock-market-app:${{ github.sha }} stock-market-app:latest
```
**Что делает**: Создает Docker образ с тегом коммита

### **Шаг 6: Deploy to server**
```yaml
- name: Deploy to server
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.HOST }}
    username: ${{ secrets.USERNAME }}
    key: ${{ secrets.SSH_KEY }}
```
**Что делает**: Подключается к серверу и выполняет команды развертывания

## 🔐 GitHub Secrets (секреты)

Для работы deploy workflow нужно добавить секреты в настройках репозитория:

1. Перейдите в **Settings** → **Secrets and variables** → **Actions**
2. Добавьте следующие секреты:
   - `HOST` - IP адрес вашего сервера
   - `USERNAME` - имя пользователя на сервере
   - `SSH_KEY` - приватный SSH ключ
   - `PORT` - SSH порт (обычно 22)

## 📊 Инструменты тестирования

### **1. pytest**
```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=apps

# Запуск только быстрых тестов
pytest -m "not slow"
```

### **2. flake8**
```bash
# Проверка качества кода
flake8 apps/ stock_market/

# Проверка с игнорированием ошибок
flake8 --ignore=E501,W503
```

### **3. coverage**
```bash
# Измерение покрытия
coverage run --source='.' manage.py test
coverage report
coverage html  # Создает HTML отчет
```

### **4. safety**
```bash
# Проверка безопасности зависимостей
safety check
```

## 🎯 Практические примеры

### **Пример 1: Добавление нового теста**
1. Создайте тест в `apps/portfolios/tests.py`
2. Запустите локально: `python manage.py test`
3. Сделайте commit и push
4. GitHub Actions автоматически запустит тесты

### **Пример 2: Проверка качества кода**
```bash
# Локально
flake8 apps/ stock_market/
black apps/ stock_market/  # Форматирование кода
isort apps/ stock_market/  # Сортировка импортов
```

### **Пример 3: Отладка CI/CD**
1. Перейдите в **Actions** в GitHub
2. Выберите workflow
3. Посмотрите логи выполнения
4. Найдите ошибки и исправьте

## 🔧 Настройка локальной разработки

### **Установка инструментов**
```bash
pip install -r requirements.txt
```

### **Запуск тестов локально**
```bash
# Все тесты
python manage.py test

# С покрытием
coverage run --source='.' manage.py test
coverage report

# Качество кода
flake8 apps/ stock_market/
```

### **Pre-commit hooks (опционально)**
Создайте `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
```

## 📈 Мониторинг и метрики

### **GitHub Actions Insights**
- Время выполнения workflow
- Успешность тестов
- Покрытие кода

### **Codecov (опционально)**
1. Зарегистрируйтесь на [codecov.io](https://codecov.io)
2. Подключите репозиторий
3. Получайте отчеты о покрытии кода

## 🚨 Troubleshooting

### **Проблема: Тесты падают**
1. Проверьте логи в GitHub Actions
2. Запустите тесты локально
3. Исправьте ошибки
4. Сделайте новый commit

### **Проблема: Медленные тесты**
1. Используйте параллельное выполнение: `--parallel`
2. Добавьте маркеры: `@pytest.mark.slow`
3. Кэшируйте зависимости

### **Проблема: Развертывание не работает**
1. Проверьте SSH ключи
2. Убедитесь, что сервер доступен
3. Проверьте права доступа

## 📚 Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Flake8 Documentation](https://flake8.pycqa.org/)

## 🎉 Результат

После настройки CI/CD вы получите:
- ✅ Автоматическое тестирование при каждом изменении
- ✅ Проверку качества кода
- ✅ Отчеты о покрытии
- ✅ Автоматическое развертывание (опционально)
- ✅ Уведомления об ошибках
- ✅ История выполнения всех проверок 