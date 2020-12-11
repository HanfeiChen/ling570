#!/usr/bin/python3

import sys
import subprocess

CARMEL = 'carmel'
FSA_FILE = sys.argv[1]
INPUT_FILE = sys.argv[2]

with open(INPUT_FILE, 'r') as f:
  for line in f:
    p = subprocess.Popen([CARMEL, '-O', '-k', '1', '-sli', FSA_FILE],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.stdin.write(line.encode())
    p.stdin.flush()
    stdout_output = p.stdout.read().decode()
    exit_code = p.wait()

    input_str = line.strip('\r\n')
    stripped_output = stdout_output.strip().split()
    output_symbols, output_prob = stripped_output[:-1], stripped_output[-1]
    if float(output_prob) == 0:
      output_str = '*none*'
    else:
      output_symbols = [symbol for symbol in output_symbols if symbol != '*e*']
      if len(output_symbols) == 0:
        output_symbols = ['*e*']
      output_str = ' '.join(output_symbols)
    print('{} => {} {}'.format(input_str, output_str, output_prob))
