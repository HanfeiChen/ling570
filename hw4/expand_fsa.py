#!/usr/bin/python3

import sys
from collections import defaultdict
from typing import Dict


LEXICON_FILE = sys.argv[1]
MORPH_RULES_FILE = sys.argv[2]
OUTPUT_FSA_FILE = sys.argv[3]


def quote(symbol):
  return "\"{}\"".format(symbol)


class StateNameGenerator:
  def __init__(self, prefix='S', used_names=[]):
    self.used = set(used_names)
    self.prefix = prefix
    self.next_index = 1

  def generateName(self):
    while '{}{}'.format(self.prefix, self.next_index) in self.used:
      self.next_index += 1
    new_state = '{}{}'.format(self.prefix, self.next_index)
    self.used.add(new_state)
    return new_state


def parse_lexicon_file(filename: str) -> Dict[str, str]:
  lexicon = defaultdict(list)
  with open(filename, 'r') as f:
    for line in f:
      if len(line.strip()) > 0:
        line = line.strip()
        word, class_label = line.split()
        lexicon[class_label].append(word)
  return lexicon


class FSA:
  EPSILON = '*e*'

  def __init__(self, fsa_file: str = None) -> None:
    self.transitions = defaultdict(set)
    if fsa_file is not None:
      with open(fsa_file, 'r') as f:
        self.final = f.readline().strip()
        self.start = None
        for line in f:
          if len(line.strip()) > 0:
            src, rest = line.strip().lstrip('(').rstrip(')').split('(')
            src = src.strip()
            if self.start is None:
              self.start = src
            dst, tr = rest.split()
            dst = dst.strip()
            tr = tr.strip()
            self.transitions[(src, tr)].add(dst)
    print(self.transitions)

  def expand(self, lexicon: Dict[str, str]) -> 'FSA':
    usedNames = set()
    for (src, class_label), dst in self.transitions.items():
      usedNames.add(src)
      usedNames |= dst
    nameGen = StateNameGenerator(used_names=usedNames)

    new_transitions = defaultdict(set)
    for (src, class_label), dsts in self.transitions.items():
      for dst in dsts:
        if class_label == self.EPSILON:
          new_transitions[(src, self.EPSILON)].add(dst)
        print("Expanding {}--{}-->{}".format(src, class_label, dst))
        for word in lexicon[class_label]:
          if len(word) == 1 or word == self.EPSILON:
            new_transitions[(src, word)].add(dst)
          else:
            lastState = src
            for idx, char in enumerate(word):
              if idx < len(word) - 1:
                newState = nameGen.generateName()
                new_transitions[(lastState, char)].add(newState)
                lastState = newState
              else:
                new_transitions[(lastState, char)].add(dst)

    new_fsa = FSA()
    new_fsa.start = self.start
    new_fsa.final = self.final
    new_fsa.transitions = new_transitions
    return new_fsa

  def write_to_file(self, filename: str) -> None:
    with open(filename, 'w') as f:
      f.write('{}\n'.format(self.final))
      # first write transition lines for the start state
      for (src, tr), dsts in self.transitions.items():
        if src == self.start:
          if tr != self.EPSILON:
            tr = quote(tr)
          for dst in dsts:
            f.write('({} ({} {}))\n'.format(src, dst, tr))
      for (src, tr), dsts in self.transitions.items():
        if src != self.start:
          if tr != self.EPSILON:
            tr = quote(tr)
          for dst in dsts:
            f.write('({} ({} {}))\n'.format(src, dst, tr))

lexicon = parse_lexicon_file(LEXICON_FILE)
morph_fsa = FSA(fsa_file=MORPH_RULES_FILE)
morph_fsa.expand(lexicon).write_to_file(OUTPUT_FSA_FILE)
