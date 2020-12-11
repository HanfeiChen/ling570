#!/usr/bin/python3

from collections import defaultdict
import sys

INPUT_HMM = sys.argv[1]


def check_header():
    section = 'header'
    actual = defaultdict(int)
    state_set = set()
    sym_set = set()
    with open(INPUT_HMM, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                line = line.strip()
                if line.startswith('\\'):
                    section = line[1:]
                    continue

                if section == 'init':
                    actual['init_line_num'] += 1
                elif section == 'transition':
                    actual['trans_line_num'] += 1
                    from_state, to_state, _ = line.split()
                    state_set.add(from_state)
                    state_set.add(to_state)
                elif section == 'emission':
                    actual['emiss_line_num'] += 1
                    state, sym, _ = line.split()
                    state_set.add(state)
                    sym_set.add(sym)

    actual['state_num'] = len(state_set)
    actual['sym_num'] = len(sym_set)

    section = 'header'
    with open(INPUT_HMM, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                line = line.strip()
                if line.startswith('\\'):
                    section = line[1:]
                    continue
                if section == 'header':
                    key, claimed = line.split('=')
                    claimed = int(claimed)
                    if actual[key] != claimed:
                        print('warning: different numbers of {}: '
                              'claimed={}, real={}'.format(key, claimed, actual[key]))
                    else:
                        print(line)


def load_hmm():
    section = 'header'
    init_prob = defaultdict(float)
    trans_prob = defaultdict(lambda: defaultdict(float))
    emiss_prob = defaultdict(lambda: defaultdict(float))
    with open(INPUT_HMM, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                line = line.strip()
                if line.startswith('\\'):
                    section = line[1:]
                    continue

                if section == 'init':
                    state, prob = line.split()
                    init_prob[state] = float(prob)
                elif section == 'transition':
                    from_state, to_state, prob = line.split()
                    trans_prob[from_state][to_state] = float(prob)
                elif section == 'emission':
                    state, symbol, prob = line.split()
                    emiss_prob[state][symbol] = float(prob)
    return (init_prob, trans_prob, emiss_prob)


def check_hmm_properties(init_prob, trans_prob, emiss_prob):
    EPSILON = 1e-6
    def _approx(a, b):
        return -EPSILON < a - b < EPSILON

    init_prob_sum = sum(init_prob.values())
    if not _approx(init_prob_sum, 1.):
        print('warning: the init_prob_sum is {:.10f}'.format(init_prob_sum))

    for from_state in trans_prob:
        trans_prob_sum = sum(trans_prob[from_state].values())
        if not _approx(trans_prob_sum, 1.):
            print('warning: the trans_prob_sum '
                  'for state {} is {:.10f}'.format(from_state, trans_prob_sum))

    for state in trans_prob:
        emiss_prob_sum = sum(emiss_prob[state].values())
        if not _approx(emiss_prob_sum, 1.):
            print('warning: the emiss_prob_sum '
                  'for state {} is {:.10f}'.format(state, emiss_prob_sum))


check_header()
hmm = load_hmm()
check_hmm_properties(*hmm)
