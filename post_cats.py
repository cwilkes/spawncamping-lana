import redis
import sys
import gzip
import time

r = redis.StrictRedis(host='localhost', port=6379, db=0)

args = sys.argv[1:]
sha1 = args.pop(0)


reader = gzip.open(args.pop(0))

lines = 0
num_flushes = 0
pipe = None


class Timer(object):
    def __init__(self):
        self.start_time = time.time()
        self.last_time = self.start_time
        self.end_time = None

    def mark(self, fmt, *argv):
        cur_time = time.time()
        print cur_time-self.last_time, fmt % argv
        self.last_time = cur_time

    def end(self):
        if self.end_time is None:
            self.end_time = time.time()
        return self.end_time - self.start_time


timer = Timer()


for uid, tuples in (_.strip().split(None, 1) for _ in reader):
    if pipe is None:
        pipe = r.pipeline()
    pipe.evalsha(sha1, 1, int(uid), tuples)
    lines += 1
    if lines % 100 == 0:
        pipe.execute()
        pipe = None
        num_flushes += 1
    if lines % 7500 == 0:
        timer.mark('inserted: %d, flushes: %d', lines, num_flushes)

if pipe is not None:
    pipe.execute()
    num_flushes += 1

total_time = timer.end()
print total_time, 'inserted: %d, flushes: %d' % (lines, num_flushes)
