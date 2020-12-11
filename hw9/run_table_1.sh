#!/bin/bash

for zz in NaiveBayes MaxEnt DecisionTree Winnow BalancedWinnow; do
  vectors2classify --training-file $exDir/train.vectors --testing-file $exDir/test.vectors --trainer $zz > $zz.stdout 2>$zz.stderr
done
