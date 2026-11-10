"""main.py의 메뉴와 공통 숫자 입력 테스트."""

import unittest

from main import get_numeric_input, handle_menu_choice, run


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
        for choice in range(2, 5):
            messages: list[str] = []
            self.assertTrue(handle_menu_choice(choice, messages.append))
            self.assertIn("구현 예정입니다.", messages[0])

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


if __name__ == "__main__":
    unittest.main()
