
def SC3():
    def _(A, B, TP, I):
        return TP / (A+B-TP) if TP > 0 else 0
    return _

def SC1():
    def _(A, B, TP, I):
        return TP / A if TP > 0 else 0
    return _

def SC2():
    def _(A, B, TP, I):
        return TP / B if TP > 0 else 0
    return _

def SC4(alpha):
    def _(A, B, TP, I):
        return (TP - alpha * (A - TP)) / A if A > 0 else 0
    return _

def AtoI():
    def _(A, B, TP, I):
        return A / I
    return _

def BtoI():
    def _(A, B, TP, I):
        return B / I
    return _


def expand(fn):
    def _(tuple):
        return fn(*tuple)
    return _

def map_many(*args):
    def _(*args2):
        return tuple(fn(*args2) for fn in args)
    return _