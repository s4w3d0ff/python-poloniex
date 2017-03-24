import collections
import time

calls_per_second = 6

deq = collections.deque(list(), calls_per_second)




def time_over_timeframe(d):
    return deq[-1] - deq[0]

def load_queue(interval):
    for i in xrange(20):
        time.sleep(interval)
        deq.append(time.time())


print deq

too_fast = 1 / 12.0
load_queue(too_fast)
print time_over_timeframe(deq) # only 0.49 seconds elapsed

slow_enough = 1 / 4.0
load_queue(slow_enough)
print time_over_timeframe(deq) # 1.33 seconds elapsed
