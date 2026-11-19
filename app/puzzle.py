import csv 

from pathlib import Path 
from dataclasses import dataclass
from typing import Optional

from app.config import PUZZLES_FILE



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


def load_puzzles(
    file_path: Path = PUZZLES_FILE,
    id_column: str = "id",
    starts_column: str = "start_numbers",
    targets_column: str = "targets",
    limit_column: str = "value_limit",
) -> list[Puzzle]:
    """
    Load puzzles from a CSV file.

    Expected format:
        id,start_numbers,targets,value_limit

    Example:
        1,"[2,3]","[11,15,21]",1000
    """

    puzzles = []

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    with file_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {
            id_column,
            starts_column,
            targets_column,
            limit_column,
        }

        available_columns = set(reader.fieldnames or [])
        missing = required_columns - available_columns

        if missing:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}. "
                f"Available columns: {sorted(available_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                puzzle = Puzzle(
                    puzzle_id=int(row[id_column]),
                    start_numbers=parse_integer_list(row[starts_column]),
                    targets=parse_integer_list(row[targets_column]),
                    value_limit=int(row[limit_column]),
                )

                puzzles.append(puzzle)

            except (ValueError, TypeError) as error:
                raise ValueError(
                    f"Invalid puzzle at CSV row {row_number}: {error}"
                ) from error

    return puzzles


def parse_integer_list(value: str) -> list[int]:
    """
    Parse a CSV field containing a JSON-style integer list.
    """

    import json

    try:
        result = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid integer list: {value}") from error

    if not isinstance(result, list):
        raise ValueError("Expected a list")

    if not all(type(number) is int for number in result):
        raise ValueError("List must contain only integers")

    return result


def load_puzzle(
    puzzle_id: int,
    file_path: Path = PUZZLES_FILE,
) -> Optional[Puzzle]:
    """
    Load one puzzle by its ID.
    """

    puzzles = load_puzzles(file_path)

    for puzzle in puzzles:
        if puzzle.puzzle_id == puzzle_id:
            return puzzle

    return None
