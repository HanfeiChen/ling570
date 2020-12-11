#!/usr/bin/env python3

import os
import sys
from collections import Counter

TRAIN_FILE, TEST_FILE, RARE_THRES, FEAT_THRES, OUTPUT_DIR = sys.argv[1:6]
RARE_THRES, FEAT_THRES = float(RARE_THRES), float(FEAT_THRES)


def generate_prefixes(token, num=4):
    prefixes = []
    for i in range(1, num+1):
        prefixes.append(token[:i])
    return prefixes


def generate_suffixes(token, num=4):
    suffixes = []
    for i in range(1, num+1):
        suffixes.append(token[-i:])
    return suffixes


def contains_number(token):
    for c in token:
        if c.isdigit():
            return True
    return False


def contains_upper_case(token):
    for c in token:
        if c.isupper():
            return True
    return False


def contains_hyphen(token):
    for c in token:
        if c == '-':
            return True
    return False


def parse_line(line):
    output = []
    for pair in line.strip().split():
        components = pair.split('/')
        orig_len = len(components)
        for i in reversed(range(orig_len)):
            if components[i][-1] == '\\':
                components[i] = components[i][:-1] + '/' + components[i+1]
                components.pop(i+1)
        output.append(tuple(components))
    return output


def parse_file(file_path):
    parsed = []
    with open(file_path, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                parsed.append(parse_line(line))
    return parsed


def create_voc(train_data):
    token_counter = Counter()
    for line in train_data:
        tokens = [pair[0] for pair in line]
        token_counter.update(tokens)
    return token_counter


def write_sorted_features(feature_counter, output_file_name):
    with open(os.path.join(OUTPUT_DIR, output_file_name), 'w') as out_file:
        for feat, freq in feature_counter.most_common():
            print("{} {}".format(feat, freq), file=out_file)


def create_train_features(train_data, train_token_counter):
    total_features = Counter()
    feature_vectors = []
    for line_idx, line in enumerate(train_data):
        for token_idx, (token, tag) in enumerate(line):
            token_features = Counter()
            if train_token_counter[token] < RARE_THRES:
                # rare
                for prefix in generate_prefixes(token):
                    token_features['pref={}'.format(prefix)] += 1
                for suffix in generate_suffixes(token):
                    token_features['suf={}'.format(suffix)] += 1
                if contains_number(token):
                    token_features['containNum'] += 1
                if contains_hyphen(token):
                    token_features['containHyp'] += 1
                if contains_upper_case(token):
                    token_features['containUC'] += 1
            else:
                # not rare
                token_features['curW={}'.format(token)] += 1
            # for all tokens
            prev_word, prev_tag = line[token_idx-1] if token_idx > 0 else ('BOS', 'BOS')
            next_word, next_tag = line[token_idx+1] if token_idx < len(line) - 1 else ('EOS', 'EOS')
            token_features['prevW={}'.format(prev_word)] += 1
            token_features['prevT={}'.format(prev_tag)] += 1
            token_features['nextW={}'.format(next_word)] += 1
            if token_idx > 0:
                prev_2_word, prev_2_tag = line[token_idx-2] if token_idx > 1 else ('BOS', 'BOS')
                token_features['prevTwoTags={}+{}'.format(prev_2_tag, prev_tag)] += 1
                token_features['prev2W={}'.format(prev_2_word)] += 1
            if token_idx < len(line) - 1:
                next_2_word, next_2_tag = line[token_idx+2] if token_idx < len(line) - 2 else ('EOS', 'EOS')
                token_features['next2W={}'.format(next_2_word)] += 1

            feature_vectors.append((line_idx, token_idx, token, tag, token_features))

            total_features += token_features
    return total_features, feature_vectors


def filter_features(feature_counter):
    criteria = lambda item: item[0].startswith('curW=') or item[1] >= FEAT_THRES
    return Counter(dict(filter(criteria, feature_counter.items())))


def write_final_feature_vectors(feature_vectors, kept_features, out_file_name):
    with open(os.path.join(OUTPUT_DIR, out_file_name), 'w') as out_file:
        for line_idx, token_idx, token, tag, feature_vector in feature_vectors:
            out_line = '{}-{}-{} {}'.format(line_idx, token_idx, token, tag)
            for feat, freq in feature_vector.items():
                feat = feat.replace(',', 'comma')
                if feat in kept_features:
                    out_line += ' {} {}'.format(feat, freq)
            out_line = out_line.replace(',', 'comma')
            print(out_line, file=out_file)


os.makedirs(OUTPUT_DIR, exist_ok=True)

train_data = parse_file(TRAIN_FILE)
train_token_counter = create_voc(train_data)
write_sorted_features(train_token_counter, 'train_voc')
train_features, feature_vectors = create_train_features(train_data, train_token_counter)
write_sorted_features(train_features, 'init_feats')
kept_features = filter_features(train_features)
write_sorted_features(kept_features, 'kept_feats')
write_final_feature_vectors(feature_vectors, kept_features, 'final_train.vectors.txt')

test_data = parse_file(TEST_FILE)
test_token_counter = create_voc(test_data)
_, test_feature_vectors = create_train_features(test_data, test_token_counter)
write_final_feature_vectors(test_feature_vectors, kept_features, 'final_test.vectors.txt')
