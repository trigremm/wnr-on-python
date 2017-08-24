"""yyyyMMdd-HH_mm_ss"""
import datetime


def get_time():
    dt = datetime.datetime.now()
    tf = '%Y%m%d-%H-%M-%S'
    ts = dt.strftime(tf)
    return ts


def get_time_old():
    dt = datetime.datetime.now()
    time_format = '{0:%Y}{0:%m}{0:%d}-{0:%H}_{0:%M}_{0:%S}'
    time_string = time_format.format(dt)
    return time_string


def test():
    import timeit
    print(timeit.timeit('get_time()', setup='from __main__ import get_time'))
    print(timeit.timeit('get_time_old()', setup='from __main__ import get_time_old'))
