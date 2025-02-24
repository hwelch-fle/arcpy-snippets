import this
from collections import Counter
import numpy as np
#words = this.s*1000
#
#vals = [val.strip() for row in words.split('\n') for val in row.split(' ') if val.strip()]

vals = np.random.randint(0, 100, size=10000000, dtype='int') 

def python():
    return np.array(list(Counter(vals).items()), dtype=[('Package', 'U50'), ('Counts', 'i4')])

def numpy():
    v, u = np.unique(vals, return_counts=True)
    return np.array(list(zip(v, u)), dtype=[('Package', 'U50'), ('Counts', 'i4')])

numpy_list = sorted(numpy().tolist())
python_list = sorted(python().tolist())

assert numpy_list == python_list

from decimal import Decimal