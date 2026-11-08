"""개별 퀴즈 문항을 표현하는 클래스."""

from typing import Any


class Quiz:
    """문제, 네 개의 선택지, 정답 번호, 힌트를 보관한다."""

    def __init__(self, question: str, choices: list[str], answer: int, hint: str) -> None:
        """입력 데이터를 검사한 뒤 Quiz 속성으로 저장한다."""
        if not isinstance(question, str):
            raise TypeError("question은 문자열이어야 합니다.")
        if not question.strip():
            raise ValueError("question은 비어 있을 수 없습니다.")
        if not isinstance(choices, list):
            raise TypeError("choices는 문자열 목록이어야 합니다.")
        if len(choices) != 4:
            raise ValueError("choices에는 선택지가 정확히 4개 있어야 합니다.")
        for choice in choices:
            if not isinstance(choice, str):
                raise TypeError("각 선택지는 문자열이어야 합니다.")
            if not choice.strip():
                raise ValueError("선택지는 비어 있을 수 없습니다.")
        if isinstance(answer, bool) or not isinstance(answer, int):
            raise TypeError("answer는 bool이 아닌 정수여야 합니다.")
        if not 1 <= answer <= 4:
            raise ValueError("answer는 1부터 4 사이의 숫자여야 합니다.")
        if not isinstance(hint, str):
            raise TypeError("hint는 문자열이어야 합니다.")

        self.question = question
        self.choices = choices.copy()
        self.answer = answer
        self.hint = hint

    def display(self) -> None:
        """문제와 선택지를 표시하되 정답과 힌트는 숨긴다."""
        print(self.question)
        for number, choice in enumerate(self.choices, start=1):
            print(f"{number}. {choice}")

    def check_answer(self, selected: int) -> bool:
        """선택 번호가 유효하면 정답 여부를 반환한다."""
        if isinstance(selected, bool) or not isinstance(selected, int):
            raise TypeError("selected는 bool이 아닌 정수여야 합니다.")
        if not 1 <= selected <= 4:
            raise ValueError("selected는 1부터 4 사이의 숫자여야 합니다.")
        return selected == self.answer

    def to_dict(self) -> dict[str, Any]:
        """JSON으로 저장할 수 있는 기본 자료형 딕셔너리를 만든다."""
        return {
            "question": self.question,
            "choices": self.choices.copy(),
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Quiz":
        """딕셔너리 데이터를 검사해 Quiz 객체로 복원한다."""
        if not isinstance(data, dict):
            raise TypeError("Quiz 데이터는 딕셔너리여야 합니다.")
        required_keys = {"question", "choices", "answer", "hint"}
        if not required_keys.issubset(data):
            missing = required_keys - data.keys()
            raise ValueError(f"필수 데이터가 없습니다: {', '.join(sorted(missing))}")
        # 생성자에서 필드별 자료형과 값을 다시 검사한다.
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data["hint"],
        )
