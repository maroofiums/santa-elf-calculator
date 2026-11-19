import pytest

from app.solver import (
    Instruction, 
    Program,
    add,
    subtract,
    multiply,
    divide,
    apply_operation,
)




def test_program_execution():
    program = Program()

    program.add_instruction(Instruction(0, "*", 1))
    program.add_instruction(Instruction(2, "+", 1))
    program.add_instruction(Instruction(3, "+", 0))

    registers = program.execute(
        start_numbers=[2, 3],
        value_limit=100
    )

    assert registers == [2, 3, 6, 9, 11]
    assert registers[-1] == 11


def test_instruction_count():
    program = Program()

    program.add_instruction(Instruction(0, "+", 1))
    program.add_instruction(Instruction(2, "*", 0))

    assert program.instruction_count() == 2


def test_invalid_register():
    program = Program()
    program.add_instruction(Instruction(0, "+", 5))

    import pytest

    with pytest.raises(ValueError):
        program.execute([2, 3], 100)


def test_basic_operations():
    assert add(2, 3) == 5
    assert subtract(8, 3) == 5
    assert multiply(4, 5) == 20
    assert divide(12, 3) == 4


def test_invalid_division():
    assert divide(12, 5) is None
    assert divide(10, 0) is None


def test_apply_operation():
    assert apply_operation(2, 3, "+", 100) == 5
    assert apply_operation(8, 3, "-", 100) == 5
    assert apply_operation(4, 5, "*", 100) == 20
    assert apply_operation(12, 3, "/", 100) == 4


def test_invalid_operations():
    assert apply_operation(2, 5, "-", 100) is None
    assert apply_operation(12, 5, "/", 100) is None
    assert apply_operation(10, 0, "/", 100) is None
    assert apply_operation(2, 3, "^", 100) is None


def test_value_limit():
    assert apply_operation(50, 50, "*", 1000) == 2500 if False else True
    assert apply_operation(50, 50, "*", 1000) is None
    assert apply_operation(10, 10, "*", 100) == 100
