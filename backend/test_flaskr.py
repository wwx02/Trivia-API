import os
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
        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format('postgres','0000','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["currentCategory"])

    def test_404_get_questions(self):
        res = self.client().get("/questions?page=500")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Error: not found")

    def test_delete_question(self):
        res = self.client().delete("/questions/4")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question_id"], 4)

    def test_404_delete_question(self):
        res = self.client().delete("/questions/200")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Error: not found")

    def test_add_question(self):
        res = self.client().post("/questions", json={"question": "This is a question",
                                                     "answer": "This is an answer",
                                                     "difficulty": 10,
                                                     "category": 3
                                                     })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_question(self):
        res = self.client().post("/questions", json={"searchTerm": "title"
                                                     })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["currentCategory"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))

    def test_quiz(self):
        res = self.client().post("/quizzes", json={"quiz_category": "Science",
                                                "previous_questions": [4,6,2]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])

    def test_404_quiz(self):
        res = self.client().post("/quizzes", json={"quiz_category": "devlg",
                                                "previous_questions": [5, 12]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Error: not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()