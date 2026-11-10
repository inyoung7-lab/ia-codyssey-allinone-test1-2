"""main.py의 메뉴와 공통 숫자 입력 테스트."""

import unittest

from main import add_quiz, get_numeric_input, handle_menu_choice, run
from quiz_data import get_default_quizzes
from quiz_game import QuizGame
from unittest.mock import patch


class NumericInputTests(unittest.TestCase):
    def test_retries_invalid_values_and_trims_whitespace(self) -> None:
        values = iter(["abc", "9", "0", "", "   ", "  3  "])
        messages: list[str] = []
        result = get_numeric_input("선택: ", 1, 5, lambda _: next(values), messages.append)
        self.assertEqual(result, 3)
        self.assertEqual(len(messages), 5)


class MenuTests(unittest.TestCase):
    def test_quiz_choice_runs_game(self) -> None:
        class StubGame:
            played = False

            def play(self) -> None:
                self.played = True

        game = StubGame()
        self.assertTrue(handle_menu_choice(1, lambda _: None, game))  # type: ignore[arg-type]
        self.assertTrue(game.played)

    def test_choices_two_to_four_keep_existing_pending_behavior(self) -> None:
        for choice in range(3, 5):
            messages: list[str] = []
            self.assertTrue(handle_menu_choice(choice, messages.append))
            self.assertIn("구현 예정입니다.", messages[0])

    def test_adds_quiz_and_preserves_it_in_game_question_pool(self) -> None:
        quizzes = get_default_quizzes()
        original = [quiz.to_dict() for quiz in quizzes]
        values = iter(["  사용자 문제  ", " 가 ", "나", "다", "라", "2", " 힌트 "])
        messages: list[str] = []
        game = QuizGame(quizzes, lambda _: next(values), messages.append)
        self.assertTrue(handle_menu_choice(2, messages.append, game, lambda _: next(values)))
        self.assertEqual(len(game.quizzes), 16)
        self.assertEqual([quiz.to_dict() for quiz in game.quizzes[:15]], original)
        added = game.quizzes[-1]
        self.assertEqual(added.question, "사용자 문제")
        self.assertEqual(added.choices, ["가", "나", "다", "라"])
        self.assertEqual(added.answer, 2)
        self.assertEqual(added.hint, "힌트")
        self.assertIn("퀴즈가 추가되었습니다!", messages)
        answers = iter(["5", *(str(quiz.answer) for quiz in game.quizzes[:5])])
        game.input_func = lambda _: next(answers)
        with patch("quiz_game.random.sample", return_value=game.quizzes[:5]) as sample, patch.object(
            game, "_read_number", wraps=game._read_number
        ):
            game.play()
        sample.assert_called_once_with(game.quizzes, 5)

    def test_retries_blank_question_and_choices_and_invalid_answer(self) -> None:
        quizzes = get_default_quizzes()
        values = iter(["   ", "문제", "", "하나", "  ", "둘", "셋", "넷", "x", "5", "3", "힌트"])
        messages: list[str] = []
        add_quiz(quizzes, lambda _: next(values), messages.append)
        self.assertEqual(len(quizzes), 16)
        self.assertEqual(quizzes[-1].answer, 3)
        self.assertEqual(sum("입력이 비어 있습니다" in message for message in messages), 3)
        self.assertEqual(sum("숫자" in message or "사이" in message for message in messages), 2)

    def test_choice_five_exits(self) -> None:
        messages: list[str] = []
        self.assertFalse(handle_menu_choice(5, messages.append))
        self.assertIn("종료", messages[0])

    def test_keyboard_interrupt_and_eof_exit_cleanly(self) -> None:
        for exception, expected in ((KeyboardInterrupt, "키보드 중단"), (EOFError, "입력 종료")):
            messages: list[str] = []

            def interrupted_input(_: str) -> str:
                raise exception

            run(interrupted_input, messages.append)
            self.assertTrue(any(expected in message for message in messages))

    def test_eof_during_quiz_entry_exits_cleanly(self) -> None:
        values = iter(["2", "질문"])
        messages: list[str] = []

        def input_until_eof(_: str) -> str:
            try:
                return next(values)
            except StopIteration as error:
                raise EOFError from error

        run(input_until_eof, messages.append)
        self.assertTrue(any("입력 종료" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
