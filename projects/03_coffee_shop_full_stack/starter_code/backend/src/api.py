import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()


# ROUTES

@app.route("/")
def get_status():
    return jsonify({
        "status": True
    })


@app.route("/drinks")
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks_formatted = [drink.long() for drink in drinks]
        # short() method contains a strange exception
        # string indices must be integers
        # i asked for help for the instructors and I couldn't find any solution
        return jsonify({
            "success": True,
            "drinks": drinks_formatted
        })
    except Exception as e:
        print(e)
        abort(500)


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": long_drinks
    })


@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    title = body.get("title")
    recipe = body.get("recipe")

    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink_title(jwt, id):
    if id == None or id <= 0:
        abort(404)

    body = request.get_json()
    title = body.get("title")

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if (drink is None):
        abort(404)

    drink.title = title
    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink_by_id(jwt, id):
    if id == None or id <= 0:
        abort(404)

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if (drink is None):
        abort(404)

    drink.delete()

    return jsonify({
        "success": True,
        "delete": drink.id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "It's not you, it's us"
    }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Sorry, we couldn't find what you were looking for"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(AuthError)
def handle_auth_error(exception):
    response = jsonify(exception.error)
    response.status_code = exception.status_code

    return response
