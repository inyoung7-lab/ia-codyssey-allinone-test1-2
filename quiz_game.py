"""콘솔 퀴즈 진행 및 결과 계산."""

import random
from collections.abc import Callable, Sequence

from quiz import Quiz
from quiz_data import get_default_quizzes


class QuizGame:
    """문항을 무작위로 출제하고 답안과 점수를 관리한다."""

    QUESTION_COUNTS = (5, 10, 15)

    def __init__(
        self,
        quizzes: Sequence[Quiz] | None = None,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
        on_result: Callable[[dict[str, int]], None] | None = None,
    ) -> None:
        self.quizzes = list(get_default_quizzes() if quizzes is None else quizzes)
        self.input_func = input_func
        self.output_func = output_func
        self.on_result = on_result

    def _read_number(self, prompt: str, minimum: int, maximum: int) -> int:
        while True:
            raw = self.input_func(prompt).strip()
            try:
                value = int(raw)
            except ValueError:
                self.output_func("숫자를 입력해 주세요.")
                continue
            if minimum <= value <= maximum:
                return value
            self.output_func(f"{minimum}부터 {maximum} 사이의 숫자를 입력해 주세요.")

    def play(self) -> dict[str, int]:
        """문제 수를 고르고 한 판을 진행한 뒤 결과 요약을 반환한다."""
        if len(self.quizzes) < min(self.QUESTION_COUNTS):
            self.output_func("퀴즈를 시작하려면 등록된 문항이 최소 5개 필요합니다.")
            return {"correct": 0, "incorrect": 0, "score": 0, "total": 0}

        available_counts = tuple(
            count for count in self.QUESTION_COUNTS if count <= len(self.quizzes)
        )
        available_text = ", ".join(str(count) for count in available_counts)
        self.output_func(f"현재 선택 가능한 문제 수: {available_text}")
        while True:
            count = self._read_number(
                f"문제 수 ({available_text}): ", 5, 15
            )
            if count in available_counts:
                break
            if count not in self.QUESTION_COUNTS:
                self.output_func(
                    f"{available_text} 중에서 선택해 주세요. 현재 등록된 퀴즈는 "
                    f"{len(self.quizzes)}개입니다."
                )
                continue
            self.output_func(
                f"등록된 퀴즈는 현재 {len(self.quizzes)}개라 {count}문제 모드는 "
                f"선택할 수 없습니다. 가능한 문제 수: {available_text}"
            )

        if count > len(self.quizzes):
            self.output_func(
                f"등록된 퀴즈 {len(self.quizzes)}개보다 많은 {count}문제는 출제할 수 없습니다."
            )
            return {"correct": 0, "incorrect": 0, "score": 0, "total": 0}

        questions = random.sample(self.quizzes, count)
        correct = 0
        hints_used = 0
        for index, quiz in enumerate(questions, start=1):
            self.output_func(f"\n문제 {index}/{count}")
            quiz.display()
            answer = self._read_answer(quiz)
            if answer is None:
                hints_used += 1
                answer = self._read_answer(quiz)
                while answer is None:
                    hints_used += 1
                    answer = self._read_answer(quiz)
            if quiz.check_answer(answer):
                correct += 1
                self.output_func("정답입니다!")
            else:
                self.output_func("오답입니다.")

        incorrect = count - correct
        score = max(0, round(correct * 100 / count) - hints_used * 10)
        self.output_func("\n퀴즈 결과")
        self.output_func(f"정답: {correct}개")
        self.output_func(f"오답: {incorrect}개")
        self.output_func(f"최종 점수: {score}/100점")
        result = {"correct": correct, "incorrect": incorrect, "score": score, "total": count}
        if self.on_result is not None:
            self.on_result(result)
        return result

    def _read_answer(self, quiz: Quiz) -> int | None:
        """정답 번호 또는 힌트 요청을 읽는다. 힌트는 요청마다 10점 감점된다."""
        while True:
            raw = self.input_func("정답 번호 (1-4, 힌트는 h): ").strip()
            if raw.lower() in {"h", "hint"}:
                self.output_func(f"힌트: {quiz.hint}")
                return None
            try:
                answer = int(raw)
            except ValueError:
                self.output_func("1부터 4 사이의 번호 또는 h를 입력해 주세요.")
                continue
            if 1 <= answer <= 4:
                return answer
            self.output_func("1부터 4 사이의 번호를 입력해 주세요.")
