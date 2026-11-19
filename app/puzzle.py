import csv, json

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
    registers: int = 40

    family: Optional[str] = None
    design_tier: Optional[str] = None
    lower_bound: Optional[str] = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.puzzle_id, str) or not self.puzzle_id:
            raise ValueError("Puzzle ID must be a non-empty string")

        if not self.start_numbers:
            raise ValueError("Puzzle must have starting values")

        if not self.targets:
            raise ValueError("Puzzle must have at least one target")

        if not all(type(n) is int for n in self.start_numbers):
            raise TypeError("Starting values must be integers")

        if not all(type(n) is int for n in self.targets):
            raise TypeError("Targets must be integers")

        if any(n <= 0 for n in self.start_numbers):
            raise ValueError("Starting values must be positive")

        if any(n <= 0 for n in self.targets):
            raise ValueError("Targets must be positive")

        if type(self.value_limit) is not int or self.value_limit <= 0:
            raise ValueError("value_limit must be a positive integer")

        if type(self.registers) is not int or self.registers <= 0:
            raise ValueError("registers must be a positive integer")

        if len(self.start_numbers) > self.registers:
            raise ValueError("More starting values than available registers")

        if any(n > self.value_limit for n in self.start_numbers):
            raise ValueError("Starting value exceeds value_limit")

        if any(n > self.value_limit for n in self.targets):
            raise ValueError("Target exceeds value_limit")

        if self.lower_bound is not None:
            if type(self.lower_bound) is not int or self.lower_bound < 0:
                raise ValueError("lower_bound must be a non-negative integer")


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
    path: Path = PUZZLES_FILE,
) -> list[Puzzle]:
    """
    Load all puzzles from a competition or practice CSV.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Puzzle dataset not found: {path}")

    puzzles = []

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "id",
            "starting_values",
            "targets",
            "value_limit",
            "registers",
        }

        if reader.fieldnames is None:
            raise ValueError("Dataset has no CSV header")

        missing = required_columns - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}"
            )

        for row in reader:
            puzzles.append(_parse_puzzle_row(row))


        puzzle_ids = [puzzle.puzzle_id for puzzle in puzzles]

    if len(puzzle_ids) != len(set(puzzle_ids)):
        raise ValueError("Dataset contains duplicate puzzle IDs")

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
) -> Puzzle:
    """
    Load one puzzle by its ID.
    """

    puzzles = load_puzzles(file_path)

    for puzzle in puzzles:
        if puzzle.puzzle_id == puzzle_id:
            return puzzle

    raise KeyError(f"Puzzle not found: {puzzle_id}")


def _parse_integer_list(
    value: str,
    field_name: str
) -> list[int]:

    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"Invalid JSON in '{field_name}'") from exc

    if not isinstance(parsed, list):
        raise ValueError(f"'{field_name}' must contain a JSON list")

    if not all(type(item) is int for item in parsed):
        raise ValueError(f"'{field_name}' must contain only integers")

    return parsed


def _parse_puzzle_row(row: dict) -> Puzzle:
    try:
        return Puzzle(
            puzzle_id=row["id"],
            start_numbers=_parse_integer_list(
                row["starting_values"],
                "starting_values",
            ),
            targets=_parse_integer_list(
                row["targets"],
                "targets",
            ),
            value_limit=int(row["value_limit"]),
            registers=int(row["registers"]),
            family=row.get("family") or None,
            design_tier=row.get("design_tier") or None,
            lower_bound=(
                int(row["lower_bound"])
                if row.get("lower_bound")
                else None
            ),
        )
    
    except (KeyError, TypeError, ValueError) as exc:
        puzzle_id = row.get("id", "unknown")
        raise ValueError(
            f"Failed to parse puzzle '{puzzle_id}': {exc}"
        ) from exc