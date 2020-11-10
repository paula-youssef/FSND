import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, check_permissions

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    DrinkShort =[]
    for drink in drinks:
        DrinkShort.append(Drink.short(drink))
    return jsonify({
        'success': True,
        'drinks': DrinkShort
    })
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth
def get_drinks_detail(payload):
    check_permissions("get:drinks-detail", payload)
    drinks = Drink.query.all()
    DrinkShort =[]
    for drink in drinks:
        DrinkShort.append(Drink.long(drink))
    return jsonify({
        'success': True,
        'drinks': DrinkShort
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth
def post_drink(payload):
    body = request.get_json()
    check_permissions("post:drinks", payload)

    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        DrinkObj = Drink()
        DrinkObj.title = title
        DrinkObj.recipe = str(recipe)
        returnedDrinks=[]
        returnedDrinks.append(DrinkObj.title)
        DrinkObj.insert()
        return jsonify({
            'success': True,
            'drinks': returnedDrinks
        })
    except:
       abort(422)

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
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth
def update_drink(payload, drink_id):
    check_permissions("patch:drinks", payload)
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
      abort(404)

    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink.title = title 
        drink.recipe = str(recipe)
        drink.update()
        returnedDrinks=[]
        return jsonify({
            'success': True,
            'drinks': returnedDrinks
        })
    except:
       abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<int:id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth
def delete_drinks(payload, drink_id):
    check_permissions("delete:drinks", payload)
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
      abort(404)

    drink.delete()
    
    return jsonify({
      'success': True,
      'delete':drink_id
    })

## Error Handling
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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 401,
      "message": "Unauthorized"
      }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

@app.errorhandler(500)
def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal Server Error"
      }), 500

@app.errorhandler(403)
def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 403,
      "message": "Permission not found"
      }), 403
  
