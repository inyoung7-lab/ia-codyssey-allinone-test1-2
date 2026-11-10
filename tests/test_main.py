"""main.py의 메뉴와 공통 숫자 입력 테스트."""

import contextlib
import json
import io
import tempfile
import unittest
from pathlib import Path

from main import add_quiz, delete_quiz, get_numeric_input, handle_menu_choice, run, show_quizzes
from quiz_data import get_default_quizzes
from quiz_game import QuizGame
from unittest.mock import patch
from state_store import StateStore


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

    def test_score_menu_guides_when_no_games_have_been_played(self) -> None:
        messages: list[str] = []
        store = StateStore("unused-state.json")
        self.assertTrue(handle_menu_choice(4, messages.append, state_store=store))
        self.assertIn("아직 완료된 퀴즈 기록이 없습니다.", messages[0])

    def test_menu_six_deletes_and_persists_selected_quiz(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "state.json")
            store.load(lambda _: None)
            original_question = store.quizzes[0].question
            store.save(lambda _: None)
            game = QuizGame(store.quizzes)
            values = iter(["1", "y"])
            messages: list[str] = []
            self.assertTrue(handle_menu_choice(6, messages.append, game, lambda _: next(values), store))
            self.assertEqual(len(game.quizzes), 14)
            self.assertNotIn(original_question, [quiz.question for quiz in game.quizzes])
            restored = StateStore(store.path)
            restored.load(lambda _: None)
            self.assertEqual(len(restored.quizzes), 14)
            self.assertNotIn(original_question, [quiz.question for quiz in restored.quizzes])
            self.assertIn("퀴즈가 삭제되었습니다.", messages)

    def test_delete_cancel_preserves_memory_and_file_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "state.json")
            store.load(lambda _: None)
            store.save(lambda _: None)
            original_bytes = store.path.read_bytes()
            game = QuizGame(store.quizzes)
            original_quizzes = [quiz.to_dict() for quiz in game.quizzes]
            messages: list[str] = []
            values = iter(["1", "n"])
            self.assertFalse(delete_quiz(game.quizzes, lambda _: next(values), messages.append, store))
            # Explicitly verify a cancelled confirmation leaves the persisted state byte-for-byte unchanged.
            self.assertEqual([quiz.to_dict() for quiz in game.quizzes], original_quizzes)
            self.assertEqual(store.path.read_bytes(), original_bytes)

    def test_invalid_and_blank_delete_numbers_are_retried(self) -> None:
        quizzes = get_default_quizzes()
        values = iter(["", "x", "99", "1", "y"])
        messages: list[str] = []
        self.assertTrue(delete_quiz(quizzes, lambda _: next(values), messages.append))
        self.assertEqual(len(quizzes), 14)
        self.assertTrue(any("비어" in message for message in messages))
        self.assertTrue(any("숫자" in message for message in messages))
        self.assertTrue(any("사이" in message for message in messages))

    def test_empty_list_and_last_quiz_deletion_remain_empty_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "state.json")
            store.load(lambda _: None)
            store.update_quizzes([store.quizzes[0]], lambda _: None)
            game = QuizGame(store.quizzes)
            values = iter(["1", "y"])
            messages: list[str] = []
            self.assertTrue(handle_menu_choice(6, messages.append, game, lambda _: next(values), store))
            self.assertEqual(game.quizzes, [])
            data = json.loads(store.path.read_text(encoding="utf-8"))
            self.assertEqual(data["quizzes"], [])
            reloaded = StateStore(store.path)
            reloaded.load(messages.append)
            self.assertEqual(reloaded.quizzes, [])
            self.assertTrue(handle_menu_choice(6, messages.append, QuizGame([]), state_store=reloaded))
            self.assertIn("등록된 퀴즈가 없습니다.", messages)

    def test_delete_preserves_high_score_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "state.json")
            store.load(lambda _: None)
            store.record_game({"total": 5, "correct": 3, "incorrect": 2, "score": 60}, lambda _: None)
            high_score = store.high_score.copy()
            history = [record.copy() for record in store.history]
            game = QuizGame(store.quizzes)
            values = iter(["1", "y"])
            self.assertTrue(delete_quiz(game.quizzes, lambda _: next(values), lambda _: None, store))
            restored = StateStore(store.path)
            restored.load(lambda _: None)
            self.assertEqual(restored.high_score, high_score)
            self.assertEqual(restored.history, history)

    def test_failed_delete_save_keeps_memory_and_state_file_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "state.json")
            store.load(lambda _: None)
            store.save(lambda _: None)
            original_bytes = store.path.read_bytes()
            game = QuizGame(store.quizzes)
            messages: list[str] = []
            values = iter(["1", "y"])
            with patch("state_store.os.replace", side_effect=OSError("disk error")):
                self.assertFalse(delete_quiz(game.quizzes, lambda _: next(values), messages.append, store))
            self.assertEqual(len(game.quizzes), 15)
            self.assertEqual(len(store.quizzes), 15)
            self.assertEqual(store.path.read_bytes(), original_bytes)
            self.assertTrue(any("저장에 실패" in message for message in messages))

    def test_deleted_quiz_stays_deleted_after_program_restart(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            initial_store = StateStore(state_path)
            initial_store.load(lambda _: None)
            initial_store.save(lambda _: None)
            deleted_question = initial_store.quizzes[0].question
            first_inputs = iter(["6", "1", "y", "5"])
            with contextlib.redirect_stdout(io.StringIO()):
                run(lambda _: next(first_inputs), lambda _: None, state_path)

            second_inputs = iter(["3", "5"])
            listing_output: list[str] = []
            with contextlib.redirect_stdout(io.StringIO()):
                run(lambda _: next(second_inputs), listing_output.append, state_path)
            restored = StateStore(state_path)
            restored.load(lambda _: None)
            self.assertEqual(len(restored.quizzes), 14)
            self.assertNotIn(deleted_question, [quiz.question for quiz in restored.quizzes])
            self.assertTrue(any("14번 퀴즈" in message for message in listing_output))

    def test_eof_during_delete_confirmation_exits_without_deleting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            store = StateStore(state_path)
            store.load(lambda _: None)
            store.save(lambda _: None)
            original_bytes = state_path.read_bytes()
            values = iter(["6", "1"])
            messages: list[str] = []

            def input_until_eof(_: str) -> str:
                try:
                    return next(values)
                except StopIteration as error:
                    raise EOFError from error

            with contextlib.redirect_stdout(io.StringIO()):
                run(input_until_eof, messages.append, state_path)
            self.assertEqual(state_path.read_bytes(), original_bytes)
            self.assertTrue(any("입력 종료" in message for message in messages))

    def test_keyboard_interrupt_during_delete_confirmation_exits_safely(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            store = StateStore(state_path)
            store.load(lambda _: None)
            store.save(lambda _: None)
            original_bytes = state_path.read_bytes()
            values = iter(["6", "1"])
            messages: list[str] = []

            def interrupt_confirmation(_: str) -> str:
                try:
                    return next(values)
                except StopIteration as error:
                    raise KeyboardInterrupt from error

            with contextlib.redirect_stdout(io.StringIO()):
                run(interrupt_confirmation, messages.append, state_path)
            self.assertEqual(state_path.read_bytes(), original_bytes)
            self.assertTrue(any("키보드 중단" in message for message in messages))

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

    def test_quiz_list_shows_all_defaults_and_added_quiz_without_answers_or_hints(self) -> None:
        quizzes = get_default_quizzes()
        added = iter(["사용자 목록 문제", "목록 선택 1", "목록 선택 2", "목록 선택 3", "목록 선택 4", "4", "비공개 힌트"])
        add_quiz(quizzes, lambda _: next(added), lambda _: None)
        game = QuizGame(quizzes)
        menu_messages: list[str] = []
        with contextlib.redirect_stdout(io.StringIO()) as displayed:
            self.assertTrue(handle_menu_choice(3, menu_messages.append, game))
        listing = displayed.getvalue()
        self.assertIn("퀴즈 목록", menu_messages)
        self.assertIn("사용자 목록 문제", listing)
        for quiz in quizzes:
            self.assertIn(quiz.question, listing)
            for choice in quiz.choices:
                self.assertIn(choice, listing)
            self.assertNotIn(quiz.hint, listing)
        self.assertNotIn("정답 번호", listing)
        self.assertNotIn("비공개 힌트", listing)

    def test_empty_quiz_list_is_reported(self) -> None:
        messages: list[str] = []
        show_quizzes([], messages.append)
        self.assertEqual(messages, ["등록된 퀴즈가 없습니다."])

    def test_list_menu_returns_to_main_menu(self) -> None:
        values = iter(["3", "5"])
        messages: list[str] = []
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            run(lambda _: next(values), messages.append, Path(directory) / "state.json")
        self.assertTrue(any("퀴즈 목록" in message for message in messages))
        self.assertTrue(any("프로그램을 종료합니다." in message for message in messages))

    def test_addition_game_history_and_restart_are_integrated(self) -> None:
        defaults = get_default_quizzes()
        values = iter([
            "2", "저장할 사용자 문제", "가", "나", "다", "라", "1", "저장 힌트",
            "1", "5", *(str(quiz.answer) for quiz in defaults[:5]), "4", "5",
        ])
        messages: list[str] = []
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            with patch("quiz_game.random.sample", return_value=defaults[:5]), contextlib.redirect_stdout(io.StringIO()):
                run(lambda _: next(values), messages.append, state_path)

            reloaded_messages: list[str] = []
            restart_inputs = iter(["3", "4", "5"])
            with contextlib.redirect_stdout(io.StringIO()):
                run(lambda _: next(restart_inputs), reloaded_messages.append, state_path)
            self.assertTrue(any("최고 점수: 100/100점" in message for message in reloaded_messages))
            self.assertTrue(any("게임 기록" in message for message in reloaded_messages))
            self.assertTrue(state_path.is_file())
            persisted = StateStore(state_path)
            persisted.load(lambda _: None)
            self.assertEqual(len(persisted.quizzes), 16)
            self.assertEqual(persisted.quizzes[-1].question, "저장할 사용자 문제")
            self.assertEqual(len(persisted.history), 1)

    def test_choice_five_exits(self) -> None:
        messages: list[str] = []
        self.assertFalse(handle_menu_choice(5, messages.append))
        self.assertIn("종료", messages[0])

    def test_keyboard_interrupt_and_eof_exit_cleanly(self) -> None:
        for exception, expected in ((KeyboardInterrupt, "키보드 중단"), (EOFError, "입력 종료")):
            messages: list[str] = []

            def interrupted_input(_: str) -> str:
                raise exception

            with tempfile.TemporaryDirectory() as directory:
                run(interrupted_input, messages.append, Path(directory) / "state.json")
            self.assertTrue(any(expected in message for message in messages))

    def test_eof_during_quiz_entry_exits_cleanly(self) -> None:
        values = iter(["2", "질문"])
        messages: list[str] = []

        def input_until_eof(_: str) -> str:
            try:
                return next(values)
            except StopIteration as error:
                raise EOFError from error

        with tempfile.TemporaryDirectory() as directory:
            run(input_until_eof, messages.append, Path(directory) / "state.json")
        self.assertTrue(any("입력 종료" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
