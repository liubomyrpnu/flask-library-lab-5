Лабораторна робота 5 - Flask + Flask-RESTful + MongoDB + Swagger

Опис
REST API для бібліотеки книг, реалізоване на **Flask** з використанням **Flask-RESTful** та **MongoDB**. Документація API через **Flasgger**.

Виконані вимоги
- ✅ Flask + Flask-RESTful
- ✅ MongoDB (Docker)
- ✅ CRUD операції для сутності **Book**
- ✅ Пагінація (`limit` + `offset`)
- ✅ Swagger документація (`/apidocs/`)
- ✅ Запуск через Docker Compose

Структура проекту
flask-library-lab-5/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md

Як запустити
powershell
docker compose up -d --build
Swagger UI: http://127.0.0.1:5000/apidocs/

Основні ендпоінти
Метод,Ендпоінт,Опис
GET,/books,Список книг + пагінація
POST,/books,Додати книгу
GET,/books/{book_id},Отримати книгу за ID
DELETE,/books/{book_id},Видалити книгу







МетодЕндпоінтОписGET/booksСписок книг + пагінаціяPOST/booksДодати книгуGET/books/{book_id}Отримати книгу за IDDELETE/books/{book_id}Видалити книгу
