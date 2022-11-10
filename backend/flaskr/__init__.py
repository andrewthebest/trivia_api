from cgi import test
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Function used to paginate questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PUT, DELETE, OPTIONS')
        return response
    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        all_categories = Category.query.order_by(Category.id).all()

        # Test if request returned an empty result
        # If not then format categories
        if len(all_categories) == 0:
            categories = {}
        else:
            categories = {cat.id: cat.type for cat in all_categories}

        return jsonify({
            'categories': categories
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        all_categories = Category.query.order_by(Category.id).all()
        all_questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, all_questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'questions': current_questions,
            'total_questions': len(all_questions),
            'categories': {cat.id: cat.type for cat in all_categories},
            # 'currentCategory' : None
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_one_question(question_id):
        try:
            question = Question.query.get_or_404(question_id)
            question.delete()
            all_questions = Question.query.all()

            return jsonify({
                "question_deleted": question_id,
                "total_questions": len(all_questions)
            })

        except BaseException:
            abort(422)
    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route("/questions", methods=["POST"])
    def create_new_question_and_search_for_existing_questions():
        body = request.get_json()

        new_answer = body.get("answer", None)
        new_question = body.get("question", None)
        new_difficulty = body.get("difficulty", None)
        new_category = body.get("category", None)
        search_term = body.get("search_term", None)

        try:
            # Test if parameters list contains search_term in order to make
            # search request
            if search_term:
                questions_based_on_search = Question.query.filter(
                    Question.question.ilike("%{}%".format(search_term))).all()

                if len(questions_based_on_search) == 0:
                    abort(422)
                current_books = paginate_questions(
                    request, questions_based_on_search)

                return jsonify({
                    "questions": current_books,
                    "total_questions": len(questions_based_on_search),
                })
            # If parameters list does not contains search_term, then proceed to
            # creation of new question
            else:
                question = Question(
                    answer=new_answer,
                    question=new_question,
                    difficulty=new_difficulty,
                    category=new_category)
                if new_answer and new_question:
                    question.insert()
                else:
                    abort(422)

                # all_questions = Question.query.order_by(Question.id).all()
                # current_questions = paginate_questions(request, all_questions)

                return jsonify(
                    {
                        "question_created": question.format(),
                        # "questions": current_questions,
                        # "total_questions": len(all_questions),
                    }
                )

        except BaseException:
            abort(422)

    '''
    @TODO: (bonus)
    Create an endpoint to POST a new category,
    which will require the type of category text.
    '''
    @app.route("/categories", methods=["POST"])
    def create_new_category():
        body = request.get_json()
        new_type = body.get("type", None)

        try:
            if new_type:
                category = Category(type=new_type)
                category.insert()
            else:
                abort(422)

            return jsonify(
                {
                    "category_created": category.format()
                }
            )

        except BaseException:
            abort(422)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_based_on_category(category_id):

        try:
            # Trying to get questions based on category in parameter
            questions_from_category = Question.query.join(
                Category,
                Category.id == Question.category) .with_entities(
                Question.id,
                Question.answer,
                Question.question,
                Question.difficulty,
                Question.category) .filter(
                Question.category == category_id).all()

            questions_from_category_formatted = []
            # Format questions
            for question in questions_from_category:
                questions_from_category_formatted.append({
                    'id': question.id,
                    'question': question.question,
                    'answer': question.answer,
                    'category': question.category,
                    'difficulty': question.difficulty
                })
            current_category = Category.query.get_or_404(category_id)

            return jsonify(
                {
                    "questions": questions_from_category_formatted,
                    "total_questions": len(questions_from_category),
                    "current_category": current_category.format(),
                }
            )

        except BaseException:
            abort(404)

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
    @app.route("/quizzes", methods=["POST"])
    def get_questions_to_play_the_quiz():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        try:
            # Test if there is no category specified
            if quiz_category['id'] == 0:
                all_categories_id = []
                all_categories = Category.query.all()
                for category in all_categories:
                    all_categories_id.append(category.id)

                # Getting random category to launch quiz
                quiz_category_id = random.choice(all_categories_id)
            else:
                quiz_category_id = quiz_category['id']

            query = Category.query.filter(
                Category.id == quiz_category_id).one_or_none()

            # If no result found, abort with error 422
            if not query:
                abort(422)

            quiz_category_id = query.id
            all_questions_id_for_quiz_category = Question.query.join(
                Category, Category.id == Question.category) .with_entities(
                Question.id) .filter(
                Question.category == quiz_category_id).all()

            all_questions_id_for_quiz_category_formatted = []
            for question in all_questions_id_for_quiz_category:
                # Chechs if question has already been asked to the user
                if question.id not in previous_questions:
                    all_questions_id_for_quiz_category_formatted.append(
                        question.id)

            if len(all_questions_id_for_quiz_category_formatted) == 0:
                current_question = None
            else:
                current_question_id = random.choice(
                    all_questions_id_for_quiz_category_formatted)
                current_question = Question.query.get(
                    current_question_id).format()

            return jsonify(
                {
                    "question": current_question,
                }
            )

        except BaseException:
            abort(422)

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({
            "success": False,
            "error": 400,
            "message": "You request is not valid"
        }), 400)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422)

    @app.errorhandler(405)
    def not_allowed(error):
        return (jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405)

    @app.errorhandler(500)
    def internal_server_eror(error):
        return (jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500)

    return app
