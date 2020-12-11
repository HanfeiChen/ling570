#!/bin/sh

./maxent_tagger.py $@

mallet import-file --input $5/final_train.vectors.txt --output $5/final_train.vectors
mallet import-file --input $5/final_test.vectors.txt --use-pipe-from $5/final_train.vectors --output $5/final_test.vectors

vectors2classify --training-file $5/final_train.vectors \
                 --testing-file $5/final_test.vectors \
                 --trainer MaxEnt \
                 --output-classifier $5/me_model \
                 > $5/me_model.stdout 2> $5/me_model.stderr

mallet classify-file --input $5/final_test.vectors.txt --classifier $5/me_model --output $5/sys_out
