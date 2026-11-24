from typing import Optional
from dataclasses import dataclass, field

from app.puzzle import Puzzle
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



# Baseline Puzzle Solver

def _find_direct_instruction(
    known: dict[int, int],
    target: int,
    value_limit: int,
    ) -> Optional[Instruction]:
    """Find one instruction that generates the target."""

    registers = list(known.items())

    for left_index, left_value in registers:
        for right_index, right_value in registers:

            for operator in ("+", "-", "*", "/"):
                result = apply_operation(
                    left_value,
                    right_value,
                    operator,
                    value_limit,
                )

                if result == target:
                    return Instruction(
                        operator,
                        left_index,
                        right_index,
                        0,  # Destination is assigned by solve_puzzle.
                    )

    return None


def _find_two_step_solution(
    known: dict[int, int],
    target: int,
    value_limit: int,
    scratch_register: int,
    ) -> Optional[tuple[Instruction, Instruction]]:
    """
    Search for:
        existing values -> intermediate -> target

    The intermediate is written to a temporary register.
    """

    registers = list(known.items())

    for left_index, left_value in registers:
        for right_index, right_value in registers:

            for operator in ("+", "-", "*", "/"):
                intermediate = apply_operation(
                    left_value,
                    right_value,
                    operator,
                    value_limit,
                )

                if intermediate is None:
                    continue

                if intermediate in known.values():
                    continue

                for existing_index, existing_value in registers:

                    combinations = (
                        (intermediate, existing_value),
                        (existing_value, intermediate),
                    )

                    for second_left, second_right in combinations:
                        for second_operator in ("+", "-", "*", "/"):

                            result = apply_operation(
                                second_left,
                                second_right,
                                second_operator,
                                value_limit,
                            )

                            if result == target:

                                first = Instruction(
                                    operator,
                                    left_index,
                                    right_index,
                                    scratch_register,
                                )

                                if second_left == intermediate:
                                    second = Instruction(
                                        second_operator,
                                        scratch_register,
                                        existing_index,
                                        0,
                                    )
                                else:
                                    second = Instruction(
                                        second_operator,
                                        existing_index,
                                        scratch_register,
                                        0,
                                    )

                                return first, second

    return None



def solve_puzzle(puzzle: Puzzle) -> Program:
    """
    Generate every target using binary construction.

    R4 stores the constant 1.
    R5 is the reusable accumulator.
    """

    if puzzle.registers < 6:
        raise ValueError("Binary solver requires at least 6 registers")

    if not puzzle.start_numbers or puzzle.start_numbers[0] <= 0:
        raise ValueError("A positive starting value is required")

    program = Program()

    # Create constant 1: R4 = R0 / R0
    program.add_instruction(
        Instruction("/", 0, 0, 4)
    )

    for target in sorted(set(puzzle.targets)):

        if target <= 0 or target > puzzle.value_limit:
            raise ValueError(f"Invalid target: {target}")

        # Reset accumulator to 1.
        program.add_instruction(
            Instruction("*", 4, 4, 5)
        )

        # Construct target using its binary representation.
        binary = bin(target)[3:]

        for bit in binary:

            # Double current value.
            program.add_instruction(
                Instruction("+", 5, 5, 5)
            )

            # Add 1 when the next binary bit is 1.
            if bit == "1":
                program.add_instruction(
                    Instruction("+", 5, 4, 5)
                )

    return program
