from feal import *
import sys

hex2bits = {'0' : (0,0,0,0),
            '1' : (0,0,0,1),
            '2' : (0,0,1,0),
            '3' : (0,0,1,1),
            '4' : (0,1,0,0),
            '5' : (0,1,0,1),
            '6' : (0,1,1,0),
            '7' : (0,1,1,1),
            '8' : (1,0,0,0),
            '9' : (1,0,0,1),
            'A' : (1,0,1,0),
            'B' : (1,0,1,1),
            'C' : (1,1,0,0),
            'D' : (1,1,0,1),
            'E' : (1,1,1,0),
            'F' : (1,1,1,1)}
bits2hex = {v : k for k,v in hex2bits.items()}

def hex_block_to_bits(hex_block):
  hex_block = hex_block.replace(" ", "").upper()
  bits = []
  for h in hex_block:
    bits += hex2bits[h]
  return bits

def bits_to_hex_block(bits):
  assert(len(bits) % 4 == 0)
  h = ""
  for i in range(len(bits) // 4):
    h += bits2hex[tuple(bits[i*4 : i*4 + 4])]
  return h

def dot(bits, variables):
  assert(len(bits) == len(variables))
  n = len(bits)
  lits = []
  for i in range(n):
    b = bits[i]
    v = variables[i]
    if b == 0:
      lits.append(-v)
    else:
      lits.append(v)
  return lits

def extract_bits(assignment, variables):
  bits = []
  for v in variables:
    if assignment[v] > 0:
      bits.append(1)
    else:
      bits.append(0)
  return bits

def parse_test_vecs(fname):
  num_tests = 0
  tests = []
  test_key = None
  with open(fname, 'r') as fin:
    for line in fin:
      if len(line) >= 3 and line[:3] == "KEY":
        num_tests += 1
        if test_key != None:
          tests.append([test_key, test_vecs])
        line = line.split()
        assert(line[0] == "KEY")
        test_key = line[2]
        test_vecs = []
      elif len(line) >= 2 and line[:2] == "PT":
        line = [x.split(':') for x in line[:-1].split(',')]
        pt_line = [x.replace(" ", "") for x in line[0]]
        ct_line = [x.replace(" ", "") for x in line[1]]
        assert(pt_line[0] == "PT")
        assert(ct_line[0] == "CT")
        test_vecs.append((pt_line[1], ct_line[1]))
  tests.append([test_key, test_vecs])
  assert(len(tests) == num_tests)
  return tests

def main(verbose):
  tests = parse_test_vecs("feal.tv")
  N = 32
  feal = FEAL_NX(N)
  nfv, res = feal.setup()
  s = Solver()
  s.add_clauses(res.cnf)

  print("Number of keys tested in test vectors (tv) file:", len(tests))
  for test_key, test_vecs in tests:
    print("Testing with key {0}".format(test_key))
    init_keys = hex_block_to_bits(test_key)
    for pt, ct in test_vecs:
      if verbose:
        print("Key {0}, PT {1} -> CT {2}".format(test_key, pt, ct), end="")
      plaintext = hex_block_to_bits(pt)
      ass = dot(init_keys, res.in_vars[:128]) + dot(plaintext, res.in_vars[128:])
      sat, soln = s.solve(ass)
      ciphertext = extract_bits(soln, res.out_vars)
      if verbose:
        print(" = {0} -> ".format(bits_to_hex_block(ciphertext)), end="")
      assert(bits_to_hex_block(ciphertext) == ct)
      if verbose:
        print("OK")
  print("All OK")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python3 test_feal.py <verbose>")
    print("verbose = 1 : Print every single test vector")
    print("verbose = 0 : Shh...")
    exit()

  verbose = int(sys.argv[1]) == 1
  main(verbose)  

