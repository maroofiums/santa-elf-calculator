
import pytest

from app.puzzle import Puzzle
from app.solver import Program, Instruction
from app.validator import validate_program


@pytest.fixture
def puzzle():
    return Puzzle(
        puzzle_id="test_001",
        start_numbers=[2, 3],
        targets=[5, 6, 9],
        value_limit=100,
        registers=4,
    )


# Successful Validation

def test_valid_program_solves_all_targets():
    puzzle = Puzzle(
        puzzle_id="test_002",
        start_numbers=[2, 3],
        targets=[5, 6],
        value_limit=100,
        registers=4,
    )

    program = Program([
        Instruction("+", 0, 1, 2),
        Instruction("*", 0, 1, 3),
    ])

    result = validate_program(puzzle, program)

    assert result.valid is True
    assert result.solved is True
    assert result.targets_found == 2
    assert result.missing_targets == []


# Partial Solution

def test_valid_program_can_have_missing_targets(puzzle):
    program = Program([
        Instruction("+", 0, 1, 2),
    ])

    result = validate_program(puzzle, program)

    assert result.valid is True
    assert result.solved is False
    assert result.targets_found == 1
    assert result.missing_targets == [6, 9]


# Invalid Arithmetic

def test_non_integer_division_is_rejected(puzzle):
    program = Program([
        Instruction("/", 0, 1, 2),
    ])

    result = validate_program(puzzle, program)

    assert result.valid is False
    assert result.solved is False
    assert result.error is not None


# Register Validation

def test_uninitialized_register_is_rejected(puzzle):
    program = Program([
        Instruction("+", 0, 3, 2),
    ])

    result = validate_program(puzzle, program)

    assert result.valid is False
    assert "uninitialized" in result.error.lower()


def test_out_of_range_register_is_rejected(puzzle):
    program = Program([
        Instruction("+", 0, 1, 4),
    ])

    result = validate_program(puzzle, program)

    assert result.valid is False
    assert "out of range" in result.error.lower()


# Target Tracking

def test_target_is_tracked_after_register_overwrite():
    puzzle = Puzzle(
        puzzle_id="test_003",
        start_numbers=[2, 3],
        targets=[5],
        value_limit=100,
        registers=4,
    )

    program = Program([
        Instruction("+", 0, 1, 2),  # R2 = 5
        Instruction("*", 0, 1, 2),  # R2 = 6 (overwrite)
    ])

    result = validate_program(puzzle, program)

    assert result.valid is True
    assert result.solved is True
    assert result.targets_found == 1


# Input Validation

def test_invalid_puzzle_type():
    with pytest.raises(TypeError):
        validate_program("not a puzzle", Program())


def test_invalid_program_type(puzzle):
    with pytest.raises(TypeError):
        validate_program(puzzle, "not a program")
