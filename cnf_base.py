from util import *

'''
All functions return [next_free_var, in_vars, out_vars, cnf]
'''
class Result:
  def __init__(self, in_vars, out_vars, cnf):
    self.in_vars = in_vars
    self.out_vars = out_vars
    self.cnf = cnf

#
# BIT LEVEL
#
'''
x = y
'''
def bit_eq(next_free_var, x):
  y = next_free_var
  cnf = [[x, -y],
         [-x, y]]
  return y+1, Result([x], [y], cnf)

'''
c = a xor b
-a -b -c
-a  b c
 a -b c
 a  b -c
'''
def bit_xor(next_free_var, x, y):
  z = next_free_var
  cnf = [[-x, -y, -z],
         [-x,  y,  z],
         [ x, -y,  z],
         [ x,  y, -z]]
  return z+1, Result([x,y], [z], cnf)

'''
c = a and b
-a -b  c
-a  b -c
 a -b -c
 a  b -c
'''
def bit_and(next_free_var, x, y):
  z = next_free_var
  cnf = [[-x, -y,  z],
         [-x,  y, -z],
         [ x, -y, -z],
         [ x,  y, -z]]
  return z+1, Result([x,y], [z], cnf)

'''
c = a or b
-a -b  c
-a  b  c
 a -b  c
 a  b -c
'''
def bit_or(next_free_var, x, y):
  z = next_free_var
  cnf = [[-x, -y,  z],
         [-x,  y,  z],
         [ x, -y,  z],
         [ x,  y, -z]]
  return z+1, Result([x,y], [z], cnf)

#
# WORD LEVEL
#
'''
Given x and y, return (x xor y)
E.g. x = [v1, v2, v3] and y = [v4, v5, v6] gives z = [v7, v8, v9]
where v7 = v1 xor v4
      v8 = v2 xor v5
      v9 = v3 xor v6
'''
def word_xor(next_free_var, x, y):
  assert(len(x) == len(y))
  num_bits = len(x)
  out_vars = []
  cnf = []
  for i in range(num_bits):
    next_free_var, res = bit_xor(next_free_var, x[i], y[i])
    out_vars += res.out_vars
    cnf += res.cnf
  return next_free_var, Result(x + y, out_vars, cnf)

'''
Given bit vector x, create corresponding rotated vector y
E.g. x = [v1, v2, v3] and k = 1 gives y = [v4, v5, v6]
where v4 = v2
      v5 = v3
      v6 = v1
'''
def rotate_left_by_k(next_free_var, num_bits, x, k):
  assert(len(x) == num_bits)
  out_vars = []
  cnf = []
  for i in range(num_bits):
    next_free_var, res = bit_eq(next_free_var, x[(i+k) % num_bits])
    out_vars += res.out_vars
    cnf += res.cnf
  return next_free_var, Result(x, out_vars, cnf)

'''
Given bit vector x, create corresponding rotated vector y
E.g. x = [v1, v2, v3] and k = 1 gives y = [v4, v5, v6]
where v4 = v3
      v5 = v1
      v6 = v2
'''
def rotate_right_by_k(next_free_var, num_bits, x, k):
  assert(len(x) == num_bits)
  out_vars = []
  cnf = []
  for i in range(num_bits):
    next_free_var, res = bit_eq(next_free_var, x[(i-k) % num_bits])
    out_vars += res.out_vars
    cnf += res.cnf
  return next_free_var, Result(x, out_vars, cnf)
  
'''
Half adder
x + y = (carry c_out, sum s)

s = x xor y
c = x and y
'''
def half_adder(next_free_var, x, y):
  next_free_var, s_res = bit_xor(next_free_var, x, y)
  next_free_var, c_res = bit_and(next_free_var, x, y)
  return next_free_var, Result([x, y],
                               c_res.out_vars + s_res.out_vars,
                               c_res.cnf + s_res.cnf)

'''
Full adder
if ignore_cout: x + y + c_in = (sum s)
if not ignore_cout: x + y + c_in = (carry c_out, sum s)

s = x xor y xor c_in
c = (x and y) or (c_in and (x xor y))
'''
def full_adder(next_free_var, x, y, c_in, ignore_cout):
  next_free_var, x_xor_y_res = bit_xor(next_free_var, x, y)
  x_xor_y = x_xor_y_res.out_vars[0]
  next_free_var, s_res = bit_xor(next_free_var, x_xor_y, c_in)
  if ignore_cout:
    return next_free_var, Result([x, y, c_in],
                                 s_res.out_vars,
                                 x_xor_y_res.cnf + s_res.cnf)
  else:
    next_free_var, x_and_y_res = bit_and(next_free_var, x, y)
    x_and_y = x_and_y_res.out_vars[0]
    next_free_var, c_right_res = bit_and(next_free_var, c_in, x_xor_y)
    c_right = c_right_res.out_vars[0]
    next_free_var, c_res = bit_or(next_free_var, x_and_y, c_right)
    return next_free_var, Result([x, y, c_in],
                                 c_res.out_vars + s_res.out_vars,
                                 x_xor_y_res.cnf + x_and_y_res.cnf + c_right_res.cnf + c_res.cnf + s_res.cnf)

'''
Given x and y, return (x + y) ignoring the overflow bit
'''
def modular_addition(next_free_var, num_bits, x, y):
  assert(len(x) == num_bits)
  assert(len(y) == num_bits)
  c = None
  out_vars = []
  cnf = []
  for i in range(num_bits-1, 0, -1):
    a = x[i]
    b = y[i]
    if c == None:
      next_free_var, res = half_adder(next_free_var, a, b)
    else:
      next_free_var, res = full_adder(next_free_var, a, b, c, ignore_cout = False)
    c = res.out_vars[0]
    s = res.out_vars[1]
    out_vars.append(s)
    cnf += res.cnf
  next_free_var, res = full_adder(next_free_var, x[0], y[0], c, ignore_cout = True)
  s = res.out_vars[0]
  out_vars.append(s)
  cnf += res.cnf
  out_vars.reverse()
  return next_free_var, Result(x + y, out_vars, cnf)

'''
Given bit vector, create variables and assign their bit values accordingly
'''
def create_constant_vec(next_free_var, vec):
  out_vars = []
  cnf = []
  for i in range(len(vec)):
    out_vars.append(next_free_var)
    if vec[i] == 0:
      cnf.append([-next_free_var])
    else:
      cnf.append([next_free_var])
    next_free_var += 1
  return next_free_var, Result([], out_vars, cnf)    

