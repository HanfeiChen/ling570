#!/bin/sh

INPUT_FILE=examples/ex

mkdir -p q3
mkdir -p q4

for fsa_file in q2/fsa*; do
  fsa=$(basename "$fsa_file")
  echo $fsa
  ./fsa_acceptor.sh q2/"$fsa" $INPUT_FILE > q3/ex."$fsa"
  ./fsa_acceptor2.sh q2/"$fsa" $INPUT_FILE > q4/ex."$fsa"
done
