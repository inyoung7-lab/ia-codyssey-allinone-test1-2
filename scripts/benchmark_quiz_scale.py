"""Measure quiz storage, listing, and sampling with isolated synthetic data.

The benchmark never opens the project-root state.json. Its only state file is
created inside a TemporaryDirectory and removed automatically on exit.
"""

from __future__ import annotations

import argparse
import contextlib
import platform
import random
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable

# Make the repository modules importable when this file is run by path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import show_quizzes
from quiz import Quiz
from state_store import StateStore


class _DiscardOutput:
    """Accept printed quiz text without terminal or buffer I/O."""

    def write(self, value: str) -> int:
        return len(value)

    def flush(self) -> None:
        pass


def _make_quizzes(count: int) -> list[Quiz]:
    return [
        Quiz(
            question=f"Synthetic question {index:04d}",
            choices=[f"Choice {index:04d}-{letter}" for letter in "ABCD"],
            answer=(index % 4) + 1,
            hint=f"Synthetic hint {index:04d}",
        )
        for index in range(count)
    ]


def _measure(
    operation: Callable[[], None], repetitions: int, warmups: int
) -> tuple[float, float, float]:
    for _ in range(warmups):
        operation()

    samples: list[float] = []
    for _ in range(repetitions):
        started = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - started) * 1000)
    return statistics.median(samples), min(samples), max(samples)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--warmups", type=int, default=3)
    args = parser.parse_args()
    if args.count < 1 or args.repetitions < 1 or args.warmups < 0:
        parser.error("count/repetitions must be positive and warmups non-negative")

    quizzes = _make_quizzes(args.count)
    noop = lambda _message: None

    with tempfile.TemporaryDirectory(prefix="quiz-benchmark-") as directory:
        state_path = Path(directory) / "state.json"
        store = StateStore(state_path)
        store.quizzes = quizzes

        def save_state() -> None:
            if not store.save(noop):
                raise RuntimeError("temporary benchmark state could not be saved")

        save_state()

        def load_state() -> None:
            loaded = StateStore(state_path)
            loaded.load(noop)
            if len(loaded.quizzes) != args.count:
                raise RuntimeError("loaded quiz count differs from synthetic input")

        def traverse_list() -> None:
            with contextlib.redirect_stdout(_DiscardOutput()):
                show_quizzes(quizzes, noop)

        def random_selection() -> None:
            selected = random.sample(quizzes, min(15, args.count))
            if len({id(quiz) for quiz in selected}) != len(selected):
                raise RuntimeError("random sample unexpectedly contains duplicates")

        operations = (
            ("save", save_state),
            ("load", load_state),
            ("list traversal/rendering", traverse_list),
            ("random sample (up to 15)", random_selection),
        )

        print(f"Python: {platform.python_version()}")
        print(f"Platform: {platform.platform()}")
        print(f"Synthetic quizzes: {args.count}")
        print(f"Warmups: {args.warmups}; measured repetitions: {args.repetitions}")
        print("Times in milliseconds (median; min-max):")
        for name, operation in operations:
            median, minimum, maximum = _measure(
                operation, args.repetitions, args.warmups
            )
            print(f"  {name}: {median:.3f}; {minimum:.3f}-{maximum:.3f}")
        print("State file: temporary directory only; removed on exit")


if __name__ == "__main__":
    main()
