import json
from collections import Counter

for mode in ["base", "bonus"]:
    path = f"games/LemonLabs_1_96/library/books/books_{mode}.json"

    try:
        with open(path) as f:
            data = json.load(f)

        sims = data if isinstance(data, list) else data.get("sims", data.get("books", []))

        total = len(sims)
        max_wins = 0
        block_counts = Counter()
        multiplier_totals = []
        high_win_events = []

        for s in sims:
            payout = s.get("payoutMultiplier", 0) / 100
            events = s.get("events", [])

            if payout >= 5000:
                max_wins += 1

            # find wildMultiplier and wildBlock events
            wild_mult = None
            blocks = []
            for e in events:
                if e.get("type") == "wildMultiplier":
                    wild_mult = e.get("totalMultiplier", 1)
                if e.get("type") == "wildBlock":
                    blocks.append({
                        "size": e.get("finalSize"),
                        "mult": e.get("multiplier"),
                        "grew": e.get("grewFrom"),
                    })

            if wild_mult:
                multiplier_totals.append(wild_mult)

            for b in blocks:
                block_counts[f"{b['size']}x{b['size']}"] += 1

            # log high wins for inspection
            if payout > 100 and len(high_win_events) < 5:
                high_win_events.append({
                    "payout": payout,
                    "wildMultiplier": wild_mult,
                    "blocks": blocks,
                })

        print(f"--- {mode} ---")
        print(f"Total sims        : {total}")
        print(f"Max wins (5000x)  : {max_wins} ({max_wins/total*100:.1f}%)")
        print()
        print("Block hit counts:")
        for k, v in sorted(block_counts.items()):
            print(f"  {k} : {v} ({v/total*100:.1f}%)")
        print()
        if multiplier_totals:
            print(f"Wild multiplier stats (when triggered):")
            print(f"  Count   : {len(multiplier_totals)}")
            print(f"  Average : {sum(multiplier_totals)/len(multiplier_totals):.1f}x")
            print(f"  Max     : {max(multiplier_totals)}x")
            print(f"  Min     : {min(multiplier_totals)}x")
        print()
        print("Sample high wins (>100x):")
        for h in high_win_events:
            print(f"  payout={h['payout']:.1f}x  wildMult={h['wildMultiplier']}  blocks={h['blocks']}")
        print()

    except FileNotFoundError:
        print(f"--- {mode} --- FILE NOT FOUND at {path}")
    except Exception as e:
        print(f"--- {mode} --- ERROR: {e}")