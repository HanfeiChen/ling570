#!/usr/bin/python3

import sys
import subprocess

CARMEL = 'carmel'
FST_FILE = sys.argv[1]
WORD_LIST = sys.argv[2]
OUTPUT_FILE = sys.argv[3]


output_lines = []

with open(WORD_LIST, 'r') as f:
  for line in f:
    p = subprocess.Popen([CARMEL, '-O', '-k', '1', '-sli', FST_FILE],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    word = line.strip()
    input_chars = [char for char in word]
    if len(word) == 0:
      input_line = '*e*'
    else:
      input_line = ' '.join(['\"{}\"'.format(c) for c in word])
    input_line = input_line + '\n'
    p.stdin.write(input_line.encode())
    p.stdin.flush()
    stdout_output = p.stdout.read().decode()
    exit_code = p.wait()

    input_str = line.strip('\r\n')
    stripped_output = stdout_output.strip().split()
    output_symbols, output_prob = stripped_output[:-1], stripped_output[-1]
    if float(output_prob) == 0:
      output_str = '*NONE*'
    else:
      output_pairs = []
      word_acc = ""
      for char, class_label in zip(input_chars, output_symbols):
        word_acc += char
        if class_label != '*e*':
          output_pairs.append('{}/{}'.format(word_acc, class_label))
          word_acc = ""
      output_str = ' '.join(output_pairs)
    output_lines.append('{} => {}\n'.format(input_str, output_str))

with open(OUTPUT_FILE, 'w') as f:
  for line in output_lines:
    f.write(line)
