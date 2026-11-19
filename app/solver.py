from typing import Optional
from dataclasses import dataclass, field

from app.config import MAX_INSTRUCTIONS, MAX_REGISTERS

@dataclass(frozen=True)
class Instruction:
    """
    One Elf Calculator instruction.

    Example:
        Instruction("*", 0, 1, 2)

    Means:
        R2 = R0 * R1
    """

    operator: str
    left: int
    right: int
    destination: int

    def __post_init__(self):
        if self.operator not in ("+", "-", "*", "/"):
            raise ValueError("Unsupported operator")

        if any(
            type(index) is not int or index < 0
            for index in (self.left, self.right, self.destination)
        ):
            raise ValueError("Register indices must be non-negative integers")

    def to_list(self) -> list:
        return [
            self.operator,
            self.left,
            self.right,
            self.destination,
        ]
    
@dataclass
class ExecutionResult:
    registers: list[Optional[int]]
    targets_seen: set[int]
    instruction_count: int

    @property
    def all_targets_found(self) -> bool:
        return self.missing_targets == set()

    @property
    def missing_targets(self) -> set[int]:
        return self._required_targets - self.targets_seen

    _required_targets: set[int] = field(
        default_factory=set,
        repr=False
    )
    

@dataclass
class Program:
    """
    Stores and executes a sequence of arithmetic instructions.
    """

    instructions: list[Instruction] = field(default_factory=list)

    def add_instruction(self, instruction: Instruction) -> None:
        if len(self.instructions) >= MAX_INSTRUCTIONS:
            raise ValueError("Maximum Instruction limit exceeded")
        
        self.instructions.append(instruction)

    def to_list(self) -> list[list]:
        return [
            instruction.to_list()
            for instruction in self.instructions
        ]


    def execute(
        self,
        start_numbers: list[int],
        value_limit: int,
        targets: Optional[list[int]] = None,
        register_count: int = MAX_REGISTERS,
    ) -> ExecutionResult:
        """
        Execute the program using reusable registers.

        Starting values occupy R0, R1, R2, ...
        Every instruction writes to its destination register.
        """

        if type(register_count) is not int:
            raise ValueError("Invalid regiister count")

        if not 1 <= register_count <= MAX_REGISTERS:
            raise ValueError("Invalid Register Count")

        if len(start_numbers) > register_count:
            raise ValueError("Too many starting values")

        if len(self.instructions) > MAX_INSTRUCTIONS:
            raise ValueError("Maximum instruction limit exceeded")

        

        registers: list[Optional[int]] = [None] * register_count

        for idx, value in enumerate(start_numbers):

            if type(value) is not int or value <= 0:
                raise ValueError("Invalid starting value")

            if value > value_limit:
                raise ValueError("Starting value exceeds `value_limit`")

            registers[idx] = value

        required_targets = set(targets or [])

        targets_seen = {
            value
            for value in start_numbers
            if value in required_targets
        }

        for instruction in self.instructions:

            indices = (
                instruction.left,
                instruction.right,
                instruction.destination
            )

            if any(
                idx  >= register_count
                for idx in indices
            ):
                raise ValueError(
                    "Register index out of range"
                )

            a = registers[instruction.left]
            b = registers[instruction.right]

            if a is None or b is None:
                raise ValueError("Reading a uninitialized register")
            
            result = apply_operation(
                a,
                b,
                instruction.operator,
                value_limit,
            )

            if result is None:
                raise ValueError("Invalid arithmetic instruction")

            registers[instruction.destination] = result

            if result in required_targets:
                targets_seen.add(result)
    
        return ExecutionResult(
            registers=registers,
            targets_seen=targets_seen,
            instruction_count=self.instruction_count(),
            _required_targets=required_targets
        )
    

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
