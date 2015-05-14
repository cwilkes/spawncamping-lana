import sys
import os
import re
import gzip
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta
from uuid import uuid4

file_re = re.compile('(\d{4}-\d{2}-\d{2})')


def read_file(fn):
    if fn.endswith('.gz'):
        reader = gzip.open(fn)
    else:
        reader = open(fn)
    for p in (_.strip().split() for _ in reader):
        yield p


def process(fn, date, output_dir):
    output_fn = uuid4().urn[9:] + '.csv'
    print 'output file name', output_fn
    handles = dict()
    for offset in range(0, 32):
        d2 = date+relativedelta(days=-offset)
        output_path = os.path.join(output_dir, '%04d-%02d-%02d' % (d2.year, d2.month+1, d2.day), output_fn)
        if not os.path.isdir(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        print 'offset %02d : %s' % (offset, output_path)
        handles[str(offset)] = open(output_path, 'w')
    lines = 0
    for p in read_file(fn):
        uid = p[0]
        for ns, site, cat, frequency, recency in (_.split(',') for _ in p[1:-1]):
            handles[recency].write('%s,%s,%s,%s\n' % (uid, ns, site, cat))
        lines+=1
        if lines % 10000 == 0:
            print 'flushing', lines, 'lines'
            for w in handles.values():
                w.flush()
    print 'done with file %s and %d lines' % (fn, lines)
    for w in handles.values():
        w.close()


def main(args):
    args.pop(0)
    input_fn = args.pop(0)
    if not os.path.isfile(input_fn):
        print 'not a file', input_fn
        return 1
    m = file_re.search(input_fn)
    if not m:
        print 'does not look like "%s" : "%s"' % (file_re, input_fn)
        return 1
    date = date_parse(m.group(1))
    output_dir = args.pop(0)
    if not os.path.isdir(output_dir):
        print 'not a directory', output_dir
        return 1
    process(input_fn, date, output_dir)



if __name__ == '__main__':
    sys.exit(main(sys.argv))
