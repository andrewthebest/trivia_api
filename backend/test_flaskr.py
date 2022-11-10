from operator import and_, or_
import os
from unicodedata import category
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # Default question used to test create new question functionnality
        self.new_question = {"answer": "Joe Biden", "category": 4, "difficulty": 1, "question": "Who is the actual president of United States?"}
        # Default category used to test create new category functionnality
        self.new_category = {"type": "Literature"}
         # Search term used to test search functionnality
        self.searchTerm = {"search_term": "Who"}
        # Inputs used to test quiz functionnality
        self.quizInputs = {
            'previous_questions': [],
            'quiz_category': {'type': 'History', 'id': 4}
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test endpoint to get all categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])

    # Test if request to get categories is valid
    def test_422_get_categories_with_params(self):
        res = self.client().post("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "You request is not valid")
    
    # Test endpoint to get all questions
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["categories"])

    # Test if page parameter is not valid
    def test_404_if_the_page_is_not_valid(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")
    
    # Test endpoint to delete one question
    def test_delete_question(self):
        res = self.client().delete("/questions/24")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 24).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question_deleted"], 24)
        self.assertTrue(data["total_questions"])

    # Test if question ID does not exist when trying to delete it
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/3000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    # Test endpoint to create new question
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question_created"])

    # Test if question's creation is not allowed
    def test_405_if_new_question_creation_not_allowed(self):
        res = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method not allowed")
    
    # Test endpoint to create new category
    def test_create_new_category(self):
        res = self.client().post("/categories", json=self.new_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["category_created"])

    # Test if category's creation is unprocessable
    def test_405_if_new_category_creation_is_unprocessable(self):
        res = self.client().post("/categories", json={"mine": "yesterday"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")
        
    # Test endpoint to get questions based on search term
    def test_get_questions_based_on_search_term(self):
        res = self.client().post("/questions", json=self.searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    # Test if search is not allowed
    def test_422_if_questions_based_on_search_term_not_allowed(self):
        res = self.client().post("/questions/2", json={"search_term": "yesterday"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method not allowed")
    
    # Test endpoint to get questions for quiz
    def test_get_questions_to_play_the_quiz(self):
        res = self.client().post("/quizzes", json=self.quizInputs)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])

    # Test if getting question is unprocessable
    def test_422_if_quizzes_questions_do_not_exists(self):
        res = self.client().post("/quizzes", json={
            'previous_questions': [1, 4, 20, 15],
            'quiz_category': 'Current category'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")
    
    # Test endpoint to get questions based on category
    def test_get_questions_based_on_category(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["current_category"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])

    # Test if category does not exist
    def test_404_if_category_does_not_exist_when_retrieve_questions(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()