from dataclasses import dataclass, field
from typing import Optional

from app.puzzle import Puzzle
from app.solver import Program


# Validation Result

@dataclass
class ValidationResult:
    valid: bool
    solved: bool
    targets_found: int
    target_count: int
    missing_targets: list[int] = field(default_factory=list)
    instruction_count: int = 0
    final_registers: list[Optional[int]] = field(default_factory=list)
    error: Optional[str] = None


# Program Validator

def validate_program(
    puzzle: Puzzle,
    program: Program,
) -> ValidationResult:
    """
    Validate and execute a program against a puzzle.

    valid:
        All instructions execute without violating
        arithmetic or register constraints.

    solved:
        Every target was generated at least once.
    """

    if not isinstance(puzzle, Puzzle):
        raise TypeError("puzzle must be a Puzzle instance")

    if not isinstance(program, Program):
        raise TypeError("program must be a Program instance")

    try:
        execution = program.execute(
            start_numbers=puzzle.start_numbers,
            value_limit=puzzle.value_limit,
            targets=puzzle.targets,
            register_count=puzzle.registers,
        )

    except (ValueError, TypeError) as exc:
        return ValidationResult(
            valid=False,
            solved=False,
            targets_found=0,
            target_count=puzzle.target_count,
            missing_targets=list(puzzle.targets),
            instruction_count=len(program.instructions),
            error=str(exc),
        )

    missing_targets = [
        target
        for target in puzzle.targets
        if target not in execution.targets_seen
    ]

    targets_found = puzzle.target_count - len(missing_targets)

    return ValidationResult(
        valid=True,
        solved=not missing_targets,
        targets_found=targets_found,
        target_count=puzzle.target_count,
        missing_targets=missing_targets,
        instruction_count=execution.instruction_count,
        final_registers=execution.registers,
    )
