
import pytest

from app.solver import Instruction, Program, apply_operation


def test_arithmetic_operations():
    assert apply_operation(2, 3, "+", 100) == 5
    assert apply_operation(8, 3, "-", 100) == 5
    assert apply_operation(4, 5, "*", 100) == 20
    assert apply_operation(12, 3, "/", 100) == 4


def test_invalid_operations():
    assert apply_operation(2, 5, "-", 100) is None
    assert apply_operation(12, 5, "/", 100) is None
    assert apply_operation(10, 0, "/", 100) is None
    assert apply_operation(2, 3, "^", 100) is None


def test_program_execution():
    program = Program([
        Instruction("*", 0, 1, 2),
        Instruction("+", 2, 1, 3),
        Instruction("+", 3, 0, 2),
    ])

    result = program.execute(
        start_numbers=[2, 3],
        value_limit=100,
        targets=[11],
        register_count=4,
    )

    assert result.registers == [2, 3, 11, 9]
    assert result.all_targets_found


def test_register_overwriting():
    program = Program([
        Instruction("+", 0, 1, 0),
    ])

    result = program.execute(
        start_numbers=[2, 3],
        value_limit=100,
        register_count=4,
    )

    assert result.registers[0] == 5


def test_target_tracking_after_overwrite():
    program = Program([
        Instruction("+", 0, 1, 2),
        Instruction("*", 0, 1, 2),
    ])

    result = program.execute(
        start_numbers=[2, 3],
        value_limit=100,
        targets=[5],
        register_count=4,
    )

    assert result.registers[2] == 6
    assert result.all_targets_found


def test_uninitialized_register():
    program = Program([
        Instruction("+", 0, 2, 1),
    ])

    with pytest.raises(ValueError):
        program.execute([2], 100, register_count=4)


def test_register_out_of_range():
    program = Program([
        Instruction("+", 0, 1, 48),
    ])

    with pytest.raises(ValueError):
        program.execute([2, 3], 100, register_count=4)
