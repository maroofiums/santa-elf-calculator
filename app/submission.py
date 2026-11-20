import csv
import json

from pathlib import Path

from app.config import SAMPLE_SUBMISSION_FILE
from app.solver import Instruction, Program


def load_submission(
    path: Path = SAMPLE_SUBMISSION_FILE,
) -> dict[str, Program]:
    """
    Load submission CSV into a mapping:

        puzzle_id -> Program
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Submission file not found: {path}"
        )

    programs = {}

    with path.open(
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {"id", "program"}

        if reader.fieldnames is None:
            raise ValueError("Submission CSV has no header")

        missing = required_columns - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Submission CSV missing columns: {sorted(missing)}"
            )

        for row in reader:
            puzzle_id = row["id"]

            if not puzzle_id:
                raise ValueError("Empty puzzle ID")

            if puzzle_id in programs:
                raise ValueError(
                    f"Duplicate submission ID: {puzzle_id}"
                )

            try:
                instructions = json.loads(row["program"])
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid program JSON for {puzzle_id}"
                ) from exc

            if not isinstance(instructions, list):
                raise ValueError(
                    f"Program for {puzzle_id} must be a list"
                )

            parsed_instructions = []

            for index, item in enumerate(instructions):
                if (
                    not isinstance(item, list)
                    or len(item) != 4
                ):
                    raise ValueError(
                        f"Invalid instruction {index} in {puzzle_id}"
                    )

                try:
                    parsed_instructions.append(
                        Instruction(
                            operator=item[0],
                            left=item[1],
                            right=item[2],
                            destination=item[3],
                        )
                    )
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid instruction {index} in {puzzle_id}: {exc}"
                    ) from exc

            programs[puzzle_id] = Program(parsed_instructions)

    return programs


def save_submission(
    programs: dict[str, Program],
    path: Path,
) -> None:
    """
    Save programs in competition submission format.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["id", "program"],
        )

        writer.writeheader()

        for puzzle_id, program in programs.items():
            writer.writerow({
                "id": puzzle_id,
                "program": json.dumps(
                    program.to_list(),
                    separators=(",", ":"),
                ),
            })
