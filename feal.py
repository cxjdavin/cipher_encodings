from cnf_base import *

class FEAL_NX:
  # N = number of rounds (must be even)
  # key length = 128
  def __init__(self, N):
    assert(N % 2 == 0)
    self.N = N
    self.init_keys = [i for i in range(1, 128+1)]
    self.plaintext = [128+i for i in range(1, 64+1)]
  
  def setup(self):
    cnf = []
    nfv = 128+64+1

    # Key schedule
    nfv, key_schedule_res = self.key_schedule(nfv)
    cnf += key_schedule_res.cnf

    # Pre-processing
    nfv, pre_state = self.preprocess(nfv)
    cnf += pre_state.cnf

    # Perform rounds
    self.state = [pre_state.out_vars]
    for r in range(1, self.N+1):
      nfv, res = self.one_round(nfv, r)
      cnf += res.cnf

    # Post-processing
    nfv, post_state = self.postprocess(nfv)
    self.ciphertext = post_state.out_vars
    cnf += post_state.cnf

    return nfv, Result(self.init_keys + self.plaintext, self.ciphertext, cnf)
    
  def s0(self, nfv, x1, x2):
    nfv, add_res = modular_addition(nfv, 8, x1, x2)
    nfv, rot_res = rotate_left_by_k(nfv, 8, add_res.out_vars, 2)
    return nfv, Result(x1 + x2, rot_res.out_vars, add_res.cnf + rot_res.cnf)
  
  def s1(self, nfv, x1, x2):
    nfv, one_res = create_constant_vec(nfv, [0,0,0,0,0,0,0,1])
    nfv, add_res = modular_addition(nfv, 8, x1, x2)
    nfv, add2_res = modular_addition(nfv, 8, add_res.out_vars, one_res.out_vars)
    nfv, rot_res = rotate_left_by_k(nfv, 8, add2_res.out_vars, 2)
    return nfv, Result(x1 + x2, rot_res.out_vars, one_res.cnf + add_res.cnf + add2_res.cnf + rot_res.cnf)
  
  '''
  a = (a0, a1, a2, a3), b = (b0, b1), f = (f0, f1, f2, f3)
  res1 : f1 = a1 xor b0
  res2 : f2 = a2 xor b1
  res3 : f1 = f1 xor a0
  res4 : f2 = f2 xor a3
  res5 : f1 = s1(f1, f2)
  res6 : f2 = s0(f2, f1)
  res7 : f0 = s0(a0, f1)
  res8 : f3 = s1(a3, f2)
  '''
  def f(self, nfv, alpha, beta):
    assert(len(alpha) == 4*8)
    assert(len(beta) == 2*8)
    a0 = alpha[0*8:1*8]
    a1 = alpha[1*8:2*8]
    a2 = alpha[2*8:3*8]
    a3 = alpha[3*8:4*8]
    b0 = beta[0*8:1*8]
    b1 = beta[1*8:2*8]
    nfv, res1 = word_xor(nfv, a1, b0)
    nfv, res2 = word_xor(nfv, a2, b1)
    nfv, res3 = word_xor(nfv, res1.out_vars, a0)
    nfv, res4 = word_xor(nfv, res2.out_vars, a3)
    nfv, res5 = self.s1(nfv, res3.out_vars, res4.out_vars)
    nfv, res6 = self.s0(nfv, res4.out_vars, res5.out_vars)
    nfv, res7 = self.s0(nfv, a0, res5.out_vars)
    nfv, res8 = self.s1(nfv, a3, res6.out_vars)
    return nfv, Result(alpha + beta,
                       res7.out_vars + res5.out_vars + res6.out_vars + res8.out_vars,
                       res1.cnf + res2.cnf + res3.cnf + res4.cnf + res5.cnf + res6.cnf + res7.cnf + res8.cnf)
  
  '''
  a = (a0, a1, a2, a3), b = (b0, b1, b2, b3), fk = (fk0, fk1, fk2, fk3)
  res1 : fk1 = a1 xor a0
  res2 : fk2 = a2 xor a3
  res3 : fk1 = s1(fk1, (fk2 xor b0))
  res4 : fk2 = s0(fk2, (fk1 xor b1))
  res5 : fk0 = s0(a0, (fk1 xor b2))
  res6 : fk3 = s1(a3, (fk2 xor b3))
  '''
  def fk(self, nfv, alpha, beta):
    assert(len(alpha) == 4*8)
    assert(len(beta) == 4*8)
    a0 = alpha[0*8:1*8]
    a1 = alpha[1*8:2*8]
    a2 = alpha[2*8:3*8]
    a3 = alpha[3*8:4*8]
    b0 = beta[0*8:1*8]
    b1 = beta[1*8:2*8]
    b2 = beta[2*8:3*8]
    b3 = beta[3*8:4*8]
    nfv, res1 = word_xor(nfv, a1, a0)
    nfv, res2 = word_xor(nfv, a2, a3)
    nfv, res3_right = word_xor(nfv, res2.out_vars, b0)
    nfv, res3 = self.s1(nfv, res1.out_vars, res3_right.out_vars)
    nfv, res4_right = word_xor(nfv, res3.out_vars, b1)
    nfv, res4 = self.s0(nfv, res2.out_vars, res4_right.out_vars)
    nfv, res5_right = word_xor(nfv, res3.out_vars, b2)
    nfv, res5 = self.s0(nfv, a0, res5_right.out_vars)
    nfv, res6_right = word_xor(nfv, res4.out_vars, b3)
    nfv, res6 = self.s1(nfv, a3, res6_right.out_vars)
    return nfv, Result(alpha + beta,
                       res5.out_vars + res3.out_vars + res4.out_vars + res6.out_vars,
                       res1.cnf + res2.cnf + res3_right.cnf + res3.cnf + res4_right.cnf + res4.cnf + res5_right.cnf + res5.cnf + res6_right.cnf + res6.cnf)
  
  def key_schedule(self, nfv):
    assert(self.N % 2 == 0)
    assert(len(self.init_keys) == 128)
    cnf = []
    
    # init_keys = (K_l, K_r) = ((A_0, B_0), (K_r1, K_r2))
    K_l = self.init_keys[0:64]
    K_r = self.init_keys[64:128]
    K_r1 = K_r[0:32]
    K_r2 = K_r[32:64]
    
    # Process right key K_r
    # Q[r] = Q_r
    nfv, Kr1_xor_Kr2_res = word_xor(nfv, K_r1, K_r2)
    cnf += Kr1_xor_Kr2_res.cnf
    Kr1_xor_Kr2 = Kr1_xor_Kr2_res.out_vars
    Q = [None]
    for r in range(1, self.N + 1):
      if r % 3 == 1:
        Q.append(Kr1_xor_Kr2)
      elif r % 3 == 2:
        Q.append(K_r1)
      elif r % 3 == 0:
        Q.append(K_r2)
  
    # Process left key K_l
    # (A_0, B_0) = K_l
    # A[i] = A_i, B[i] = B_i, D[i] = D_i
    A = [K_l[0:32]]
    B = [K_l[32:64]]
    nfv, d_init = create_constant_vec(nfv, [0]*32)
    cnf += d_init.cnf
    D = [d_init.out_vars]
    
    # Compute K_i
    self.keys = []
    for r in range(1, (self.N//2)+4 + 1):
      D.append(A[r-1])
      A.append(B[r-1])
      nfv, Br_r = word_xor(nfv, B[r-1], D[r-1])
      nfv, Br_r2 = word_xor(nfv, Br_r.out_vars, Q[r])
      nfv, Br_res = self.fk(nfv, A[r-1], Br_r2.out_vars)
      B.append(Br_res.out_vars)
      Br0 = Br_res.out_vars[0:8]
      Br1 = Br_res.out_vars[8:16]
      Br2 = Br_res.out_vars[16:24]
      Br3 = Br_res.out_vars[24:32]
      self.keys.append(Br0 + Br1)
      self.keys.append(Br2 + Br3)
      cnf += Br_r.cnf
      cnf += Br_r2.cnf
      cnf += Br_res.cnf

    self.Q = Q
    self.A = A
    self.B = B
    self.D = D
    return nfv, Result([], [], cnf)
    
  def preprocess(self, nfv):
    assert(self.N % 2 == 0)
    assert(len(self.plaintext) == 64)
    assert(len(self.keys) == self.N + 8)
    nfv, res = word_xor(nfv, self.plaintext, self.keys[self.N] + self.keys[self.N+1] + self.keys[self.N+2] + self.keys[self.N+3])
    nfv, zeroes = create_constant_vec(nfv, [0]*32)
    lhs = res.out_vars
    rhs = zeroes.out_vars + res.out_vars[0:32]
    nfv, res2 = word_xor(nfv, lhs, rhs)
    return nfv, Result([], res2.out_vars, res.cnf + zeroes.cnf + res2.cnf)
  
  def one_round(self, nfv, r):
    prev = self.state[r-1]
    prev_l = prev[0:32]
    prev_r = prev[32:64]
    round_key = self.keys[r-1]
    cur_l = prev_r
    nfv, rr = self.f(nfv, prev_r, round_key)
    nfv, r = word_xor(nfv, prev_l, rr.out_vars)
    cur_r = r.out_vars
    self.state.append(cur_l + cur_r)
    return nfv, Result([], [], rr.cnf + r.cnf)

  def postprocess(self, nfv):
    assert(len(self.keys) == self.N + 8)
    l_n = self.state[-1][:32]
    r_n = self.state[-1][32:]
    nfv, zeroes = create_constant_vec(nfv, [0]*32)
    lhs = r_n + l_n
    rhs = zeroes.out_vars + r_n
    nfv, res = word_xor(nfv, lhs, rhs)
    lhs2 = res.out_vars
    rhs2 = self.keys[self.N+4] + self.keys[self.N+5] + self.keys[self.N+6] + self.keys[self.N+7]
    nfv, res2 = word_xor(nfv, lhs2, rhs2)
    return nfv, Result([], res2.out_vars, zeroes.cnf + res.cnf + res2.cnf)

