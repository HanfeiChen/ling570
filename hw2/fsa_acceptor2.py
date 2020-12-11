#!/usr/bin/python3

import sys
from collections import defaultdict, deque
from typing import Set, List, Tuple

FSA_FILE = sys.argv[1]
INPUT_FILE = sys.argv[2]

class FSA:
  EPSILON = '*e*'

  def __init__(self, fsa_file) -> None:
    self.transitions = defaultdict(set)
    with open(fsa_file, 'r') as f:
      self.final = f.readline().strip()
      self.start = None
      for line in f:
        src, rest = line.strip().lstrip('(').rstrip(')').split('(')
        src = src.strip()
        if self.start is None:
          self.start = src
        dst, rest = rest.split()
        tr = rest.strip("\"")
        self.transitions[(src, tr)].add(dst)

  def recognize(self, tape: List[str]) -> bool:
    agenda = deque([(self.start, 0)])
    currentState = agenda.popleft()
    while True:
      if self._isAcceptState(tape, currentState):
        return True
      newStates = self._generateNewStates(tape, currentState)
      for state in newStates:
        agenda.append(state)
      if len(agenda) == 0:
        return False
      currentState = agenda.popleft()

  def _generateNewStates(self,
                         tape: List[str],
                         currentState: Tuple[str, int]) -> Set[Tuple[str, int]]:
    node, index = currentState
    newStates = set()
    for nextNode in self.transitions[(node, FSA.EPSILON)]:
      newStates.add((nextNode, index))
    if index < len(tape):
      for nextNode in self.transitions[(node, tape[index])]:
        newStates.add((nextNode, index+1))
    return newStates

  def _isAcceptState(self, tape: List[str], searchState: Tuple[str, int]) -> bool:
    node, index = searchState
    return index == len(tape) and node == self.final

fsa = FSA(FSA_FILE)

with open(INPUT_FILE, 'r') as f:
  for line in f:
    s = [token.strip("\"") for token in line.strip().split()]
    if any(token == fsa.EPSILON for token in s):
      s = []
    result = 'yes' if fsa.recognize(s) else 'no'

    stripped_line = line.strip('\r\n')
    print('{}\t=>\t{}'.format(stripped_line, result))
