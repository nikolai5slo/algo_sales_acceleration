import os
import pickle
import sys
import time

import numpy as np

from helpers.scoring import SC4, expand, map_many, SC1, SC2, SC3, AtoI, BtoI


def printResults(result):
    for k, scores in result.items():
        scs = map_many(SC1(), SC2(), SC3(), AtoI(), BtoI(), SC4(0.1))
        scores = np.average(list(map(expand(scs), scores)), axis=0)
        print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.3f}".format(v * 100), scores[:4])), scores[5])

def readArgs():
    if '-v' in sys.argv or '--verbose' in sys.argv:
        return (5, 20, None)
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    orderlim = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    saveto = sys.argv[3] if len(sys.argv) > 3 else None

    return (K, orderlim, saveto)

def dprint(*args):
    if '-v' in sys.argv or '--verbose' in sys.argv:
        print(*args)

class suppress_stdout_stderr(object):
    '''
    Context manager for suppressing stdout and stderror
    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fd =  os.open(os.devnull,os.O_RDWR)
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointer to stdout and stderr.
        os.dup2(self.null_fd, 1)
        os.dup2(self.null_fd, 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)

        # Close the null file
        os.close(self.null_fd)


class MeasureTimer(object):
    '''
    Context manager for measuring process time
    '''
    def __init__(self, timefun = time.perf_counter):
        self.runs = []
        self._fn = timefun

    def __enter__(self):
        self.time = self._fn()

    def __exit__(self, *args):
        self.runs.append(self._fn() - self.time)

    def getAverage(self):
        return sum(self.runs) / len(self.runs)

    def getAvg(self):
        return self.getAverage()

    def getSum(self):
        return sum(self.runs)

    def getMax(self):
        return max(self.runs)

    def getMin(self):
        return min(self.runs)

    def saveToFile(self, fd):
        pickle.dump(self.runs, fd)

class Result(object):
    def __init__(self, results, timer):
        self.results = results
        self.timer = timer