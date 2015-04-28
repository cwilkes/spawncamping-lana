hyper_params_aa = dict(input_fn='/tmp/data_%d.npy' % (label, ), nvis=93, batch_size=100, max_epochs=401, nhid=12, output_fn='/tmp/model_%d.pkl' % (label, ), save_freq=50)


aa_yaml=open('autoenc1.yaml', 'r').read()
config=aa_yaml % hyper_params_aa



train = yaml_parse.load(config)
