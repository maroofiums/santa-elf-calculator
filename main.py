from app.puzzle import Puzzle

puzzle = Puzzle(
    puzzle_id=1,
    start_numbers=[2, 3],
    targets=[11, 15, 21],
    value_limit=1000
)

print(puzzle)
print("Number of targets:", puzzle.target_count)