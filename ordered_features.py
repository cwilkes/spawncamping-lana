import numpy as np
from collections import Counter
import sys


def get_above_zero_sorted(data):
    q = np.argsort(data, axis=1)
    ret = list()
    for x, xi in zip(data, q):
        ret.append(xi[x[xi] > 0])
    return ret


def find_descending(data):
    q = np.argsort(data, axis=1)
    ret = list()
    while len(ret) < data.shape[1]:
        c = Counter(q[:, -1])
        print >>sys.stderr, 'round:', len(ret), c.most_common()[:10]
        if len(ret) < data.shape[1]-1:
            c.update(Counter(q[:, -2]))
        print >>sys.stderr, ' round', len(ret), c.most_common()[:10]
        val = c.most_common()[0][0]
        ret.append(val)
        for vals in q:
            i = np.arange(vals.size)[vals == val][0]
            vals[1:i+1] = vals[0:i]
    return np.array(ret)
