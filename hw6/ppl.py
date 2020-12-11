#!/usr/bin/python3

from collections import defaultdict
import math
import sys

LM_FILE = sys.argv[1]
L1, L2, L3 = (float(l) for l in sys.argv[2:5])
TEST_DATA = sys.argv[5]
OUTPUT_FILE = sys.argv[6]

BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'

sum = 0
word_num = 0
oov_num = 0
sent_num = 0

P1, P2, P3 = [defaultdict(lambda: (0, 0.0, float('-inf')))] * 3

with open(LM_FILE, 'r') as f:
    current_section = 0
    for line in f:
        if len(line.strip()) > 0:
            if line.startswith('\\'):
                if line.startswith('\\1-grams:'):
                    current_section = 1
                elif line.startswith('\\2-grams:'):
                    current_section = 2
                elif line.startswith('\\3-grams:'):
                    current_section = 3
                elif line.startswith('\\end'):
                    current_section = 0
                continue

            if current_section == 1:
                cnt, prob, lgprob, w = line.strip().split()
                P1[w] = (int(cnt), float(prob), float(lgprob))
            elif current_section == 2:
                cnt, prob, lgprob, w1, w2 = line.strip().split()
                P1[(w1, w2)] = (int(cnt), float(prob), float(lgprob))
            elif current_section == 3:
                cnt, prob, lgprob, w1, w2, w3 = line.strip().split()
                P1[(w1, w2, w3)] = (int(cnt), float(prob), float(lgprob))

with open(OUTPUT_FILE, 'w') as out_file:
    with open(TEST_DATA, 'r') as test_file:
        for line in test_file:
            if len(line.strip()) > 0:
                sent_num += 1
                sent = line.strip().split()
                word_num += len(sent)
                sent = [BOS_TOKEN] + sent + [EOS_TOKEN]
                out_file.write('Sent #{}: {}\n'.format(sent_num, ' '.join(sent)))
                sent_sum = 0
                sent_oov_num = 0
                for i in range(1, len(sent)):
                    if i == 1:
                        if sent[i] in P1:
                            p2 = P2[(sent[i-1], sent[i])][1]
                            p1 = P1[sent[i]][1]
                            notes = ' (unseen ngrams)' if p2 == 0.0 else ''
                            p = L2 * p2 + L1 * p1
                            lgprob = math.log10(p)
                            sent_sum += lgprob
                            out_file.write('{}: lg P({} | {}) = {}{}\n'.format(i, sent[i], sent[i-1], lgprob, notes))
                        else:
                            sent_oov_num += 1
                            out_file.write('{}: lg P({} | {}) = {}{}\n'.format(i, sent[i], sent[i-1], '-inf', ' (unknown word)'))
                    else:
                        if sent[i] in P1:
                            p3 = P3[(sent[i-2], sent[i-1], sent[i])][1]
                            p2 = P2[(sent[i-1], sent[i])][1]
                            p1 = P1[sent[i]][1]
                            notes = ' (unseen ngrams)' if p2 == 0.0 or p3 == 0.0 else ''
                            p = L3 * p3 + L2 * p2 + L1 * p1
                            lgprob = math.log10(p)
                            sent_sum += lgprob
                            out_file.write('{}: lg P({} | {} {}) = {}{}\n'.format(i, sent[i], sent[i-2], sent[i-1], lgprob, notes))
                        else:
                            out_file.write('{}: lg P({} | {} {}) = {}{}\n'.format(i, sent[i], sent[i-2], sent[i-1], '-inf', ' (unknown word)'))
                            sent_oov_num += 1
                sent_cnt = len(sent) - 1 - sent_oov_num
                out_file.write('1 sentence, {} words, {} OOVs\n'.format(len(sent) - 2, sent_oov_num))
                out_file.write('lgprob={:.10f}, ppl={:.10f}\n'.format(sent_sum, 10 ** (-sent_sum / sent_cnt)))
                sum += sent_sum
                oov_num += sent_oov_num
                out_file.write('\n\n\n')
        out_file.write('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')

        cnt = word_num + sent_num - oov_num
        total = sum/cnt
        ppl = 10 ** (-total)
        out_file.write('sent_num={} word_num={} oov_num={}\n'.format(sent_num, word_num, oov_num))
        out_file.write('lgprob={:.10f} ave_lgprob={:.10f} ppl={:.10f}\n'.format(sum, total, ppl))
