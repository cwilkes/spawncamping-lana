import sys
import os
import re
import gzip
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta
from uuid import uuid4
from collections import Counter

file_re = re.compile('(\d{4}-\d{2}-\d{2})/part-.*(\d+)')


def read_file(fn):
    if fn.endswith('.gz'):
        reader = gzip.open(fn)
    else:
        reader = open(fn)
    for p in (_.strip().split() for _ in reader):
        yield p


def process(input_fn, date, part_num, output_dir):
    date_str = '%04d-%02d-%02d' % (date.year, date.month, date.day)
    handles = dict()
    for r in range(0, 32):
        d2 = date + relativedelta(days=-r)
        fn = os.path.join(output_dir, '%04d-%02d-%02d_%d_%d.csv' % (d2.year, d2.month, d2.day, part_num, r))
        print 'recency %02d: %s' % (r, fn)
        handles[str(r)] = open(fn, 'w')
    lines, attr = 0, 0
    for p in read_file(input_fn):
        uid = p[0]
        for ns, site, cat, frequency, recency in (_.split(',') for _ in p[1:-1]):
            w = handles[recency]
            w.write('%s,%s,%s,%s,%s,%s\n' % (uid, date_str, ns, site, cat, frequency))
            attr += 1
        lines += 1
        if lines % 10000 == 0:
            print 'flushing %d attributes in %d lines' % (attr, lines)
            for w in handles.values():
                w.flush()
    print 'done with file %s and %d lines with %d attribtues' % (input_fn, lines, attr)
    for w in handles.values():
        w.flush()


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
    date, part_num = date_parse(m.group(1)), int(m.group(2))
    output_dir = args.pop(0)
    if not os.path.isdir(output_dir):
        print 'not a directory', output_dir
        return 1
    process(input_fn, date, part_num, output_dir)



if __name__ == '__main__':
    sys.exit(main(sys.argv))
