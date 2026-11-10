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
    ) -> None:
        self.quizzes = list(get_default_quizzes() if quizzes is None else quizzes)
        self.input_func = input_func
        self.output_func = output_func

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
        self.output_func("문제 수를 선택하세요: 5, 10, 15")
        count = self._read_number("문제 수 (5/10/15): ", 5, 15)
        while count not in self.QUESTION_COUNTS:
            self.output_func("5, 10, 15 중에서 선택해 주세요.")
            count = self._read_number("문제 수 (5/10/15): ", 5, 15)

        questions = random.sample(self.quizzes, count)
        correct = 0
        for index, quiz in enumerate(questions, start=1):
            self.output_func(f"\n문제 {index}/{count}")
            quiz.display()
            answer = self._read_number("정답 번호 (1-4): ", 1, 4)
            if quiz.check_answer(answer):
                correct += 1
                self.output_func("정답입니다!")
            else:
                self.output_func("오답입니다.")

        incorrect = count - correct
        score = round(correct * 100 / count)
        self.output_func("\n퀴즈 결과")
        self.output_func(f"정답: {correct}개")
        self.output_func(f"오답: {incorrect}개")
        self.output_func(f"최종 점수: {score}/100점")
        return {"correct": correct, "incorrect": incorrect, "score": score, "total": count}
