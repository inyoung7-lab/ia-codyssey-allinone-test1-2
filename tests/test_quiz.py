"""Quiz 클래스의 데이터 검증과 동작을 확인한다."""

import contextlib
import io
import unittest

from quiz import Quiz


class QuizTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quiz = Quiz("의료 AI란 무엇인가요?", ["선택 A", "선택 B", "선택 C", "선택 D"], 2, "힌트 내용")

    def test_create_and_attributes(self) -> None:
        self.assertEqual(self.quiz.question, "의료 AI란 무엇인가요?")
        self.assertEqual(self.quiz.choices, ["선택 A", "선택 B", "선택 C", "선택 D"])
        self.assertEqual(self.quiz.answer, 2)
        self.assertEqual(self.quiz.hint, "힌트 내용")

    def test_display_shows_question_and_choices_without_answer_or_hint(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.quiz.display()
        displayed = output.getvalue()
        self.assertIn(self.quiz.question, displayed)
        for number, choice in enumerate(self.quiz.choices, start=1):
            self.assertIn(f"{number}. {choice}", displayed)
        self.assertNotIn(self.quiz.hint, displayed)
        self.assertNotIn("정답", displayed)

    def test_answer_check(self) -> None:
        self.assertTrue(self.quiz.check_answer(2))
        self.assertFalse(self.quiz.check_answer(1))
        with self.assertRaises(ValueError):
            self.quiz.check_answer(0)
        with self.assertRaises(TypeError):
            self.quiz.check_answer(True)  # type: ignore[arg-type]

    def test_requires_four_nonempty_choices(self) -> None:
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋"], 1, "힌트")
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋", "  "], 1, "힌트")
        with self.assertRaises(TypeError):
            Quiz("문제", "하나,둘,셋,넷", 1, "힌트")  # type: ignore[arg-type]

    def test_rejects_empty_question_and_choice(self) -> None:
        choices = ["하나", "둘", "셋", "넷"]
        with self.assertRaises(ValueError):
            Quiz("  ", choices, 1, "힌트")
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "", "셋", "넷"], 1, "힌트")

    def test_rejects_invalid_answer(self) -> None:
        for answer in (0, 5):
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                Quiz("문제", ["하나", "둘", "셋", "넷"], answer, "힌트")
        with self.assertRaises(TypeError):
            Quiz("문제", ["하나", "둘", "셋", "넷"], True, "힌트")

    def test_round_trip_keeps_hint(self) -> None:
        restored = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(restored.to_dict(), self.quiz.to_dict())
        self.assertEqual(restored.hint, "힌트 내용")

    def test_rejects_damaged_serialized_data(self) -> None:
        with self.assertRaises(TypeError):
            Quiz.from_dict([])  # type: ignore[arg-type]
        for damaged in (
            {"question": "문제", "choices": ["하나"], "answer": 1, "hint": "힌트"},
            {"question": "문제", "choices": ["하나", "둘", "셋", "넷"], "answer": 5, "hint": "힌트"},
            {"question": "문제", "choices": ["하나", "둘", "셋", "넷"], "answer": 1},
        ):
            with self.subTest(damaged=damaged), self.assertRaises((ValueError, TypeError)):
                Quiz.from_dict(damaged)


if __name__ == "__main__":
    unittest.main()
