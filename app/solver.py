from typing import Optional


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Return the product of two integers."""
    return a * b


def divide(a: int, b: int) -> Optional[int]:
    """
    Perform exact integer division.

    Return None if division is invalid.
    """
    if b == 0:
        return None

    if a % b != 0:
        return None

    return a // b


def apply_operation(
    a: int,
    b: int,
    operator: str,
    value_limit: int,
) -> Optional[int]:
    """
    Execute an arithmetic operation under puzzle constraints.

    Returns:
        int: Valid result.
        None: Invalid operation.
    """

    if type(a) is not int or type(b) is not int:
        return None

    if a <= 0 or b <= 0:
        return None

    if value_limit <= 0:
        return None

    if operator == "+":
        result = add(a, b)

    elif operator == "-":
        result = subtract(a, b)

    elif operator == "*":
        result = multiply(a, b)

    elif operator == "/":
        result = divide(a, b)

        if result is None:
            return None

    else:
        return None

    # Enforce positive intermediate values.
    if result <= 0:
        return None

    # Enforce puzzle-specific value limit.
    if result > value_limit:
        return None

    return result
