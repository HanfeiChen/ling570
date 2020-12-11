#!/usr/bin/python3

import sys
from collections import defaultdict

OUTPUT_HMM = sys.argv[1]
L1 = float(sys.argv[2])
L2 = float(sys.argv[3])
L3 = float(sys.argv[4])
UNK_PROB_FILE = sys.argv[5]

def parse_line(line):
    output = []
    for pair in line.strip().split():
        components = pair.split('/')
        orig_len = len(components)
        for i in reversed(range(orig_len)):
            if components[i][-1] == '\\':
                components[i] = components[i][:-1] + '/' + components[i+1]
                components.pop(i+1)
        assert len(components) == 2
        output.append(tuple(components))
    return output

def parse_input():
    parsed_sentences = []
    for line in sys.stdin:
        if len(line.strip()) > 0:
            parsed_sentences.append([('<s>', 'BOS')] + parse_line(line) + [('</s>', 'EOS')])
    return parsed_sentences

def parse_unk_file(unk_file):
    unk_prob = defaultdict(float)
    with open(unk_file, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                state, prob = line.split()
                unk_prob[state] = float(prob)
    return unk_prob

def train_hmm(sentences):
    unigram_count = defaultdict(int)
    bigram_count = defaultdict(int)
    trigram_count = defaultdict(int)
    emission_count = defaultdict(int)
    sym_set = set()
    tag_set = set()
    state_set = set()

    for s in sentences:
        for i in range(len(s)):
            tag_set.add(s[i][1])
            sym_set.add(s[i][0])
            unigram_count[s[i][1]] += 1
            emission_count[(s[i][1], s[i][0])] += 1
            if i < len(s) - 1:
                bigram_count[(s[i][1], s[i+1][1])] += 1
            if i < len(s) - 2:
                trigram_count[(s[i][1], s[i+1][1], s[i+2][1])] += 1

    sym_set.add('<unk>')
    sym_num = len(sym_set)
    default_trans_prob = 1. / (len(tag_set) - 2 + 1)

    init_prob = {('BOS', 'BOS'): 1.0}
    trans_prob = defaultdict(float)
    # for trigram, count in trigram_count.items():
    #     p3 = count / bigram_count[(trigram[0], trigram[1])]
    #     p2 = bigram_count[(trigram[1], trigram[2])] / unigram_count[trigram[1]]
    #     p1 = unigram_count[trigram[2]] / len(unigram_count)
    #     prob = L3 * p3 + L2 * p2 + L1 * p1
    #     trans_prob[(trigram[0] + '_' + trigram[1], trigram[1] + '_' + trigram[2])] = prob
    for t1 in tag_set:
        for t2 in tag_set:
            for t3 in tag_set:
                si, sj = (t1, t2), (t2, t3)
                state_set.add(si)
                state_set.add(sj)
                # t2 == t2' => P(t3 | t1 t2)
                if (t1, t2) not in bigram_count or bigram_count[(t1, t2)] == 0:
                    p3 = 0. if t3 == 'BOS' else default_trans_prob
                else:
                    p3 = trigram_count[(t1, t2, t3)] / bigram_count[(t1, t2)]
                p2 = bigram_count[(t2, t3)] / unigram_count[t2]
                p1 = unigram_count[t3] / sum(unigram_count.values())
                prob = L3 * p3 + L2 * p2 + L1 * p1
                trans_prob[(si, sj)] = prob

    state_num = len(state_set)

    unk_prob = parse_unk_file(UNK_PROB_FILE)
    emiss_prob_by_tag = defaultdict(float)
    for tag, prob in unk_prob.items():
        emiss_prob_by_tag[(tag, '<unk>')] = prob
    emiss_prob = defaultdict(float)
    for emission, count in emission_count.items():
        hidden, _ = emission
        prob = count / unigram_count[hidden]
        emiss_prob_by_tag[emission] = prob * (1 - unk_prob[hidden])
    for state in state_set:
        t1, t2 = state
        for sym in sym_set:
            if (t2, sym) in emiss_prob_by_tag:
                emiss_prob[(state, sym)] = emiss_prob_by_tag[(t2, sym)]

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
            f.write('{} {:.10f}\n'.format('_'.join(state), prob))
        f.write('\n')

        f.write('\\transition\n')
        for bigram, prob in sorted(trans_prob.items()):
            f.write('{} {} {:.10f}\n'.format('_'.join(bigram[0]), '_'.join(bigram[1]), prob))
        f.write('\n')

        f.write('\\emission\n')
        for emission, prob in sorted(emiss_prob.items()):
            f.write('{} {} {:.10f}\n'.format('_'.join(emission[0]), emission[1], prob))
        # f.write('\n')

write_hmm(*train_hmm(parse_input()))
