
from dataclasses import dataclass
from typing import Optional


@dataclass
class Puzzle:
    """
    Represents one Santa 2026 arithmetic puzzle.
    """

    puzzle_id: int
    start_numbers: list[int]
    targets: list[int]
    value_limit: int

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.puzzle_id, int):
            raise TypeError("puzzle_id must be an integer")

        if not self.start_numbers:
            raise ValueError("Puzzle must have starting numbers")

        if not self.targets:
            raise ValueError("Puzzle must have at least one target")

        if not all(isinstance(n, int) for n in self.start_numbers):
            raise TypeError("Starting numbers must be integers")

        if not all(isinstance(n, int) for n in self.targets):
            raise TypeError("Targets must be integers")

        if not all(n > 0 for n in self.start_numbers):
            raise ValueError("Starting numbers must be positive")

        if not all(n > 0 for n in self.targets):
            raise ValueError("Targets must be positive")

        if self.value_limit <= 0:
            raise ValueError("value_limit must be positive")

        if any(n > self.value_limit for n in self.start_numbers):
            raise ValueError("Starting number exceeds value_limit")

        if any(n > self.value_limit for n in self.targets):
            raise ValueError("Target exceeds value_limit")

    @property
    def target_count(self) -> int:
        return len(self.targets)

    def __repr__(self) -> str:
        return (
            f"Puzzle(id={self.puzzle_id}, "
            f"starts={self.start_numbers}, "
            f"targets={self.targets}, "
            f"value_limit={self.value_limit})"
        )
