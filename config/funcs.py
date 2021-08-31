### Functions ###
from time import time


def wait_time(start):
    end = time()
    total = end - start
    if total < .2:
        wait = .2 - total
        return wait
    else:
        return 0
