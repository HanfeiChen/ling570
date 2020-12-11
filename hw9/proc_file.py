#!/usr/bin/env python3

import os
import sys
from collections import Counter

INPUT_FILE, TARGET_LABEL, OUTPUT_FILE = sys.argv[1:4]

def clean_line(line):
    return ''.join(c.lower() if c.isalpha() else ' ' for c in line)


def process_file(input_file, output_file, target_label):
    instance_name = os.path.basename(input_file)

    token_counter = Counter()

    with open(input_file, 'r') as in_file:
        header = True
        for line in in_file:
            if header:
                if len(line.strip()) == 0:
                    header = False
                continue
            line = line.strip()
            line = clean_line(line)
            token_counter.update(line.split())

    with open(output_file, 'w') as out_file:
        out_file.write("{} {}".format(instance_name, target_label))
        for feat, value in sorted(token_counter.items()):
            out_file.write(" {} {}".format(feat, value))
        out_file.write("\n")


process_file(INPUT_FILE, OUTPUT_FILE, TARGET_LABEL)
