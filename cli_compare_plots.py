import sys
import os
from collections import namedtuple
import util
import numpy as np


TrainTest = namedtuple('TrainTest', 'model_fn test_fn')


def make_plots(tt_1, tt_2):
    print >>sys.stderr, 'Working on', tt_1, tt_2
    y_1_1, x_1_1 = util.autoencode(tt_1.model_fn, tt_1.test_fn)
    y_1_2, x_1_2 = util.autoencode(tt_1.model_fn, tt_2.test_fn)
    y_2_1, x_2_1 = util.autoencode(tt_2.model_fn, tt_1.test_fn)
    y_2_2, x_2_2 = util.autoencode(tt_2.model_fn, tt_2.test_fn)
    diff_1_1 = np.sum(np.power(y_1_1-x_1_1, 2), axis=1)
    diff_1_2 = np.sum(np.power(y_1_2-x_1_2, 2), axis=1)
    diff_2_1 = np.sum(np.power(y_2_1-x_2_1, 2), axis=1)
    diff_2_2 = np.sum(np.power(y_2_2-x_2_2, 2), axis=1)
    print >>sys.stderr, 'sizes', diff_1_1.shape, diff_2_1.shape, diff_1_2.shape, diff_2_2.shape
    X_1 = np.vstack((diff_1_1, diff_2_1)).T
    X_2 = np.vstack((diff_1_2, diff_2_2)).T
    X = np.vstack((X_1, X_2))
    Y = np.zeros(X.shape[0], np.int)
    Y[:X_1.shape[0]] = 0
    Y[-X_2.shape[0]:] = 1
    a = np.zeros((Y.size, 3))
    a[:,0] = Y
    a[:,1:] = X
    return a


def make_train_test(top_dir, label):
    return TrainTest(
        os.path.join(top_dir, 'model', 'model_%d.pkl' % (label, )),
        os.path.join(top_dir, 'test', 'data_%d_test.npy' % (label, ))
    )


def main():
    args = sys.argv[1:]
    top_dir = args.pop(0)
    if not os.path.isdir(top_dir):
        print >>sys.stderr, 'Not a directory', top_dir
        return 1
    label_1 = int(args.pop(0))
    label_2 = int(args.pop(0))
    output_fn = args.pop(0)
    data = make_plots(make_train_test(top_dir, label_1), make_train_test(top_dir, label_2))
    np.save(output_fn, data)


if __name__ == '__main__':
    sys.exit(main())
