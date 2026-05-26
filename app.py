from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger
from pymongo import MongoClient
from bson import ObjectId, errors as bson_errors
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Library API - Лабораторна 5",
        "description": "Flask + Flask-RESTful + MongoDB",
        "version": "1.0"
    }
})

api = Api(app)

client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo_admin:password@mongo_db:27017/books?authSource=admin"))
db = client.books
books_collection = db.books

book_parser = reqparse.RequestParser()
book_parser.add_argument("title", type=str, required=True)
book_parser.add_argument("author", type=str, required=True)
book_parser.add_argument("description", type=str)
book_parser.add_argument("status", type=str, choices=["available", "issued"], required=True)
book_parser.add_argument("year", type=int, required=True)

update_parser = reqparse.RequestParser()
update_parser.add_argument("title", type=str)
update_parser.add_argument("author", type=str)
update_parser.add_argument("description", type=str)
update_parser.add_argument("status", type=str, choices=["available", "issued"])
update_parser.add_argument("year", type=int)


def parse_object_id(book_id):
    try:
        return ObjectId(book_id)
    except (bson_errors.InvalidId, Exception):
        return None


class BookList(Resource):
    def get(self):
        """Отримати всі книги з пагінацією
        ---
        tags:
          - books
        parameters:
          - name: limit
            in: query
            type: integer
            default: 10
          - name: offset
            in: query
            type: integer
            default: 0
        responses:
          200:
            description: Список книг
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      _id:
                        type: string
                      title:
                        type: string
                      author:
                        type: string
                      description:
                        type: string
                      status:
                        type: string
                      year:
                        type: integer
                limit:
                  type: integer
                offset:
                  type: integer
                total:
                  type: integer
        """
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        books = list(books_collection.find().skip(offset).limit(limit))
        for book in books:
            book["_id"] = str(book["_id"])

        return {
            "items": books,
            "limit": limit,
            "offset": offset,
            "total": books_collection.count_documents({})
        }

    def post(self):
        """Додати нову книгу
        ---
        tags:
          - books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - title
                - author
                - status
                - year
              properties:
                title:
                  type: string
                  example: "Кобзар"
                author:
                  type: string
                  example: "Тарас Шевченко"
                description:
                  type: string
                  example: "Збірка поезій"
                status:
                  type: string
                  enum: ["available", "issued"]
                  example: "available"
                year:
                  type: integer
                  example: 1840
        responses:
          201:
            description: Книга успішно створена
            schema:
              type: object
              properties:
                id:
                  type: string
                message:
                  type: string
        """
        args = book_parser.parse_args()
        result = books_collection.insert_one(dict(args))
        return {"id": str(result.inserted_id), "message": "Book created"}, 201


class Book(Resource):
    def get(self, book_id):
        """Отримати книгу за ID
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Інформація про книгу
            schema:
              type: object
              properties:
                _id:
                  type: string
                title:
                  type: string
                author:
                  type: string
                description:
                  type: string
                status:
                  type: string
                year:
                  type: integer
          400:
            description: Невалідний ID
          404:
            description: Книга не знайдена
        """
        oid = parse_object_id(book_id)
        if not oid:
            return {"error": "Invalid ID format"}, 400

        book = books_collection.find_one({"_id": oid})
        if not book:
            return {"error": "Book not found"}, 404
        book["_id"] = str(book["_id"])
        return book

    def put(self, book_id):
        """Оновити книгу за ID
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            required: true
            type: string
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                  example: "Нова назва"
                author:
                  type: string
                  example: "Новий автор"
                description:
                  type: string
                status:
                  type: string
                  enum: ["available", "issued"]
                year:
                  type: integer
        responses:
          200:
            description: Книга успішно оновлена
            schema:
              type: object
              properties:
                _id:
                  type: string
                title:
                  type: string
                author:
                  type: string
                description:
                  type: string
                status:
                  type: string
                year:
                  type: integer
          400:
            description: Невалідний ID або порожнє тіло
          404:
            description: Книга не знайдена
        """
        oid = parse_object_id(book_id)
        if not oid:
            return {"error": "Invalid ID format"}, 400

        args = update_parser.parse_args()
        update_data = {k: v for k, v in args.items() if v is not None}

        if not update_data:
            return {"error": "No fields to update"}, 400

        result = books_collection.update_one({"_id": oid}, {"$set": update_data})
        if result.matched_count == 0:
            return {"error": "Book not found"}, 404

        book = books_collection.find_one({"_id": oid})
        book["_id"] = str(book["_id"])
        return book

    def delete(self, book_id):
        """Видалити книгу
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Книга видалена
            schema:
              type: object
              properties:
                message:
                  type: string
          400:
            description: Невалідний ID
          404:
            description: Книга не знайдена
        """
        oid = parse_object_id(book_id)
        if not oid:
            return {"error": "Invalid ID format"}, 400

        result = books_collection.delete_one({"_id": oid})
        if result.deleted_count == 0:
            return {"error": "Book not found"}, 404
        return {"message": "Book deleted"}, 200


api.add_resource(BookList, "/books")
api.add_resource(Book, "/books/<string:book_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
