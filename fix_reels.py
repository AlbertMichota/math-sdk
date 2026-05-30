import random
random.seed(99)

# replace 60% of H1/H2, 40% of H3/H4/W
replacements = {
    'H1': 'L4',
    'H2': 'L5',
    'H3': 'L5',
    'H4': 'L5',
    'W':  'L3',   # reduce wilds too — fewer wilds = fewer block triggers
}
replace_rates = {
    'H1': 0.6,
    'H2': 0.6,
    'H3': 0.4,
    'H4': 0.4,
    'W':  0.4,
}

for filename in ['BR0', 'FR0', 'FRWCAP']:
    try:
        with open(f'games/LemonLabs_1_96/reels/{filename}.csv') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            cols = line.strip().split(',')
            new_cols = []
            for sym in cols:
                rate = replace_rates.get(sym, 0)
                if rate and random.random() < rate:
                    new_cols.append(replacements[sym])
                else:
                    new_cols.append(sym)
            new_lines.append(','.join(new_cols) + '\n')
        with open(f'games/LemonLabs_1_96/reels/{filename}.csv', 'w') as f:
            f.writelines(new_lines)
        print(f'Updated {filename}.csv')
    except FileNotFoundError:
        print(f'{filename}.csv not found')