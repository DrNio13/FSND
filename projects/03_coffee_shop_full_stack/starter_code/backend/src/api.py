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


@app.route("/")
def get_status():
    return jsonify({
        "status": True
    })

# db_drop_and_create_all()


# ROUTES


@app.route("/drinks")
def get_drinks():
    try:
        drinks = Drink.query.all()
        short_drinks = [drink.short() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": short_drinks
        })
    except Exception as e:
        print(e)
        abort(500)


@app.route("/drinks-detail")
@requires_auth('get:drink-details')
def get_drinks_detail(jwt):
    try:
        print(jwt)
        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": long_drinks
        })
    except Exception as e:
        print(e)
        abort(500)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


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


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
