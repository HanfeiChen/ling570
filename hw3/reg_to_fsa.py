#!/usr/bin/python3

import sys

def quote(symbol):
  return "\"{}\"".format(symbol)

def build_fsa():
  transitions = []
  F0 = 'F0'
  for line in sys.stdin:
    if line:
      rule = line.split()
      if len(rule) == 3:
        # X => y Z
        X, y, Z = rule
        transitions.append((X, Z, y))
      elif len(rule) == 2:
        # X => y
        X, y = rule
        transitions.append((X, F0, y))
  print(F0)
  for src, dst, tr in transitions:
    src, dst = quote(src), quote(dst)
    if tr != '*e*':
      tr = quote(tr)
    print("({} ({} {})".format(src, dst, tr))

if __name__ == '__main__':
  build_fsa()
