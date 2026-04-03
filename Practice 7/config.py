def load_config():
    # Возвращает параметры подключения к PostgreSQL
    return {
        "host": "localhost",
        "database": "phonebook_db", # имя моей бд
        "user": "postgres",         # мой пользователь бд
        "password": "1234" # и мой пароль
    }

# Этот файл будет хранить настройки для подключения к базе данных