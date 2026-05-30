import csv

for mode in ["base", "bonus"]:
    path = f"games/LemonLabs_1_96/library/lookup_tables/lookUpTable_{mode}.csv"
    try:
        total = 0
        in_profit = 0
        zero_win = 0
        total_payout = 0

        with open(path) as f:
            for row in csv.reader(f):
                total += 1
                payout = float(row[2]) / 100
                total_payout += payout
                if payout > 1.0:
                    in_profit += 1
                elif payout == 0:
                    zero_win += 1

        print(f"--- {mode} ---")
        print(f"Total sims : {total}")
        print(f"Raw RTP    : {total_payout/total*100:.2f}%")
        print(f"In profit  : {in_profit} ({in_profit/total*100:.1f}%)")
        print(f"Zero win   : {zero_win} ({zero_win/total*100:.1f}%)")
        print(f"Small win  : {total - in_profit - zero_win} ({(total-in_profit-zero_win)/total*100:.1f}%)")
        print()

    except FileNotFoundError:
        print(f"--- {mode} --- FILE NOT FOUND")
        print()