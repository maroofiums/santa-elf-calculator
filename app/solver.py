from typing import Optional

from dataclasses import dataclass, field


@dataclass
class Instruction:
    """
    Represents one arithmetic instruction.

    Example:
        Instruction(left=0, operator="+", right=1)

    Means:
        register[2] = register[0] + register[1]
    """

    left: int
    operator: str
    right: int

    def __post_init__(self):
        if self.left < 0 or self.right < 0:
            raise ValueError("Register indices cannot be negative")

        if self.operator not in ("+", "-", "*", "/"):
            raise ValueError(f"Invalid operator: {self.operator}")


@dataclass
class Program:
    """
    Stores and executes a sequence of arithmetic instructions.
    """

    instructions: list[Instruction] = field(default_factory=list)

    def add_instruction(self, instruction: Instruction) -> None:
        self.instructions.append(instruction)

    def execute(
        self,
        start_numbers: list[int],
        value_limit: int,
    ) -> list[int]:
        """
        Execute instructions sequentially.

        Every new result is appended to the register list.
        """

        registers = list(start_numbers)

        for instruction in self.instructions:

            if instruction.left >= len(registers):
                raise ValueError("Left register does not exist")

            if instruction.right >= len(registers):
                raise ValueError("Right register does not exist")

            a = registers[instruction.left]
            b = registers[instruction.right]

            result = apply_operation(
                a,
                b,
                instruction.operator,
                value_limit,
            )

            if result is None:
                raise ValueError("Invalid arithmetic instruction")

            registers.append(result)

        return registers

    def instruction_count(self) -> int:
        return len(self.instructions)


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
