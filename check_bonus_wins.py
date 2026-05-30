import json

for mode in ["base", "bonus"]:
    path = f"games/LemonLabs_1_96/library/books/books_{mode}.json"

    try:
        with open(path) as f:
            data = json.load(f)

        # handle both list format and wrapped format
        sims = data if isinstance(data, list) else data.get("sims", data.get("books", []))

        wins = sorted(
            [s.get("payoutMultiplier", 0) / 100 for s in sims],
            reverse=True
        )

        print(f"--- {mode} ---")
        print(f"Total sims : {len(wins)}")
        print(f"Average win: {sum(wins)/len(wins):.2f}x")
        print(f"Max win    : {wins[0]:.2f}x")
        print(f"Min win    : {wins[-1]:.2f}x")
        print()
        print("Top 10 wins:")
        for i, w in enumerate(wins[:10]):
            print(f"  #{i+1}: {w:.2f}x")
        print()
        print("Win distribution:")
        brackets = [0, 1, 2, 5, 10, 25, 50, 100, 500, 1000, 5000]
        for i in range(len(brackets) - 1):
            lo, hi = brackets[i], brackets[i+1]
            count = sum(1 for w in wins if lo <= w < hi)
            print(f"  {lo:>6}x - {hi:>6}x : {count:>5} ({count/len(wins)*100:.1f}%)")
        print()

    except FileNotFoundError:
        print(f"--- {mode} --- FILE NOT FOUND at {path}")
    except Exception as e:
        print(f"--- {mode} --- ERROR: {e}")