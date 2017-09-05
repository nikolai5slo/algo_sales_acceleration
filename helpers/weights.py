from functools import reduce

import numpy as np
from itertools import groupby, zip_longest
import operator



def weight_rating(products_info):
    def _(i1, i2, products):
        l = np.array(
            [float(products_info[p]['rating']) if p in products_info and products_info[p]['rating'] != None else float(0)
             for p in products])
        return np.sum(l) / len(products) if len(l) > 0 else 0
    return _


def weight_category(product_info):
    def _(i1, i2, products):
        # Get categories for products
        l = [product_info[pi]['category'] for pi in products if pi in product_info]
        # Group by categories and count
        g = [len(list(group)) for key, group in groupby(l)]
        if len(g) > 0:
            return np.average(g)
        return 0
    return _

def weight_products_category(product_info):
    def _(i1, i2, buyers):
        return int(i1 in product_info and i2 in product_info and product_info[i1]['category'] == product_info[i2]['category'])
    return _


def weight_promotion(products_info):
    def _(i1, i2, products):
        return sum(1 if p not in products_info or products_info[p]['promotion'] is None else 0 for p in products)
    return _

def weight_products_promotion(products_info):
    def _(i1, i2, buyers):
        return sum(1 if p not in products_info or products_info[p]['promotion'] is None else 0 for p in [i1, i2])
    return _

def weight_quantity(products_info):
    def _(i1, i2, products):
        s = sum(products_info[p]['quantity'] if p in products_info else 0 for p in products)
        return s
    return _

def simple_weight():
    def _(i1, i2, products):
        return len(products)
    return _

def bipartite_weights(B):
    def _(i1, i2, products):
        if len(products) == 0:
            return 0
        return np.sum([B[i1][p]['weight'] + B[i2][p]['weight'] for p in products])
    return _

def bipartite_products_weights(B):
    def _(i1, i2, buyers):
        if len(buyers) == 0:
            return 0
        return np.sum([B[b][i1]['weight'] + B[b][i2]['weight'] for b in buyers])
    return _

def cutOffK(fn, k):
    def _(i1, i2, products):
        ret = fn(i1, i2, products)
        return ret if ret is not None and ret >= k else None

    return _

def mul(fns):
    def _(i1, i2, products):
        return reduce(operator.mul, [fn(i1, i2, products) for fn in fns])
    return _

def combine_weights(fns, weights = []):
    def _(i1, i2, products):
        res = []
        for fn in fns:
            r = fn(i1, i2, products)
            if r is None:
                return None
            res.append(r)

        return sum(a * b for a, b in zip_longest(res, weights, fillvalue = 1))

    return _