# Codyssey 올인원 미션 1-2

## 프로젝트 개요

의료 IT, 인공지능, 디지털 헬스케어를 주제로 한 Python 콘솔 퀴즈 프로젝트입니다. Python 표준 라이브러리만 사용합니다.

## 퀴즈 주제 선정 이유

의료 IT와 디지털 헬스케어는 실제 의료 현장의 정보 시스템과 연결되고, 인공지능은 의료 데이터 활용과 새로운 헬스케어 기술을 이해하는 데 중요합니다. 세 주제를 함께 다루어 Python 기초 문법을 익히면서 관련 용어와 활용 사례도 확인할 수 있도록 구성했습니다.

## 실행 방법

프로젝트 루트에서 실행합니다.

```powershell
python main.py
```

메뉴 `1. 퀴즈 풀기`에서는 5개, 10개, 15개 모드 중 현재 보유한 퀴즈 수 이하인 모드만 선택할 수 있습니다. 예를 들어 7개를 보유하면 5개 모드만, 12개를 보유하면 5개와 10개 모드만 가능합니다. 선택 가능한 모드에서 중복 없이 무작위로 출제하며, 각 문제에 선택지 네 개를 표시합니다. 퀴즈가 5개 미만이면 안내 후 게임을 시작하지 않습니다. 답은 1~4번으로 입력하고, `h`를 입력하면 힌트를 확인할 수 있습니다. 힌트 요청 1회마다 최종 점수에서 10점 감점되며, 점수는 정답 비율을 반올림한 뒤 감점을 적용하고 0점 아래로 내려가지 않습니다. 게임이 끝나면 정답·오답 개수와 100점 만점 점수를 표시합니다. 잘못된 입력은 재입력을 안내하며, Ctrl+C 또는 입력 종료(EOF)는 안전하게 종료합니다.

메뉴 `2. 퀴즈 추가`에서는 문제, 선택지 네 개, 정답 번호, 힌트를 입력해 문항을 등록합니다. 문제와 선택지는 비어 있지 않도록 확인하며 입력 앞뒤 공백을 제거합니다. 추가 문항은 `state.json`에 저장되어 재시작 후에도 유지됩니다.

메뉴 `3. 퀴즈 목록`은 저장된 기본 및 사용자 문항을 순서대로 출력합니다. 기본 문항은 의료 IT·인공지능·디지털 헬스케어 주제별 5개씩 총 15개입니다. 각 항목에 순번·문제·선택지 네 개만 표시하며 정답과 힌트는 목록에 표시하지 않습니다. 목록 확인 후 메인 메뉴로 돌아옵니다.

메뉴 `4. 점수 확인`은 최고 점수와 완료된 전체 게임 히스토리를 보여줍니다. 최고 점수보다 낮은 결과는 히스토리에만 추가하며, 동점이면 기존 최고 기록의 날짜·시간을 유지합니다. 각 게임 기록에는 날짜·시간, 문제 수, 정답 수, 최종 점수가 포함됩니다. 게임 기록 저장에 실패하면 최고 점수와 히스토리를 저장 전 메모리 상태로 되돌리고 오류를 안내합니다.

메뉴 `5. 종료`는 프로그램을 종료합니다. 메뉴 `6. 퀴즈 삭제`는 등록된 퀴즈를 번호와 문제 내용으로 확인한 뒤 삭제 여부를 묻습니다. `y`로 승인한 경우에만 목록을 저장하고, `n`이면 현재 목록과 저장 파일을 그대로 둡니다. 마지막 문항을 삭제해 저장 목록이 비어도 기본 퀴즈를 자동 복원하지 않습니다. 삭제 저장이 실패하면 메모리 목록도 변경하지 않습니다. 기본 제공 문항과 사용자 추가 문항 모두 삭제할 수 있습니다.

## 저장 데이터

게임 상태는 프로젝트 루트의 `state.json`에 UTF-8 JSON(`ensure_ascii=False`)으로 저장합니다. 퀴즈 추가·삭제 및 완료 게임 기록은 저장되며 재시작 후 복원됩니다. 파일이 없으면 기본 퀴즈 15개와 빈 점수 기록으로 시작합니다. JSON이 손상되었거나 읽기 오류가 있으면 안내 후 기본값을 사용합니다. 저장은 임시 파일을 쓴 뒤 교체하며, 기록 저장에 실패하면 메모리의 최고 점수와 히스토리도 이전 상태로 복구합니다. 정상 저장된 빈 퀴즈 목록은 기본 퀴즈로 대체하지 않습니다. `state.json`은 개인 실행 기록이므로 Git에서 제외됩니다.

```json
{
  "version": 1,
  "quizzes": [
    {"question": "문제 예시", "choices": ["가", "나", "다", "라"], "answer": 1, "hint": "힌트 예시"}
  ],
  "high_score": {
    "datetime": "2026-11-10T12:00:00+09:00",
    "questions": 5,
    "correct": 4,
    "score": 80
  },
  "history": [
    {
      "datetime": "2026-11-10T12:00:00+09:00",
      "questions": 5,
      "correct": 4,
      "score": 80
    }
  ]
}
```

`high_score`는 히스토리에서 가장 높은 최종 점수의 기록이며, 점수 동률에서는 먼저 기록된 최고 점수의 시간 정보를 유지합니다. 마지막 퀴즈를 삭제한 경우 `quizzes`는 빈 배열로 저장될 수 있습니다.

## Git 실습 과정

저장소 복제 및 최신 `main` 확인은 다음 명령으로 진행했습니다.

```powershell
git clone https://github.com/inyoung7-lab/ia-codyssey-allinone-test1-2.git
cd ia-codyssey-allinone-test1-2
git pull --ff-only origin main
```

클론과 pull은 아래 실습 스크린샷에서 확인할 수 있습니다.

- [저장소 클론 (`git clone`)](docs/screenshots/git_workflow/01_git_clone.png)
- [main 최신 상태 확인 (`git pull --ff-only origin main`)](docs/screenshots/git_workflow/02_git_pull.png)

이후 기능별 `feature/quiz-play`, `feature/quiz-add`, `feature/quiz-list`, `feature/quiz-score-history`, `feature/quiz-delete` 브랜치에서 기능을 작업한 커밋과 원격 브랜치가 확인됩니다. Git 이력에는 이 기능 브랜치들의 작업 커밋과 Pull Request #1~#5 병합 커밋이 남아 있습니다. 따라서 브랜치 작업, 커밋, 원격 Push 및 PR 병합은 저장소의 브랜치·커밋 이력으로 확인되며, clone과 pull은 위 스크린샷으로 확인됩니다. 각 기능의 구체적 브랜치 생성·커밋·Push 명령은 별도 기록이 없어 재현 명령으로 단정해 적지 않았습니다.

### 기능별 스크린샷 증빙

- Step 5 퀴즈 플레이: [01_quiz_play.png](docs/screenshots/core_features/mission1-2-step5-play-evidence/01_quiz_play.png), [02_quiz_result.png](docs/screenshots/core_features/mission1-2-step5-play-evidence/02_quiz_result.png)
- Step 6 퀴즈 추가: [01_quiz_add.png](docs/screenshots/core_features/mission1-2-step6-add-evidence/01_quiz_add.png), [02_added_quiz_play.png](docs/screenshots/core_features/mission1-2-step6-add-evidence/02_added_quiz_play.png)
- Step 7 퀴즈 목록: [01_quiz_list.png](docs/screenshots/core_features/mission1-2-step7-list-evidence/01_quiz_list.png), [02_added_quiz_list.png](docs/screenshots/core_features/mission1-2-step7-list-evidence/02_added_quiz_list.png)
- Step 8 점수·히스토리·저장·힌트: [01_first_score.png](docs/screenshots/core_features/mission1-2-step8-score-evidence/01_first_score.png), [02_best_score.png](docs/screenshots/core_features/mission1-2-step8-score-evidence/02_best_score.png), [03_score_history.png](docs/screenshots/core_features/mission1-2-step8-score-evidence/03_score_history.png), [04_persistence.png](docs/screenshots/core_features/mission1-2-step8-score-evidence/04_persistence.png), [05_hint_display.png](docs/screenshots/core_features/mission1-2-step8-score-evidence/05_hint_display.png), [06_hint_deduction.png](docs/screenshots/core_features/mission1-2-step8-score-evidence/06_hint_deduction.png)
- Step 9 퀴즈 삭제: [01_delete_menu.png](docs/screenshots/core_features/mission1-2-step9-delete-evidence/01_delete_menu.png), [02_delete_success.png](docs/screenshots/core_features/mission1-2-step9-delete-evidence/02_delete_success.png), [03_delete_cancel.png](docs/screenshots/core_features/mission1-2-step9-delete-evidence/03_delete_cancel.png), [04_delete_persistence.png](docs/screenshots/core_features/mission1-2-step9-delete-evidence/04_delete_persistence.png), [05_history_preserved.png](docs/screenshots/core_features/mission1-2-step9-delete-evidence/05_history_preserved.png)

## 제출 증빙

아래 링크는 저장소에 포함된 환경 설정, 예외 처리, Git 실습 스크린샷입니다.

### 실행 환경

- [Python 개발 환경](docs/screenshots/environment/01_development_environment.png)

### 예외 처리

- [잘못된 메뉴 입력 처리](docs/screenshots/error_handling/01_invalid_menu_input.png)
- [Ctrl+C 안전 종료](docs/screenshots/error_handling/02_keyboard_interrupt.png)
- [EOFError 안전 종료](docs/screenshots/error_handling/03_eof_safe_exit.png)

### Git 실습

- **clone:** 저장소 복제는 [git clone](docs/screenshots/git_workflow/01_git_clone.png) 증빙을 참고하세요.
- **pull:** 원격 `main` 최신화는 [git pull --ff-only origin main](docs/screenshots/git_workflow/02_git_pull.png) 증빙을 참고하세요.
- **commit/push:** 복제한 저장소에서 변경 내용을 커밋하고 원격으로 보내는 과정은 [clone, commit, push](docs/screenshots/git_workflow/03_clone_commit_push.png) 증빙에 있습니다.
- **원본 저장소 pull:** 원본 저장소에서 최신 변경을 가져오는 과정은 [원본 저장소 pull](docs/screenshots/git_workflow/04_original_repo_pull.png) 증빙에 있습니다.
- **checkout:** 브랜치 전환은 [git checkout](docs/screenshots/git_workflow/05_git_checkout.png) 증빙에 있습니다.
- **init:** 저장소 초기화는 [git init](docs/screenshots/git_workflow/06_git_init.png) 증빙에 있습니다.
- **commit graph:** 브랜치와 커밋 흐름은 [커밋 그래프](docs/screenshots/git_workflow/07_git_commit_graph.png)에서 확인할 수 있습니다.

## 파일 구성

```text
main.py                 # 콘솔 메뉴와 실행 흐름
quiz.py                 # 개별 Quiz 모델과 답안 판정
quiz_data.py            # 기본 퀴즈 15문항
quiz_game.py            # 무작위 퀴즈 진행과 점수 계산
state_store.py          # state.json 저장과 복원
tests/                  # unittest 자동 테스트
```

## 테스트

전체 테스트는 다음 명령으로 실행합니다.

```powershell
python -m unittest discover -s tests -v
```

## 향후 기능

- 해설과 오답 다시 풀기 등 확장 기능
