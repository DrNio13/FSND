import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources=r'/api/*')

    @app.route("/")
    def index():
        return jsonify({"status": True})

    @app.after_request
    def after_equest(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, DELETE, PUT, PATCH, OPTIONS")
        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify({
            "categories": formatted_categories
        })

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        categories = set()
        for question in questions:
            category_type = get_category_type(question.category)
            categories.add(category_type)

        return jsonify({
            "questions": formatted_questions[start:end],
            "total_questions": len(formatted_questions),
            "categories": list(categories),
            "current_category": None
        })

    def get_category_type(id):
        categories = Category.query.all()
        category_found = ''

        for category in categories:
            if (category.id == id):
                category_found = category.type
        return category_found

    @app.route('/questions/<int:id>', methods=["DELETE"])
    def delete_question_by_id(id):
        try:
            Question.query.filter(Question.id == id).delete()
            db.session.commit()

            return jsonify({
                "success": True
            })

        except:
            abort(500)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Sorry, we couldn't found what you are looking for"
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "It's not you, it's us"
        }), 500

    @app.errorhandler(422)
    def unable_to_process(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Your request is well-formed, however, due to semantic errors it is unable to be processed"
        }), 422

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "Oops...unauthorized error"
        }), 401

    @app.route('/questions', methods=["POST"])
    def create_question():
        try:
            body = request.get_json()

            question = body.get('question', None)
            answer = body.get('answer', None)
            category = body.get('category', None)
            difficulty = body.get('difficulty', None)

            question = Question(question=question, answer=answer,
                                category=category, difficulty=difficulty)
            question.insert()
            return jsonify({
                "success": True
            })
        except:
            abort(500)

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    return app
