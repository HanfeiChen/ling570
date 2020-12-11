#!/usr/bin/python3

import sys
from collections import defaultdict

OUTPUT_HMM = sys.argv[1]

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

def parse_input():
    parsed_sentences = []
    for line in sys.stdin:
        if len(line.strip()) > 0:
            parsed_sentences.append([('<s>', 'BOS')] + parse_line(line) + [('</s>', 'EOS')])
    return parsed_sentences

def train_hmm(sentences):
    bigram_count = defaultdict(int)
    unigram_count = defaultdict(int)
    emission_count = defaultdict(int)
    state_set = set()
    sym_set = set()

    for s in sentences:
        for i in range(len(s)):
            state_set.add(s[i][1])
            sym_set.add(s[i][0])
            unigram_count[s[i][1]] += 1
            emission_count[(s[i][1], s[i][0])] += 1
            if i < len(s) - 1:
                bigram_count[(s[i][1], s[i+1][1])] += 1

    # print(unigram_count, bigram_count, emission_count)

    state_num = len(state_set)
    sym_num = len(sym_set)

    init_prob = {'BOS': 1.0}
    trans_prob = defaultdict(float)
    for bigram, count in bigram_count.items():
        prob = count / unigram_count[bigram[0]]
        trans_prob[bigram] = prob
    emiss_prob = defaultdict(float)
    for emission, count in emission_count.items():
        hidden, _ = emission
        prob = count / unigram_count[hidden]
        emiss_prob[emission] = prob

    hmm = state_num, sym_num, init_prob, trans_prob, emiss_prob
    # print(hmm)
    return hmm

def write_hmm(state_num, sym_num, init_prob, trans_prob, emiss_prob):
    with open(OUTPUT_HMM, 'w') as f:
        f.write('state_num={}\n'.format(state_num))
        f.write('sym_num={}\n'.format(sym_num))
        f.write('init_line_num={}\n'.format(len(init_prob)))
        f.write('trans_line_num={}\n'.format(len(trans_prob)))
        f.write('emiss_line_num={}\n'.format(len(emiss_prob)))
        f.write('\n')

        f.write('\\init\n')
        for state, prob in sorted(init_prob.items()):
            f.write('{} {:.10f}\n'.format(state, prob))
        f.write('\n')

        f.write('\\transition\n')
        for bigram, prob in sorted(trans_prob.items()):
            f.write('{} {} {:.10f}\n'.format(bigram[0], bigram[1], prob))
        f.write('\n')

        f.write('\\emission\n')
        for emission, prob in sorted(emiss_prob.items()):
            f.write('{} {} {:.10f}\n'.format(emission[0], emission[1], prob))
        f.write('\n')

write_hmm(*train_hmm(parse_input()))
