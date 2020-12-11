#!/usr/bin/python3

import math
import sys
from collections import Counter


NGRAM_COUNT_FILE = sys.argv[1]
LM_FILE = sys.argv[2]

BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'

unigrams = Counter()
bigrams = Counter()
trigrams = Counter()


with open(NGRAM_COUNT_FILE, 'r') as f:
    for line in f:
        if len(line.strip()) > 0:
            parts = line.strip().split()
            count, ngram = parts[0], parts[1:]
            count = int(count)
            ngram = tuple(ngram)
            if len(ngram) == 1:
                unigrams[ngram[0]] = count
            elif len(ngram) == 2:
                bigrams[ngram] = count
            elif len(ngram) == 3:
                trigrams[ngram] = count


with open(LM_FILE, 'w') as f:
    f.write('\\data\\\n')
    f.write('ngram 1: type={} token={}\n'.format(len(unigrams), sum(unigrams.values())))
    f.write('ngram 2: type={} token={}\n'.format(len(bigrams), sum(bigrams.values())))
    f.write('ngram 3: type={} token={}\n'.format(len(trigrams), sum(trigrams.values())))
    f.write('\n')

    f.write('\\1-grams:\n')
    for unigram, count in unigrams.most_common():
        prob = count / sum(unigrams.values())
        log_prob = math.log10(prob)
        f.write('{} {:.10f} {:.10f} {}\n'.format(count, prob, log_prob, unigram))
    f.write('\n')

    f.write('\\2-grams:\n')
    for bigram, count in bigrams.most_common():
        prob = count / unigrams[bigram[0]]
        log_prob = math.log10(prob)
        f.write('{} {:.10f} {:.10f} {}\n'.format(count, prob, log_prob, ' '.join(bigram)))
    f.write('\n')

    f.write('\\3-grams:\n')
    for trigram, count in trigrams.most_common():
        prob = count / bigrams[tuple(trigram[:2])]
        log_prob = math.log10(prob)
        f.write('{} {:.10f} {:.10f} {}\n'.format(count, prob, log_prob, ' '.join(trigram)))
    f.write('\n')

    f.write('\\end\\\n')
