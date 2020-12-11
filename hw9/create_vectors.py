#!/usr/bin/env python3

import os
import sys
import math
from collections import Counter

TRAIN_VECTOR_FILE, TEST_VECTOR_FILE, RATIO = sys.argv[1:4]
RATIO = float(RATIO)
DIRS = sys.argv[4:]


def clean_line(line):
    return ''.join(c.lower() if c.isalpha() or c.isspace() else ' ' for c in line)


def process_file(input_file, target_label):
    # instance_name = os.path.basename(input_file)
    instance_name = input_file

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

    out_line = "{} {}".format(instance_name, target_label)
    for feat, value in sorted(token_counter.items()):
        out_line += " {} {}".format(feat, value)
    out_line += "\n"
    return out_line


if os.path.exists(TRAIN_VECTOR_FILE):
    os.remove(TRAIN_VECTOR_FILE)

if os.path.exists(TEST_VECTOR_FILE):
    os.remove(TEST_VECTOR_FILE)


for dir_path in DIRS:
    label = os.path.basename(dir_path)
    files = sorted(os.listdir(dir_path))
    num_train = math.floor(RATIO * len(files))
    train_files, test_files = files[:num_train], files[num_train:]

    with open(TRAIN_VECTOR_FILE, 'a') as train_vector_file:
        for train_file in train_files:
            train_file_path = os.path.join(dir_path, train_file)
            train_vector_file.write(process_file(train_file_path, label))

    with open(TEST_VECTOR_FILE, 'a') as test_vector_file:
        for test_file in test_files:
            test_file_path = os.path.join(dir_path, test_file)
            test_vector_file.write(process_file(test_file_path, label))
