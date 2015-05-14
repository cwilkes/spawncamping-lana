"""
Test for softmax_regression.ipynb
from /Users/cwilkes/Documents/workspace/pylearn2//pylearn2/scripts//tutorials/softmax_regression/tests/test_softmaxreg.py

"""
import os
import sys
from pylearn2.config import yaml_parse
from theano import config
import numpy as np

def config_fn(dirname):
    def get(fn):
        return os.path.join(dirname, 'config', fn)
    return get


def get_number_labels(fn):
    y = np.load(fn)
    #return len(set(y))
    return y.shape[1]


def test():

    args = sys.argv[1:]

    dirname = args.pop(0)
    train_fn = args.pop(0)
    labels_fn = args.pop(0)
    output_fn = args.pop(0)

    fn = config_fn(dirname)
    nvis=np.load(train_fn).shape[1]

    with open(fn('sr_dataset.yaml'), 'r') as f:
        dataset = f.read()

    hyper_params = dict(input_fn=train_fn, labels_fn=labels_fn)
    dataset = dataset % hyper_params

    with open(fn('sr_model.yaml'), 'r') as f:
        model = f.read()

    model = model % dict(number_classes=get_number_labels(labels_fn), nvis=nvis)

    with open(fn('sr_algorithm.yaml'), 'r') as f:
        algorithm = f.read()

    hyper_params = dict(batch_size=10, max_epochs=100)
    algorithm = algorithm % hyper_params

    with open(fn('sr_train.yaml'), 'r') as f:
        train = f.read()

    save_path = output_fn
    train = train % locals()
    print 'train'
    print train

    train = yaml_parse.load(train)
    print 'running'
    train.main_loop()

    try:
        os.remove("{}/softmax_regression.pkl".format(save_path))
        os.remove("{}/softmax_regression_best.pkl".format(save_path))
    except OSError:
        pass

if __name__ == '__main__':
    test()
