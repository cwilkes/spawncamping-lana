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
        self.data, self.overs = util.scale(self.dl.data)
        self.top_dir = top_dir
        self.base_hyper_params_aa = dict(nvis=93, batch_size=100, max_epochs=76, nhid=15, save_freq=25)
        self.aa_yaml=open('autoenc1.yaml', 'r').read()

    def run_label(self, label):
        print >>sys.stderr, time.time(), 'Working on label', label
        print 'Working on label', label
        train_fn = os.path.join(self.top_dir, 'train', 'data_%d_train.npy' % (label, ))
        test_fn = os.path.join(self.top_dir, 'test', 'data_%d_test.npy' % (label, ))
        model_fn = os.path.join(self.top_dir, 'model', 'model_%d.pkl' % (label, ))
        result_fn = os.path.join(self.top_dir, 'results', 'result_%d_%d.npy' % (label, label))
        _mkdir(train_fn)
        _mkdir(test_fn)
        _mkdir(model_fn)

        train, test = util.split_train_test(self.data[self.dl.get_mask_for_label(label)], 0.80)
        np.save(train_fn, train)
        np.save(test_fn, test)

        hyper_params_aa = self.base_hyper_params_aa.copy()
        hyper_params_aa['input_fn'] = train_fn
        hyper_params_aa['output_fn'] = model_fn
        config = self.aa_yaml % hyper_params_aa

        train = yaml_parse.load(config)
        train.main_loop()
        run_ae(model_fn, test_fn, result_fn)
        print 'model', model_fn, 'result', result_fn


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
