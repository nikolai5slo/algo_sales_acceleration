import os
import sys

def printResults(result):
    for k, scores in result.items():
        print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v * 100), scores)))

def readArgs():
    if '-v' in sys.argv or '--verbose' in sys.argv:
        return (5, 20, None)
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    orderlim = int(sys.argv[2]) if len(sys.argv) > 2 else 20
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
