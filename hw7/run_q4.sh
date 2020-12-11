#!/bin/sh

cat examples/wsj_sec0.word_pos | ./create_2gram_hmm.sh q4/2g_hmm
cat examples/wsj_sec0.word_pos | ./create_3gram_hmm.sh q4/3g_hmm_0.1_0.1_0.8 0.1 0.1 0.8 examples/unk_prob_sec22
cat examples/wsj_sec0.word_pos | ./create_3gram_hmm.sh q4/3g_hmm_0.2_0.3_0.5 0.2 0.3 0.5 examples/unk_prob_sec22
./check_hmm.sh q4/2g_hmm > q4/2g_hmm.warning
./check_hmm.sh q4/3g_hmm_0.1_0.1_0.8 > q4/3g_hmm_0.1_0.1_0.8.warning
./check_hmm.sh q4/3g_hmm_0.2_0.3_0.5 > q4/3g_hmm_0.2_0.3_0.5.warning
