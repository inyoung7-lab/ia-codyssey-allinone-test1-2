"""기본 퀴즈 데이터의 개수, 구성, 직렬화와 독립성을 확인한다."""

import json
import unittest
from collections import Counter

from quiz import Quiz
from quiz_data import get_default_quizzes


class DefaultQuizDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quizzes = get_default_quizzes()

    def test_has_fifteen_quizzes_and_five_per_topic(self) -> None:
        self.assertEqual(len(self.quizzes), 15)
        topics = Counter(quiz.question.split("]", 1)[0] + "]" for quiz in self.quizzes)
        self.assertEqual(topics, {"[의료 IT]": 5, "[인공지능]": 5, "[디지털 헬스케어]": 5})

    def test_fields_are_complete_and_quiz_objects_are_valid(self) -> None:
        self.assertTrue(all(isinstance(quiz, Quiz) for quiz in self.quizzes))
        for quiz in self.quizzes:
            with self.subTest(question=quiz.question):
                self.assertTrue(quiz.question.strip())
                self.assertEqual(len(quiz.choices), 4)
                self.assertTrue(all(choice.strip() for choice in quiz.choices))
                self.assertIn(quiz.answer, range(1, 5))
                self.assertTrue(quiz.hint.strip())

    def test_answer_numbers_are_balanced(self) -> None:
        distribution = Counter(quiz.answer for quiz in self.quizzes)
        self.assertEqual(distribution, {1: 4, 2: 4, 3: 4, 4: 3})

    def test_questions_are_unique(self) -> None:
        questions = [quiz.question for quiz in self.quizzes]
        self.assertEqual(len(questions), len(set(questions)))

    def test_json_round_trip_for_all_quizzes(self) -> None:
        encoded = json.dumps([quiz.to_dict() for quiz in self.quizzes], ensure_ascii=False)
        decoded = json.loads(encoded)
        restored = [Quiz.from_dict(item) for item in decoded]
        self.assertEqual([quiz.to_dict() for quiz in restored], [quiz.to_dict() for quiz in self.quizzes])

    def test_each_call_returns_independent_objects(self) -> None:
        second_set = get_default_quizzes()
        self.assertEqual(len(second_set), len(self.quizzes))
        self.assertIsNot(self.quizzes[0], second_set[0])
        self.assertIsNot(self.quizzes[0].choices, second_set[0].choices)
        self.quizzes[0].choices[0] = "변경한 선택지"
        self.assertNotEqual(self.quizzes[0].choices[0], second_set[0].choices[0])


if __name__ == "__main__":
    unittest.main()
