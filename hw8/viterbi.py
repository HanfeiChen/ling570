#!/usr/bin/env python3

import sys
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import dok_matrix
from tqdm import tqdm


INPUT_HMM, TEST_FILE, OUTPUT_FILE = sys.argv[1:4]

class Vocabulary:
    def __init__(self, tokens) -> None:
        self.id2tok = ['<unk>']
        self.tok2id = defaultdict(int)
        self.tok2id['<unk>'] = 0
        for token in set(tokens):
            if token not in self.tok2id:
                self.id2tok.append(token)
                self.tok2id[token] = len(self.id2tok) - 1

    def __len__(self):
        return len(self.id2tok)

    def convert_tokens_to_ids(self, tokens):
        return [self.tok2id[token] for token in tokens]

    def convert_ids_to_tokens(self, ids):
        return [self.id2tok[id_] for id_ in ids]


def lg(val):
    if val == 0.:
        return float('-inf')
    return math.log10(val)


class HMM:
    def __init__(self, states, symbols, init_prob, trans_prob, emiss_prob):
        self.states = states
        self.symbols = symbols
        self.init_prob = init_prob
        self.trans_prob = trans_prob
        self.emiss_prob = emiss_prob


def load_hmm():
    state_set = set()
    symbol_set = set()
    init_prob = defaultdict(float)
    trans_prob = defaultdict(lambda: defaultdict(float))
    emiss_prob = defaultdict(lambda: defaultdict(float))

    section = 'header'
    with open(INPUT_HMM, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                line = line.strip()
                if line.startswith('\\'):
                    section = line[1:]
                    continue

                if section == 'init':
                    state, prob = line.split()
                    if not 0. <= float(prob) <= 1.:
                        print("warning: the prob is not in [0,1] range: " + line, file=sys.stderr)
                        continue
                    init_prob[state] = float(prob)
                elif section == 'transition':
                    from_state, to_state, prob = line.split()[:3]
                    if not 0. <= float(prob) <= 1.:
                        print("warning: the prob is not in [0,1] range: " + line, file=sys.stderr)
                        continue
                    trans_prob[from_state][to_state] = float(prob)
                    state_set.add(from_state)
                    state_set.add(to_state)
                elif section == 'emission':
                    state, symbol, prob = line.split()[:3]
                    if not 0. <= float(prob) <= 1.:
                        print("warning: the prob is not in [0,1] range: " + line, file=sys.stderr)
                        continue
                    emiss_prob[state][symbol] = float(prob)
                    state_set.add(state)
                    symbol_set.add(symbol)

    states = Vocabulary(state_set)
    symbols = Vocabulary(symbol_set)
    num_states = len(states)
    num_symbols = len(symbols)
    init_prob_arr = [0. for _ in range(num_states)]
    trans_prob_arr = dok_matrix((num_states, num_states))
    emiss_prob_arr = dok_matrix((num_states, num_symbols))
    for state, prob in init_prob.items():
        init_prob_arr[states.tok2id[state]] = prob
    for from_state, nested in trans_prob.items():
        for to_state, prob in nested.items():
            trans_prob_arr[states.tok2id[from_state], states.tok2id[to_state]] = prob
    for state, nested in emiss_prob.items():
        for symbol, prob in nested.items():
            emiss_prob_arr[states.tok2id[state], symbols.tok2id[symbol]] = prob

    print("Loaded HMM with {} states, {} symbols".format(len(state_set), len(symbol_set)))
    return HMM(states, symbols, init_prob_arr, trans_prob_arr, emiss_prob_arr)


def viterbi(hmm, observation_seq):
    o = hmm.symbols.convert_tokens_to_ids(observation_seq)
    seq_len = len(observation_seq)
    num_states = len(hmm.states)
    delta = dok_matrix((seq_len + 1, num_states))
    bp = dok_matrix((seq_len + 1, num_states), dtype=np.int)
    # FORWARD
    # initialization
    prev_to_try = []
    for j in range(len(hmm.states)):
        delta[0, j] = lg(hmm.init_prob[j])
        bp[0, j] = -1
        if delta[0, j] != float('-inf'):
            prev_to_try.append(j)
    # recursion: 2...n+1
    for t in range(seq_len):
        prev_to_try_next = []
        for j in range(num_states):
            k = o[t]
            maxVal = float('-inf')
            argMax = -1
            for i in prev_to_try:
                if (i, j) in hmm.trans_prob and (j, k) in hmm.emiss_prob:
                    val = delta[t, i] + lg(hmm.trans_prob[i, j]) + lg(hmm.emiss_prob[j, k])
                    if val > maxVal:
                        maxVal = val
                        argMax = i
            delta[t+1, j] = maxVal
            bp[t+1, j] = argMax
            if delta[t+1, j] != float('-inf'):
                prev_to_try_next.append(j)
        prev_to_try = prev_to_try_next
    # termination
    lgprob = float('-inf')
    qn = -1
    for i in range(num_states):
        if delta[seq_len, i] > lgprob:
            lgprob = delta[seq_len, i]
            qn = i

    # BACKWARD
    best_state_sequence = [-1 for _ in range(seq_len + 1)]
    best_state_sequence[seq_len] = qn

    for t in reversed(range(0, seq_len)):
        best_state_sequence[t] = bp[t+1, best_state_sequence[t+1]]

    best_state_sequence = hmm.states.convert_ids_to_tokens(best_state_sequence)

    return lgprob, best_state_sequence


hmm = load_hmm()

with open(TEST_FILE, 'r') as in_file, open(OUTPUT_FILE, 'w') as out_file:
    for line in tqdm(in_file.readlines()):
        if len(line.strip()) > 0:
            # print("Processing", line)
            line = line.strip()
            observations = line.split()
            # print(observations)
            lgprob, states = viterbi(hmm, observations)
            out_file.write("{} => {} {}\n".format(line, ' '.join(states), lgprob))
            # (line, '=>', ' '.join(states), lgprob)
