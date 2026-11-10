"""의료 IT·AI 퀴즈 게임의 콘솔 메뉴."""

from collections.abc import Callable

from quiz import Quiz
from quiz_game import QuizGame


TITLE = "의료 IT · AI · 디지털 헬스케어 퀴즈"
MENU_ITEMS = (
    "1. 퀴즈 풀기",
    "2. 퀴즈 추가",
    "3. 퀴즈 목록",
    "4. 점수 확인",
    "5. 종료",
)


def get_numeric_input(
    prompt: str,
    minimum: int,
    maximum: int,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    """범위 안의 정수를 받을 때까지 입력을 확인한다."""
    while True:
        raw_value = input_func(prompt).strip()
        if not raw_value:
            output_func("입력이 비어 있습니다. 숫자를 입력해 주세요.")
            continue
        try:
            value = int(raw_value)
        except ValueError:
            output_func("숫자로 입력해 주세요.")
            continue
        if not minimum <= value <= maximum:
            output_func(f"{minimum}부터 {maximum} 사이의 숫자를 입력해 주세요.")
            continue
        return value


def show_menu(output_func: Callable[[str], None] = print) -> None:
    """프로그램 제목과 메뉴를 표시한다."""
    output_func(f"\n{TITLE}")
    for item in MENU_ITEMS:
        output_func(item)


def get_nonempty_input(
    prompt: str,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> str:
    """공백을 제거한 비어 있지 않은 문자열을 받을 때까지 입력한다."""
    while True:
        value = input_func(prompt).strip()
        if value:
            return value
        output_func("입력이 비어 있습니다. 다시 입력해 주세요.")


def add_quiz(
    quizzes: list[Quiz],
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> None:
    """사용자 입력을 검증해 퀴즈 목록에 새 문항을 추가한다."""
    question = get_nonempty_input("퀴즈 문제: ", input_func, output_func)
    choices = [
        get_nonempty_input(f"선택지 {number}: ", input_func, output_func)
        for number in range(1, 5)
    ]
    answer = get_numeric_input("정답 번호 (1-4): ", 1, 4, input_func, output_func)
    hint = input_func("힌트: ").strip()
    quizzes.append(Quiz(question, choices, answer, hint))
    output_func("퀴즈가 추가되었습니다!")


def show_quizzes(
    quizzes: list[Quiz],
    output_func: Callable[[str], None] = print,
) -> None:
    """전체 퀴즈의 순번, 문제, 선택지를 표시한다."""
    if not quizzes:
        output_func("등록된 퀴즈가 없습니다.")
        return

    output_func("퀴즈 목록")
    for index, quiz in enumerate(quizzes, start=1):
        output_func(f"\n{index}번 퀴즈")
        quiz.display()


def handle_menu_choice(
    choice: int,
    output_func: Callable[[str], None] = print,
    quiz_game: QuizGame | None = None,
    input_func: Callable[[str], str] = input,
) -> bool:
    """메뉴를 처리하고 계속 실행할지 반환한다."""
    if choice == 1:
        (quiz_game or QuizGame(output_func=output_func)).play()
    elif choice == 2:
        game = quiz_game or QuizGame(output_func=output_func)
        add_quiz(game.quizzes, input_func, output_func)
    elif choice == 3:
        game = quiz_game or QuizGame(output_func=output_func)
        show_quizzes(game.quizzes, output_func)
    elif choice == 4:
        output_func("점수 확인 기능은 구현 예정입니다.")
    else:
        output_func("프로그램을 종료합니다.")
        return False
    return True


def run(input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print) -> None:
    """메뉴를 반복 실행하고 입력 중단을 정상 종료로 처리한다."""
    quiz_game = QuizGame(input_func=input_func, output_func=output_func)
    try:
        while True:
            show_menu(output_func)
            choice = get_numeric_input("메뉴를 선택해 주세요 (1-5): ", 1, 5,
                                       input_func, output_func)
            if not handle_menu_choice(
                choice,
                output_func,
                quiz_game,
                input_func,
            ):
                break
    except KeyboardInterrupt:
        output_func("\n키보드 중단을 감지했습니다. 프로그램을 종료합니다.")
    except EOFError:
        output_func("\n입력 종료를 감지했습니다. 프로그램을 종료합니다.")
    # 저장 기능 구현 시에는 이 종료 경로를 정리 단계와 연결해 안전하게 저장한다.


if __name__ == "__main__":
    run()
