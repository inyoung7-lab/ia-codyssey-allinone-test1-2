"""퀴즈와 게임 기록을 프로젝트 루트의 JSON 파일에 저장한다."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from quiz import Quiz
from quiz_data import get_default_quizzes


class StateStore:
    """퀴즈 목록, 최고 점수, 완료 기록을 읽고 쓴다."""

    VERSION = 1

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path(__file__).with_name("state.json")
        self.quizzes = get_default_quizzes()
        self.high_score: dict[str, Any] | None = None
        self.history: list[dict[str, Any]] = []

    def load(self, output_func=print) -> None:
        """저장 상태를 복원하고, 없거나 손상된 파일에는 기본 상태를 사용한다."""
        if not self.path.exists():
            self.quizzes = get_default_quizzes()
            self.high_score = None
            self.history = []
            return
        try:
            with self.path.open("r", encoding="utf-8") as state_file:
                data = json.load(state_file)
            if not isinstance(data, dict):
                raise ValueError("저장 데이터는 JSON 객체여야 합니다.")
            if data.get("version", self.VERSION) != self.VERSION:
                raise ValueError("지원하지 않는 저장 데이터 버전입니다.")
            if not isinstance(data.get("quizzes"), list):
                raise ValueError("퀴즈 데이터 형식이 올바르지 않습니다.")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            high_score = data.get("high_score")
            history = data.get("history", [])
            if high_score is not None:
                self._validate_record(high_score)
            if not isinstance(history, list):
                raise ValueError("게임 기록 데이터 형식이 올바르지 않습니다.")
            for record in history:
                self._validate_record(record)
            self.quizzes = quizzes
            self.high_score = high_score
            self.history = history
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            self.quizzes = get_default_quizzes()
            self.high_score = None
            self.history = []
            output_func(f"저장 파일을 읽을 수 없어 기본 퀴즈로 시작합니다: {error}")

    @staticmethod
    def _validate_record(record: Any) -> None:
        if not isinstance(record, dict):
            raise ValueError("게임 기록 데이터 형식이 올바르지 않습니다.")
        if not isinstance(record.get("datetime"), str):
            raise ValueError("게임 기록 날짜 형식이 올바르지 않습니다.")
        questions = record.get("questions")
        correct = record.get("correct")
        score = record.get("score")
        if (
            isinstance(questions, bool)
            or not isinstance(questions, int)
            or questions < 1
            or isinstance(correct, bool)
            or not isinstance(correct, int)
            or not 0 <= correct <= questions
            or isinstance(score, bool)
            or not isinstance(score, int)
            or not 0 <= score <= 100
        ):
            raise ValueError("게임 기록 점수 형식이 올바르지 않습니다.")

    def save(self, output_func=print) -> bool:
        """상태를 UTF-8 JSON으로 원자적으로 저장한다."""
        data = {
            "version": self.VERSION,
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "high_score": self.high_score,
            "history": self.history,
        }
        temporary_path = self.path.with_name(self.path.name + ".tmp")
        try:
            with temporary_path.open("w", encoding="utf-8") as state_file:
                json.dump(data, state_file, ensure_ascii=False, indent=2)
                state_file.write("\n")
            os.replace(temporary_path, self.path)
            return True
        except OSError as error:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            output_func(f"저장 파일을 쓸 수 없습니다: {error}")
            return False

    def update_quizzes(self, quizzes: list[Quiz], output_func=print) -> bool:
        self.quizzes = list(quizzes)
        return self.save(output_func)

    def record_game(self, result: dict[str, int], output_func=print) -> bool:
        """완료 게임을 기록하고 엄격히 더 높은 점수만 최고 점수로 갱신한다."""
        record: dict[str, Any] = {
            "datetime": datetime.now().astimezone().isoformat(timespec="seconds"),
            "questions": result["total"],
            "correct": result["correct"],
            "score": result["score"],
        }
        self.history.append(record)
        if self.high_score is None or record["score"] > self.high_score["score"]:
            self.high_score = record.copy()
        return self.save(output_func)
