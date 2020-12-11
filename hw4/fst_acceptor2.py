#!/usr/bin/python3

import sys
from typing import List, Tuple

FST_FILE = sys.argv[1]
INPUT_FILE = sys.argv[2]

def quote(symbol):
  return "\"{}\"".format(symbol)

class FST:
  EPSILON = '*e*'

  def __init__(self, fst_file: str) -> None:
    self.transitions = dict()
    with open(fst_file, 'r') as f:
      self.final = f.readline().strip()
      self.start = None
      for line in f:
        if len(line.strip()):
          src, rest = line.strip().lstrip('(').rstrip(')').split('(')
          src = src.strip()
          if self.start is None:
            self.start = src
          rest = rest.split()
          if len(rest) == 3:
            dst, in_symbol, out_symbol = rest
            prob = 1.
          elif len(rest) == 4:
            dst, in_symbol, out_symbol, prob = rest
          else:
            raise UserWarning("unexpected format")
          in_symbol = in_symbol.strip("\"")
          out_symbol = out_symbol.strip("\"")
          prob = float(prob)
          self.transitions[(src, in_symbol)] = (dst, out_symbol, prob)

  def recognize(self, tape: List[str]) -> Tuple[List[str], float, bool]:
    index = 0
    currentState = self.start
    output_tape = []
    output_prob = 1.0
    while True:
      if index == len(tape):
        if currentState == self.final:
          return output_tape, output_prob, True
        else:
          return [], 0., False
      elif (currentState, tape[index]) not in self.transitions:
        return [], 0., False
      else:
        currentState, out_symbol, prob = self.transitions[(currentState, tape[index])]
        output_tape.append(out_symbol)
        output_prob *= prob
        index += 1

fst = FST(FST_FILE)

with open(INPUT_FILE, 'r') as f:
  for line in f:
    tape = [token.strip("\"") for token in line.strip().split()]
    if any(token == fst.EPSILON for token in tape):
      tape = []
    output_tape, prob, accept = fst.recognize(tape)

    input_str = line.strip()
    if accept:
      output_quoted = [quote(symbol) for symbol in output_tape if symbol != fst.EPSILON]
      if len(output_quoted) == 0:
        output_quoted = [fst.EPSILON]
      output_str = ' '.join(output_quoted)
    else:
      output_str = '*none*'
    print('{} => {} {}'.format(input_str, output_str, prob))
