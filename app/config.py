from pathlib import Path

# Project Paths

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

PUZZLES_FILE = DATA_DIR / "puzzles.csv"
SAMPLE_SUBMISSION_FILE = DATA_DIR / "sample_submission.csv"

SUBMISSION_FILE = OUTPUT_DIR / "submission.csv"


# Competition Constraints

MAX_REGISTERS = 48
MAX_INSTRUCTIONS = 4096
MAX_PROGRAM_BYTES = 131_072
DEFAULT_VALUE_LIMIT = None


# Arithmetic Operations

OPERATIONS = ("+", "-", "*", "/")


# Solver Configuration

SOLVER_CONFIG = {
    "max_targets_per_puzzle": None,
    "use_greedy": True,
    "allow_intermediate_values": True,
    "integer_division_only": True,
    "positive_values_only": True,
}


# Execution Configuration

RANDOM_SEED = 42
VERBOSE = True
BATCH_SIZE = 100
