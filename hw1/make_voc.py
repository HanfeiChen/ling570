#!/usr/bin/python3

import sys
from collections import defaultdict

counter = defaultdict(int)

for line in sys.stdin:
    l = line.split()
    for word in l:
        counter[word] += 1

for word, count in counter.items():
    print(word, count, sep='\t')
