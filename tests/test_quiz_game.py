"""QuizGame 출제, 입력 검증, 결과 계산 테스트."""

import contextlib
import io
import unittest
from unittest.mock import patch

from quiz_data import get_default_quizzes
from quiz_game import QuizGame


class QuizGameTests(unittest.TestCase):
    def test_plays_five_unique_randomly_sampled_questions_and_scores(self) -> None:
        quizzes = get_default_quizzes()
        answers = iter(["5", *(str(quiz.answer) for quiz in quizzes[:5])])
        messages: list[str] = []
        game = QuizGame(quizzes, lambda _: next(answers), messages.append)
        with patch("quiz_game.random.sample", return_value=quizzes[:5]) as sample, contextlib.redirect_stdout(io.StringIO()) as displayed:
            result = game.play()
        sample.assert_called_once_with(quizzes, 5)
        self.assertEqual(result, {"correct": 5, "incorrect": 0, "score": 100, "total": 5})
        self.assertEqual(sum("/5" in message and message.split("/")[-1] == "5" for message in messages), 5)
        self.assertTrue(all(choice in displayed.getvalue() for quiz in quizzes[:5] for choice in quiz.choices))

    def test_retries_invalid_question_count_and_answers(self) -> None:
        quizzes = get_default_quizzes()
        answers = iter(["6", "x", "5", "0", str(quizzes[0].answer), *(["1"] * 4)])
        messages: list[str] = []
        with patch("quiz_game.random.sample", return_value=quizzes[:5]):
            result = QuizGame(quizzes, lambda _: next(answers), messages.append).play()
        self.assertEqual(result["total"], 5)
        self.assertTrue(any("5, 10, 15" in message for message in messages))
        self.assertTrue(any("숫자를 입력" in message for message in messages))

    def test_fifteen_questions_and_zero_score(self) -> None:
        quizzes = get_default_quizzes()
        answers = iter(["15", *(["1"] * 15)])
        messages: list[str] = []
        with patch("quiz_game.random.sample", return_value=quizzes):
            result = QuizGame(quizzes, lambda _: next(answers), messages.append).play()
        expected = sum(quiz.answer == 1 for quiz in quizzes)
        self.assertEqual(result["correct"], expected)
        self.assertEqual(result["incorrect"], 15 - expected)
        self.assertEqual(result["score"], round(expected * 100 / 15))

    def test_ten_question_mode(self) -> None:
        quizzes = get_default_quizzes()
        answers = iter(["10", *(str(quiz.answer) for quiz in quizzes[:10])])
        with patch("quiz_game.random.sample", return_value=quizzes[:10]), contextlib.redirect_stdout(io.StringIO()):
            result = QuizGame(quizzes, lambda _: next(answers), lambda _: None).play()
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["score"], 100)

    def test_each_hint_request_deducts_ten_points(self) -> None:
        quizzes = get_default_quizzes()
        answers = iter(["5", "h", str(quizzes[0].answer), *(str(q.answer) for q in quizzes[1:5])])
        messages: list[str] = []
        with patch("quiz_game.random.sample", return_value=quizzes[:5]), contextlib.redirect_stdout(io.StringIO()):
            result = QuizGame(quizzes, lambda _: next(answers), messages.append).play()
        self.assertEqual(result["correct"], 5)
        self.assertEqual(result["score"], 90)
        self.assertTrue(any("힌트:" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
