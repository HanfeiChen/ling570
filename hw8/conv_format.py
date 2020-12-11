#!/usr/bin/env python3

import sys

for line in sys.stdin:
    if len(line.strip()) > 0:
        left, right = line.strip().split('=>')
        symbols = left.strip().split()
        states = right.strip().split()[1:-1]
        pos = [state.split('_')[1] for state in states]
        output_parts = ['{}/{}'.format(symbol, pos) for symbol, pos in zip(symbols, pos)]
        print(' '.join(output_parts))
