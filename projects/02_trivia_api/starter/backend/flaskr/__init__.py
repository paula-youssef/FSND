import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)

  '''
  @Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  '''
  @Done: Use the after_request decorator to set Access-Control-Allow
  '''

  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @Done: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.with_entities(Category.type).order_by(Category.id).all()
    
    return jsonify({
      'success': True,
      'categories': categories,
      'total_categories': len(categories)
    })


  '''
  @Done: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def get_questions():
      page = request.args.get('page', 1 ,type = int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = Question.query.order_by(Question.id).all()
      categories = Category.query.with_entities(Category.type).order_by(Category.id).all()
      formatted_questions =[]
      for question in questions:
        formatted_questions.append(Question.format(question))
       
      return jsonify({
          'success': True,
          'questions': formatted_questions[start:end],
          'total_questions': len(questions),
          'categories': categories
      })

  '''
  @Done: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question is None:
      abort(404)

    question.delete()
    
    return jsonify({
      'success': True,
      'deleted_question_id':question_id
    })

  '''
  @Done in one method search_post_questions: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @Done: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions',methods=['POST'])
  def search_post_questions():
      body = request.get_json()

      search = body.get('searchTerm', None)
      question = body.get('question', None)
      answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)
      try:
        if search:
          questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()
          formatted_questions =[]
          for question in questions:
            formatted_questions.append(Question.format(question))
          return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions)
          })
        elif question is not None and answer is not None and difficulty is not None and category is not None:
          category = str(int(category)+1)
          questionObj = Question(question = question, answer = answer, category = category, difficulty = difficulty )
          questionObj.insert()
          questions = Question.query.order_by(Question.id).all()
          formatted_questions =[]
          for question in questions:
            formatted_questions.append(Question.format(question))
          return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions)
          })
        else:
          abort(400)
      except:
       abort(422)
  '''
  @Done: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_category_questions(category_id):
      page = request.args.get('page', 1 ,type = int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = Question.query.filter(Question.category == str(category_id+1)).order_by(Question.id).all()
      categories = Category.query.with_entities(Category.type).order_by(Category.id).all()
      formatted_questions =[]
      for question in questions:
        formatted_questions.append(Question.format(question))
       
      return jsonify({
          'success': True,
          'questions': formatted_questions[start:end],
          'total_questions': len(questions),
          'categories': categories
      })
  '''
  @Done: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quizzes():
      body = request.get_json()

      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)
      try:
        if quiz_category['type'] =='click':
          questions = Question.query.order_by(Question.id).all()
          if len(previous_questions) != len(questions):
            n = random.randint(0,len(questions)-1)
            while questions[n].id in previous_questions :
                n = random.randint(1,len(questions)-1)
            formatted_question = Question.format(questions[n])
            return jsonify({
              'success': True,
              'question': formatted_question,
              'total_questions': len(questions)
            })
          else:
            return jsonify({
              'success': True
            })
        else:
          category_id = str(int(quiz_category['id'])+1)
          questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
          if len(previous_questions) != len(questions):
            n = random.randint(0,len(questions)-1)
            while questions[n].id in previous_questions :
                n = random.randint(1,len(questions)-1)
            formatted_question = Question.format(questions[n])
            return jsonify({
              'success': True,
              'question': formatted_question,
              'total_questions': len(questions)
            })
          else:
            return jsonify({
              'success': True
            })
      except:
       abort(422)
  '''
  @Done: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

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
  
  return app

    