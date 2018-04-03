# A collection of cipher encodings
We first create CNF generators for "building block" functions (see `cnf_base.py`), then generate CNF for ciphers based on cipher definitions.

## Requirements
* [cryptominisat](https://github.com/msoos/cryptominisat)

  We use cryptominisat's Python wrapper to perform tests on the generated CNFs

## File naming conventions
* `cnf_base.py`: "Building block" functions
* `<cipher>.py`: Cipher generating class
* `test_<...>.py`: For unit testing
* `<cipher>.tv`: Test vectors for cipher

## Usage
* At the top of your script, add `from <cipher> import *`
* `cipher = <cipher>(<params>)`
* `next_free_variable, result = cipher.setup()`
* `result.cnf` contains the CNF representing the cipher
* `result.in_vars` contain the input variables. By default, res.in_vars = [key vars, plaintext vars]
* `result.out_vars` contain the output variables. By default, res.out_vars = [ciphertext vars]

### Examples (via cryptominisat)
#### Importing FEAL
```
from feal import *
feal = FEAL_NX(32)
nfv, res = feal.setup()
```

#### Simulation
```
from pycryptosat import Solver
s = Solver()
s.add_clauses(res.cnf)
<Extract key and plaintext variables from res.in_vars>
<Extract ciphertext variables from res.out_vars>
ass = <Assign T/F to variables in key and plaintext variables>
sat, soln = s.solve(ass)
<Read off T/F for ciphertext by looking at soln[variable]>
```

#### Known plaintext attack
```
from pycryptosat import Solver
s = Solver()
s.add_clauses(res.cnf)
<Extract key and plaintext variables from res.in_vars>
<Extract ciphertext variables from res.out_vars>
ass = <Assign T/F to variables in plaintext and ciphertext variables>
sat, soln = s.solve(ass)
<Read off T/F for key by looking at soln[variable]>
```

## Currently supported ciphers
* FEAL-NX

  A Fiestel-based cipher first published in 1987 by Akihiro Shimizu and Shoji Miyaguchi from NTT

  [Wikipedia](https://en.wikipedia.org/wiki/FEAL) |
[Official page](http://info.isl.ntt.co.jp/crypt/eng/archive/index.html#feal) |
[Specifications](http://info.isl.ntt.co.jp/crypt/eng/archive/dl/feal/call-3e.pdf) |
[Test vectors (N = 32 rounds)](http://info.isl.ntt.co.jp/crypt/eng/archive/dl/feal/call-5.zip)
