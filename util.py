import os
import numpy as np
import sys
from collections import Counter
import theano
from pylearn2.utils import serial


def find_cutoffs(ary, percent, min_cutoff=0, trim_zeros=True):
    a2 = np.sort(ary, axis=0)
    if trim_zeros:
        ret = list()
        for pos, vals in enumerate(a2.T):
            q = vals[vals > min_cutoff]
            ret.append(q[q.size*percent])
        return np.array(ret)
    else:
        return a2[a2.shape[0]*percent]


def scale(ary, percent=0.99):
    cutoffs = find_cutoffs(ary, percent)
    b = 1.*ary / cutoffs
    return np.clip(b, 0, 1.0), b > 1.0


def get_train_test_mask(data_len, train_percent=0.80):
    ind = np.arange(data_len)
    np.random.shuffle(ind)
    mask = np.zeros(data_len, np.bool)
    mask_on_indexes = ind[:ind.size*train_percent]
    mask[mask_on_indexes] = True
    return mask


def split_train_test(ary, train_percent=0.80):
    mask = get_train_test_mask(ary.shape[0], train_percent)
    return ary[mask], ary[~mask]


def autoencode(model_fn, input_fn):
    model = serial.load(model_fn)
    x = serial.load(input_fn)
    X = model.get_input_space().make_theano_batch()
    Y = model.reconstruct(X)
    f = theano.function([X], Y, allow_input_downcast=True)
    return f(x), x


def _is_list(val):
    """
    cheesy test to see if a number or a list / numpy array
    """
    try:
        len(val)
        return False
    except:
        return True


def make_submission_file(fn, dr, model):
    w = open(fn, 'w')
    for row_id, data in zip(dr.ids, dr.data):
        prediction = model.predict(data)
        if _is_list(prediction):
            out = prediction
        else:
            out = np.zeros(9, np.int)
            out[prediction] = 1
        w.append('%d,%s\n' % (row_id, ','.join((str(_) for _ in out))))
    w.close()


class DownloadReader(object):
    def __init__(self, fn='train.csv', data_dir='/Users/cwilkes/Documents/workspace/kaggle/otto_data'):
        self.input_file = os.path.join(data_dir, fn)
        if self.input_file.endswith('.npy'):
            q = np.load(self.input_file)
            self.ids = q[:, 0]
            if q.shape[1] == 95:
                self.data = q[:, 1:-1]
                self.labels = q[:, -1]
                self.has_label = True
            else:
                self.data = q[:, 1:]
                self.labels = np.ndarray(0)
                self.has_label = False
        else:
            reader = (_.strip().split(',') for _ in open(self.input_file))
            headers = next(reader)
            self.has_label = headers[-1] == 'target'
            raw_data = list()
            raw_labels = list()
            raw_ids = list()
            for p in reader:
                if self.has_label:
                    vals = [int(_) for _ in p[1:-1]]
                    ending_label_str = p[-1].split('_')[-1]
                    raw_labels.append(int(ending_label_str)-1)
                else:
                    vals = [int(_) for _ in p[1:]]
                raw_data.append(vals)
                raw_ids.append(int(p[0]))
            self.data = np.array(raw_data)
            self.labels = np.array(raw_labels)
            self.py_labels = self.labels.reshape((self.labels.size, 1))
            self.ids = np.array(raw_ids)

    def __repr__(self):
        return 'Shape: %s, Labels: %s' % (self.data.shape, Counter(self.labels).most_common())

    def get_mask_for_label(self, label):
        return self.labels == label

    def get_data_for_label(self, label):
        return self.data[self.get_mask_for_label(label)]

    def write_as_numpy_array(self, fn, use_data_dir=True):
        out_ary = np.hstack((self.ids.reshape((self.ids.size, 1)), self.data))
        if self.has_label:
            out_ary = np.hstack((out_ary, self.labels.reshape(self.labels.size, 1)))
        if use_data_dir:
            fn = os.path.join(os.path.dirname(self.input_file), fn)
        np.save(fn, out_ary)
