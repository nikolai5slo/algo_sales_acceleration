import os
import sys


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
