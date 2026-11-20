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




@dataclass
class SubmissionEvaluation:
    total_puzzles: int
    evaluated_puzzles: int
    valid_programs: int
    solved_puzzles: int
    targets_found: int
    total_targets: int
    total_instructions: int

    missing_programs: list[str] = field(default_factory=list)
    extra_programs: list[str] = field(default_factory=list)
    invalid_programs: dict[str, str] = field(default_factory=dict)

    @property
    def target_coverage(self) -> float:
        if self.total_targets == 0:
            return 0.0

        return self.targets_found / self.total_targets

    @property
    def fully_solved_rate(self) -> float:
        if self.total_puzzles == 0:
            return 0.0

        return self.solved_puzzles / self.total_puzzles


def evaluate_submission(
    puzzles: list[Puzzle],
    programs: dict[str, Program],
) -> SubmissionEvaluation:
    """
    Evaluate a complete submission against a puzzle dataset.
    """

    puzzle_map = {
        puzzle.puzzle_id: puzzle
        for puzzle in puzzles
    }

    missing_programs = [
        puzzle_id
        for puzzle_id in puzzle_map
        if puzzle_id not in programs
    ]

    extra_programs = [
        puzzle_id
        for puzzle_id in programs
        if puzzle_id not in puzzle_map
    ]

    valid_programs = 0
    solved_puzzles = 0
    targets_found = 0
    total_targets = 0
    total_instructions = 0

    invalid_programs = {}

    for puzzle_id, puzzle in puzzle_map.items():

        total_targets += puzzle.target_count

        program = programs.get(puzzle_id)

        if program is None:
            continue

        total_instructions += len(program.instructions)

        result = validate_program(puzzle, program)

        if not result.valid:
            invalid_programs[puzzle_id] = result.error or "Unknown error"
            continue

        valid_programs += 1
        targets_found += result.targets_found

        if result.solved:
            solved_puzzles += 1

    return SubmissionEvaluation(
        total_puzzles=len(puzzles),
        evaluated_puzzles=len(puzzle_map) - len(missing_programs),
        valid_programs=valid_programs,
        solved_puzzles=solved_puzzles,
        targets_found=targets_found,
        total_targets=total_targets,
        total_instructions=total_instructions,
        missing_programs=missing_programs,
        extra_programs=extra_programs,
        invalid_programs=invalid_programs,
    )


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
