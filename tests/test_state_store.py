"""상태 JSON 저장과 복원 테스트. 모든 파일은 임시 디렉터리에 격리한다."""

import json
import tempfile
import unittest
from pathlib import Path

from quiz import Quiz
from state_store import StateStore


class StateStoreTests(unittest.TestCase):
    def test_missing_file_uses_defaults_without_creating_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            store = StateStore(path)
            store.load(lambda _: None)
            self.assertEqual(len(store.quizzes), 15)
            self.assertIsNone(store.high_score)
            self.assertEqual(store.history, [])
            self.assertFalse(path.exists())

    def test_corrupt_file_reports_error_and_recovers_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("{broken", encoding="utf-8")
            messages: list[str] = []
            store = StateStore(path)
            store.load(messages.append)
            self.assertEqual(len(store.quizzes), 15)
            self.assertIsNone(store.high_score)
            self.assertEqual(store.history, [])
            self.assertTrue(messages)

    def test_valid_json_with_invalid_shape_recovers_and_io_errors_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("[]", encoding="utf-8")
            messages: list[str] = []
            store = StateStore(path)
            store.load(messages.append)
            self.assertEqual(len(store.quizzes), 15)
            self.assertTrue(messages)

            path.unlink()
            path.mkdir()
            read_messages: list[str] = []
            store.load(read_messages.append)
            self.assertEqual(len(store.quizzes), 15)
            self.assertTrue(read_messages)
            write_messages: list[str] = []
            self.assertFalse(store.save(write_messages.append))
            self.assertTrue(write_messages)

    def test_saves_and_restores_added_quiz_and_game_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            store = StateStore(path)
            store.load(lambda _: None)
            store.quizzes.append(Quiz("추가 문제", ["가", "나", "다", "라"], 2, "힌트"))
            store.update_quizzes(store.quizzes, lambda _: None)
            store.record_game({"total": 5, "correct": 4, "incorrect": 1, "score": 80}, lambda _: None)

            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["version"], 1)
            restored = StateStore(path)
            restored.load(lambda _: None)
            self.assertEqual(len(restored.quizzes), 16)
            self.assertEqual(restored.quizzes[-1].question, "추가 문제")
            self.assertEqual(restored.high_score["score"], 80)
            self.assertEqual(restored.history[0]["questions"], 5)
            self.assertIn("datetime", restored.history[0])

    def test_high_score_updates_only_when_score_is_higher_and_keeps_ties(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "state.json")
            store.load(lambda _: None)
            store.record_game({"total": 5, "correct": 4, "incorrect": 1, "score": 80}, lambda _: None)
            best_time = store.high_score["datetime"]
            store.record_game({"total": 10, "correct": 8, "incorrect": 2, "score": 80}, lambda _: None)
            self.assertEqual(store.high_score["datetime"], best_time)
            store.record_game({"total": 5, "correct": 2, "incorrect": 3, "score": 40}, lambda _: None)
            self.assertEqual(store.high_score["score"], 80)
            self.assertEqual(len(store.history), 3)


if __name__ == "__main__":
    unittest.main()
