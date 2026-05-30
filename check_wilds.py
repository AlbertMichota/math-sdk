import json
from collections import Counter

path = "games/LemonLabs_1_96/library/books/books_base.json"

with open(path) as f:
    data = json.load(f)

sims = data if isinstance(data, list) else data.get("sims", data.get("books", []))

wild_counts = Counter()
board_sizes = Counter()
has_wildblock = 0
has_wildmult = 0

for s in sims:
    events = s.get("events", [])
    for e in events:
        if e.get("type") == "reveal":
            board = e.get("board", [])
            num_reels = len(board)
            num_rows = len(board[0]) if board else 0
            board_sizes[f"{num_reels}x{num_rows}"] += 1
            wild_count = sum(
                1
                for reel in board
                for sym in reel
                if sym.get("name") == "W"
            )
            wild_counts[wild_count] += 1
        if e.get("type") == "wildBlock":
            has_wildblock += 1
        if e.get("type") == "wildMultiplier":
            has_wildmult += 1

print("Board sizes seen:")
for k, v in board_sizes.items():
    print(f"  {k} : {v} spins")

print()
print("Wild count per spin:")
for k in sorted(wild_counts.keys()):
    print(f"  {k} wilds : {wild_counts[k]} spins")

print()
print(f"Spins with wildBlock event   : {has_wildblock}")
print(f"Spins with wildMultiplier    : {has_wildmult}")