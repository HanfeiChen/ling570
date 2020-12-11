#!/usr/bin/python3

import sys
import subprocess

CARMEL = 'carmel'
FSA_FILE = sys.argv[1]
INPUT_FILE = sys.argv[2]

with open(INPUT_FILE, 'r') as f:
  for line in f:
    p = subprocess.Popen([CARMEL, '-k', '1', '-sli', FSA_FILE],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.stdin.write(line.encode())
    p.stdin.flush()
    stdout_output = p.stdout.read().decode()
    stderr_output = p.stderr.read().decode()
    exit_code = p.wait()

    result = "no" if "No derivations found" in stderr_output else "yes"

    stripped_line = line.strip('\r\n')
    print('{}\t=>\t{}'.format(stripped_line, result))
