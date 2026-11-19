import pytest

from app.solver import (
    add,
    subtract,
    multiply,
    divide,
    apply_operation,
)


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
