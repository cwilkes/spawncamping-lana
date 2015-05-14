import sys
import numpy as np
import util
import os
from pylearn2.config import yaml_parse
from pylearn2.utils import serial
import theano
from collections import Counter


def prep_data(all_data_fn, output_dir=None):
    uid, data, labels = util.load_from_train(all_data_fn)
    cutoffs = util.find_cutoffs(data, 0.99)
    x2 = np.clip(data, [0 for _ in range(cutoffs.size)], cutoffs)
    x3, mags = util.scale_rows(x2)
    if output_dir is not None:
        np.save(os.path.join(output_dir, 'cutoffs.npy'), cutoffs)
        np.save(os.path.join(output_dir, 'mags.npy'), mags)
    return x3, labels


def seperate_train_test(data, labels, output_dir):
    train_fn = os.path.join(output_dir, 'train.npy')
    train_labels_fn = os.path.join(output_dir, 'train_labels.npy')
    test_fn = os.path.join(output_dir, 'test.npy')
    test_labels_fn = os.path.join(output_dir, 'test_labels.npy')

    train, test, mask = util.split_train_test(data)

    np.save(train_fn, train)
    np.save(train_labels_fn, labels[mask])
    np.save(test_fn, test)
    np.save(test_labels_fn, labels[~mask])

    return train_fn


def make_model(args):
    all_data_fn = args.pop(0)
    output_dir = args.pop(0)

    data, labels = prep_data(all_data_fn, output_dir)


    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    train_fn = seperate_train_test(data, labels, output_dir)
    nvis = np.load(train_fn).shape[1]

    model_fn = os.path.join(output_dir, 'model.pkl')

    hyper_params_aa = dict(
        nvis=nvis, batch_size=75, nhid=100, save_freq=5,
        tied_weights=False, max_epochs=200)
    hyper_params_aa['input_fn'] = train_fn
    hyper_params_aa['output_fn'] = model_fn

    aa_yaml = open('autoenc1.yaml', 'r').read()
    config = aa_yaml % hyper_params_aa

    train = yaml_parse.load(config)
    train.main_loop()


def make_hidden(args):
    model_fn = args.pop(0)
    input_fn = args.pop(0)
    output_fn = args.pop(0)
    model = serial.load(model_fn)
    x = serial.load(input_fn)
    X = model.get_input_space().make_theano_batch()
    Y = model.encode(X)
    f = theano.function([X], Y, allow_input_downcast=True)
    encoded=f(x)
    hb=model.hidbias
    bias=np.repeat([hb.get_value()], encoded.shape[0], axis=0)
    hid=encoded+bias
    hid_val=np.zeros(hid.shape, np.int)
    hid_val[hid > 0] = 1
    np.save(output_fn, hid_val)
    for label in range(hid_val.shape[1]):
        c=Counter(hid_val[:,label])
        print label, c[0], c[1]


def main(args):
    args=args[1:]
    action = args.pop(0)
    if action == 'make_model':
        make_model(args)
    elif action == 'make_hidden':
        make_hidden(args)
    else:
        print 'Do not know about "%s"' % (action, )
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
