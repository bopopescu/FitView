import time
import logging

def timing(f):
    def wrap(*args):
        log = logging.getLogger(__name__)
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        log.debug('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap