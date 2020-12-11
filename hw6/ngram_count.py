#!/usr/bin/python3

import sys
from collections import Counter

TRAINING_DATA = sys.argv[1]
NGRAM_COUNT_FILE = sys.argv[2]

BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'

unigrams = Counter()
bigrams = Counter()
trigrams = Counter()

with open(TRAINING_DATA, 'r') as f:
    for line in f:
        if len(line.strip()) > 0:
            tokens = line.strip().split()
            tokens = [BOS_TOKEN] + tokens + [EOS_TOKEN]
            for i in range(len(tokens)):
                unigrams[tokens[i]] += 1
                if i < len(tokens) - 1:
                    bigrams[tuple(tokens[i:i+2])] += 1
                if i < len(tokens) - 2:
                    trigrams[tuple(tokens[i:i+3])] += 1

with open(NGRAM_COUNT_FILE, 'w') as f:
    for unigram, count in unigrams.most_common():
        f.write("{}\t{}\n".format(count, unigram))

    for bigram, count in bigrams.most_common():
        f.write("{}\t{}\n".format(count, ' '.join(bigram)))

    for trigram, count in trigrams.most_common():
        f.write("{}\t{}\n".format(count, ' '.join(trigram)))
