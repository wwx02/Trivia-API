import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import choice

from models import setup_db, Question, Category, db
from sqlalchemy.exc import NoResultFound

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        categories = {str(cat.id): cat.type for cat in categories}
        return jsonify({
            'categories': categories,
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        questions = Question.query.order_by(Question.id).all()
        questions = [cat.format() for cat in questions]

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        curr = questions[start:end]
        if len(curr) == 0:
            abort(404)

        categories = Category.query.all()
        categories = {str(cat.id): cat.type for cat in categories}
        cat = Category.query.filter_by(id=curr[0]["category"]).one()

        return jsonify({
            'questions': curr,
            'totalQuestions': len(questions),
            'categories': categories,
            'currentCategory': cat.type
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
            db.session.delete(question)
            db.session.commit()
        except:
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            "success": True,
            "question_id": question_id
        })

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.json

        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)

        if question:
            try:
                question = Question(question=question,
                                    answer=answer,
                                    difficulty=difficulty,
                                    category=category)
                db.session.add(question)
                db.session.commit()
            except:
                abort(422)
            finally:
                db.session.close()
                return jsonify({
                    "success": True,
                })
        else:
            return search_question()

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def search_question():
        body = request.json
        search = body.get("searchTerm", None)

        if search:
            questions = Question.query.filter(Question.question.ilike("%{}%".format(search)))
            questions = [q.format() for q in questions]
            cat = Category.query.filter_by(id=questions[0]["category"]).one()

            return jsonify({
                "questions": questions,
                "totalQuestions": len(questions),
                "currentCategory": cat.type
            })
        else:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        cat = Category.query.get(category_id)
        if cat is None:
            abort(404)
        cat = cat.type
        questions = Question.query.filter_by(category=category_id).all()
        questions = [q.format() for q in questions]

        return jsonify({"questions": questions,
                        "totalQuestions": len(questions),
                        "currentCategory": cat})

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=['POST'])
    def play():
        body = request.json

        category = body.get("quiz_category", None)
        questions = body.get("previous_questions", [])

        if category["id"]==0:
            quest=Question.query.all()
        else:
            try:
                quest = Question.query.filter_by(category=category["id"]).all()
            except:
                abort(404)

        quest = [q.format() for q in quest]
        quest = [q for q in quest if q["id"] not in questions]
        quest = choice(quest)

        return jsonify({
            "quiz_category": category,
            "question": quest,
            "previous_questions": questions
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False,
                     "error": 404,
                     "message": "Error: not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
                     "error": 422,
                     "message": "Error: unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False,
                     "error": 400,
                     "message": "Error: bad request"}),
            400,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({"success": False,
                     "error": 500,
                     "message": "Error: server error"}),
            500,
        )


    @app.errorhandler(405)
    def method_error(error):
        return (
            jsonify({"success": False,
                     "error": 405,
                     "message": "Error: method unallowed"}),
            405,
        )

    return app
