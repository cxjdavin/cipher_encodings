from cnf_base import *
import random
import sys

#
# Helper functions (Quite self-explanatory)
#
def largest_seen(cnf):
  largest = 0
  for clause in cnf:
    for x in clause:
      largest = max(largest, abs(x))
  return largest

def bit_array_to_num(arr):
  num = 0
  for i in range(len(arr)):
    num = 2*num + arr[i]
  return num

def num_to_bit_array(bits, num):
  arr = []
  bin_str = bin(num)[2:]
  for b in bin_str:
    arr.append(int(b))
  assert(len(arr) <= bits)
  while len(arr) != bits:
    arr = [0] + arr
  return arr

def dot_product(bin_arr, indices):
  assert(len(bin_arr) == len(indices))
  res = []
  for i in range(len(bin_arr)):
    if bin_arr[i] == 0:
      res.append(-indices[i])
    else:
      res.append(indices[i])
  return res

def extract_bits(soln, indices):
  bits = dict()
  for idx in indices:
    bits[idx] = 1 if soln[idx] > 0 else 0
  return bits

'''
Simulate all instantiations of in_vec and verify against condition
'''
def run_solver(cnf, in_vec, out_vec, condition, args = None):
  s = Solver()
  s.add_clauses(cnf)
  n = len(in_vec)
  for i in range(pow(2, n)):
    arr = num_to_bit_array(n, i)
    ass = dot_product(arr, in_vec)
    sat, soln = s.solve(ass)
    bits = extract_bits(soln, in_vec + out_vec)
    assert(condition(bits, in_vec, out_vec, args))

#
# Tests
#
# For variable length functions, length 5-8 randomly chosen
# Choosing length > 8 will slow down testing as we try 2^(length) possible inputs
#
def test_bit_eq(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    x = bits[in_vec[0]]
    y = bits[out_vec[0]]
    return (x == y)

  print("Testing bit_eq... ", end="")
  for i in range(num_tests):
    x = random.randint(1, 100)
    next_free_var = x + random.randint(1, 200)
    nfv, res = bit_eq(next_free_var, x)
    y = res.out_vars[0]
    assert(y == next_free_var)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x], [y], condition)
  print("OK")

def test_bit_xor(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    x = bits[in_vec[0]]
    y = bits[in_vec[1]]
    z = bits[out_vec[0]]
    return ((x ^ y) == z)
    
  print("Testing bit_xor... ", end="")
  for i in range(num_tests):
    xy = random.sample(range(1,100), 2)
    x = xy[0]
    y = xy[1]
    next_free_var = max(x,y) + random.randint(1, 200)
    nfv, res = bit_xor(next_free_var, x, y)
    z = res.out_vars[0]
    assert(z == next_free_var)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x,y], [z], condition)
  print("OK")

def test_bit_and(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    x = bits[in_vec[0]]
    y = bits[in_vec[1]]
    z = bits[out_vec[0]]
    return ((x & y) == z)
    
  print("Testing bit_and... ", end="")
  for i in range(num_tests):
    xy = random.sample(range(1,100), 2)
    x = xy[0]
    y = xy[1]
    next_free_var = max(x,y) + random.randint(1, 200)
    nfv, res = bit_and(next_free_var, x, y)
    z = res.out_vars[0]
    assert(z == next_free_var)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x,y], [z], condition)
  print("OK")

def test_bit_or(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    x = bits[in_vec[0]]
    y = bits[in_vec[1]]
    z = bits[out_vec[0]]
    return ((x | y) == z)
    
  print("Testing bit_or... ", end="")
  for i in range(num_tests):
    xy = random.sample(range(1,100), 2)
    x = xy[0]
    y = xy[1]
    next_free_var = max(x,y) + random.randint(1, 200)
    nfv, res = bit_or(next_free_var, x, y)
    z = res.out_vars[0]
    assert(z == next_free_var)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x,y], [z], condition)
  print("OK")

def test_word_xor(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    assert(len(in_vec) % 2 == 0)
    n = len(in_vec) // 2
    x = in_vec[:n]
    y = in_vec[n:]
    z = out_vec
    condition_ok = None
    for i in range(n):
      xi = bits[x[i]]
      yi = bits[y[i]]
      zi = bits[z[i]]
      condition_ok = ((xi ^ yi) == zi)
    return condition_ok

  print("Testing word_xor... ", end="")
  for i in range(num_tests):
    num_bits = random.randint(5, 8)
    xy = random.sample(range(1, pow(2,num_bits)), 2*num_bits)
    x = xy[:num_bits]
    y = xy[num_bits:]
    next_free_var = max(xy) + random.randint(1, 200)
    nfv, res = word_xor(next_free_var, x, y)
    z = res.out_vars
    assert(len(z) == num_bits)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, x+y, z, condition)
  print("OK")

def test_rotate_left_by_k(num_tests):
  def condition(bits, in_vec, out_vec, args):
    assert(len(in_vec) == len(out_vec))
    n = len(in_vec)
    k = args[0]
    condition_ok = None
    for i in range(n):
      xi = bits[in_vec[(i+k) % n]]
      yi = bits[out_vec[i]]
      condition_ok = (xi == yi)
    return condition_ok

  print("Testing rotate_left_by_k... ", end="")
  for i in range(num_tests):
    num_bits = random.randint(5, 8)
    k = random.randint(1, 10)
    x = random.sample(range(1, pow(2,num_bits)), num_bits)
    next_free_var = max(x) + random.randint(1, 200)
    nfv, res = rotate_left_by_k(next_free_var, num_bits, x, k)
    y = res.out_vars
    assert(len(y) == num_bits)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, x, y,condition, [k])
  print("OK")

def test_rotate_right_by_k(num_tests):
  def condition(bits, in_vec, out_vec, args):
    assert(len(in_vec) == len(out_vec))
    n = len(in_vec)
    k = args[0]
    condition_ok = None
    for i in range(n):
      xi = bits[in_vec[(i-k) % n]]
      yi = bits[out_vec[i]]
      condition_ok = (xi == yi)
    return condition_ok

  print("Testing rotate_right_by_k... ", end="")
  for i in range(num_tests):
    num_bits = random.randint(5, 8)
    k = random.randint(1, 10)
    x = random.sample(range(1, pow(2,num_bits)), num_bits)
    next_free_var = max(x) + random.randint(1, 200)
    nfv, res = rotate_right_by_k(next_free_var, num_bits, x, k)
    y = res.out_vars
    assert(len(y) == num_bits)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, x, y,condition, [k])
  print("OK")

def test_half_adder(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    x = bits[in_vec[0]]
    y = bits[in_vec[1]]
    c = bits[out_vec[0]]
    s = bits[out_vec[1]]
    return ((x ^ y) == s) and ((x & y) == c)
    
  print("Testing half_adder... ", end="")
  for i in range(num_tests):
    xy = random.sample(range(1,100), 2)
    x = xy[0]
    y = xy[1]
    next_free_var = max(x,y) + random.randint(1, 200)
    nfv, res = half_adder(next_free_var, x, y)
    z = res.out_vars
    assert(len(z) == 2)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x,y], z, condition)
  print("OK")

def test_full_adder(num_tests):
  def condition(bits, in_vec, out_vec, args):
    x = bits[in_vec[0]]
    y = bits[in_vec[1]]
    cin = bits[in_vec[2]]
    ignore_cout = args[0]
    if ignore_cout:
      s = bits[out_vec[0]]
      return ((x ^ y ^ cin) == s)
    else:
      c = bits[out_vec[0]]
      s = bits[out_vec[1]]
      return ((x ^ y ^ cin) == s) and (((x & y) | (cin & (x ^ y))) == c)

  print("Testing full_adder... ", end="")
  for i in range(num_tests):
    xyc = random.sample(range(1,100), 3)
    x = xyc[0]
    y = xyc[1]
    c_in = xyc[2]
    next_free_var = max(xyc) + random.randint(1, 200)

    # Test ignoring cout
    nfv, res = full_adder(next_free_var, x, y, c_in, ignore_cout = True)
    z = res.out_vars
    assert(len(z) == 1)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x,y,c_in], z, condition, [True])

    # Test considering cout
    nfv, res = full_adder(next_free_var, x, y, c_in, ignore_cout = False)
    z = res.out_vars
    assert(len(z) == 2)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, [x,y,c_in], z, condition, [False])
  print("OK")

def test_modular_addition(num_tests):
  def condition(bits, in_vec, out_vec, args = None):
    assert(len(in_vec) % 2 == 0)
    n = len(in_vec) // 2
    x = bit_array_to_num([bits[x] for x in in_vec[:n]])
    y = bit_array_to_num([bits[y] for y in in_vec[n:]])
    z = bit_array_to_num([bits[z] for z in out_vec])
    return (((x + y) % pow(2,n)) == z)

  print("Testing modular_addition... ", end="")
  for i in range(num_tests):
    num_bits = random.randint(5, 8)
    xy = random.sample(range(1, pow(2,num_bits)), 2*num_bits)
    x = xy[:num_bits]
    y = xy[num_bits:]
    next_free_var = max(xy) + random.randint(1, 200)
    nfv, res = modular_addition(next_free_var, num_bits, x, y)
    z = res.out_vars
    assert(len(z) == num_bits)
    assert(nfv == largest_seen(res.cnf) + 1)
    run_solver(res.cnf, x+y, z, condition)
  print("OK")

def test_create_constant_vec(num_tests):
  print("Testing create_constant_vec... ", end="")
  for i in range(num_tests):
    num_bits = random.randint(5, 8)
    next_free_var = random.randint(1, 200)
    for num in range(pow(2, num_bits)):
      vec = num_to_bit_array(num_bits, num)
      nfv, res = create_constant_vec(next_free_var, vec)
      z = res.out_vars
      assert(len(z) == num_bits)
      assert(nfv == largest_seen(res.cnf) + 1)
      s = Solver()
      s.add_clauses(res.cnf)
      sat, soln = s.solve()
      bits = extract_bits(soln, z)
      assert(bit_array_to_num([bits[v] for v in z]) == num)
  print("OK")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python3 test_cnf_base.py <num_tests>")
    exit()
  num_tests = int(sys.argv[1])

  test_bit_eq(num_tests)
  test_bit_xor(num_tests)
  test_bit_and(num_tests)
  test_bit_or(num_tests)
  test_word_xor(num_tests)
  test_rotate_left_by_k(num_tests)
  test_rotate_right_by_k(num_tests)
  test_half_adder(num_tests)
  test_full_adder(num_tests)
  test_modular_addition(num_tests)
  test_create_constant_vec(num_tests)

