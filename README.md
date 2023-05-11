# Личный блог

## Описание
Личный блог с постами, покрытый тестами.

Unittest в Django: моделей, urls, views, шаблонов, контекста, форм.

Стек: Django, pytest, paginator, свои страницы ошибок, регистрация/авторизация.


## Как запустить проект

1. Kлонируем репозиторий
```
git clone 
```

2. Установим и активируем виртуальное окружение
```
python3 -m venv venv
```
```
. venv/bin/activate
```

3. Установим зависимости
```
pip install -r requirements.txt
```

4. Выполним миграции
```
python manage.py migrate
```

5. Запустим проект
```
python manage.py runserver
```
