from app.puzzle import load_puzzles, load_puzzle

puzzles = load_puzzles("tests/data/sample.csv")

print("Total puzzles:", len(puzzles))

for puzzle in puzzles:
    print(puzzle)

first = load_puzzle(1, "tests/data/sample.csv")

print("Selected puzzle:", first)