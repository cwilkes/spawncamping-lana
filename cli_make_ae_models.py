import sys
import os
import util
import numpy as np
import util
from pylearn2.config import yaml_parse
import time

def _mkdir(fn):
    d = os.path.dirname(fn)
    if not os.path.isdir(d):
        os.makedirs(d)


def run_ae(model_fn, data_fn, output_fn):
    _mkdir(output_fn)
    y, x = util.autoencode(model_fn, data_fn)
    diffs = np.sum(np.power(y-x, 2), axis=1)
    np.save(output_fn, diffs)


class MakeAEModels():
    def __init__(self, raw_train_fn, top_dir):
        self.dl = util.DownloadReader(raw_train_fn)
        self.data, self.overs = util.scale(self.dl.data, 0.99)
        #self.data[self.data > 0] = 1
        #self.data = np.hstack((self.data, self.overs.astype(self.data.dtype)))
        #last_col = np.sum(self.overs, axis=1)
        last_col = np.zeros(self.overs.shape[0])
        last_col[np.sum(self.overs, axis=1)>0] = True
        #self.data = np.hstack((self.data, last_col.reshape(last_col.shape[0], -1)))
        self.top_dir = top_dir
        self.base_hyper_params_aa = dict(
            nvis=self.data.shape[1], batch_size=10, nhid=60, save_freq=10,
            tied_weights=False)
        self.aa_yaml=open('autoenc1.yaml', 'r').read()

    def run_label(self, label):
        start_time = time.time()
        print >>sys.stderr, start_time, 'Working on label', label
        print 'Working on label', label
        train_fn = os.path.join(self.top_dir, 'train', 'data_%d_train.npy' % (label, ))
        test_fn = os.path.join(self.top_dir, 'test', 'data_%d_test.npy' % (label, ))
        model_fn = os.path.join(self.top_dir, 'model', 'model_%d.pkl' % (label, ))
        result_fn = os.path.join(self.top_dir, 'results', 'result_%d_%d.npy' % (label, label))
        _mkdir(train_fn)
        _mkdir(test_fn)
        _mkdir(model_fn)

        train, test, mask = util.split_train_test(self.data[self.dl.get_mask_for_label(label)], 0.80)
        np.save(train_fn, train)
        np.save(test_fn, test)

        hyper_params_aa = self.base_hyper_params_aa.copy()
        hyper_params_aa['input_fn'] = train_fn
        hyper_params_aa['output_fn'] = model_fn
        #hyper_params_aa['max_epochs'] = train.shape[0]/580000+40
        hyper_params_aa['max_epochs'] = 300
        config = self.aa_yaml % hyper_params_aa

        train = yaml_parse.load(config)
        train.main_loop()
        run_ae(model_fn, test_fn, result_fn)
        print 'time', time.time() - start_time, 'model', model_fn, 'result', result_fn, 'train', train


def main():
    args = sys.argv[1:]
    raw_train_fn = args.pop(0)
    if not os.path.isfile(raw_train_fn):
        print >>sys.stderr, 'must be the raw data file', raw_train_fn
    output_dir = args.pop(0)
    if not os.path.isdir(output_dir):
        print >>sys.stderr, 'Output dir not a directory', output_dir
        return 1
    maem = MakeAEModels(raw_train_fn, output_dir)
    for label in (int(_) for _ in args):
        maem.run_label(label)


if __name__ == '__main__':
    sys.exit(main())
