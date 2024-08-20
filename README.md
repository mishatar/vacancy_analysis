## В корне проекта создаем файл .env и добавляем туда:

 - SPREADSHEET_ID = <уникальный идентификатор вашей таблицы в Google Sheets>
 - RANGE_NAME = <название листа в Google Sheets>
 - APP_HOST_PORT = 8005
 - POSTGRES_DB_USER = <имя пользователя бд>
 - POSTGRES_DB_PASSWORD = <пароль от бд>
 - POSTGRES_DB_HOST_PORT = 5432
 - POSTGRES_DB_HOST = db
 - POSTGRES_DB_NAME = <имя бд>

## Также добавить в /app файл credentials.json с конфиогом Google Sheets API
