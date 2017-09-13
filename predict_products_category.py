from collections import defaultdict

import sys
import pickle

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np

from helpers.helpers import dprint, readArgs, Result, MeasureTimer, printResults

from predictor import validate_buyers_for_products, validate_products_for_buyers
import operator

(K, orderlim, saveto) = readArgs()

# Load orders
orders = data.cut_orders_by_repeated_buyers(data.load_orders(), orderlim)

buyers = set([order['buyer'] for order in orders])
all_c = len(buyers)

# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)
testBuyers, testProducts = nx.bipartite.sets(B_test)

category_buyers = defaultdict(lambda: defaultdict(int))
category_products = defaultdict(list)

timer = MeasureTimer()

for order in train:
    category_buyers[order['buyer']][order['category']] += 1
    category_products[order['category']].append(order['product'])

def predict_category_products(testBuyers, category_buyers, category_products, k):
    for buyer in testBuyers:
        if len(category_buyers[buyer]) > 0:
            category = max(category_buyers[buyer].items(), key=operator.itemgetter(1))[0]
            products = np.random.choice(category_products[category], min(len(category_products[category]), k), replace=False)
            yield (buyer, products)
        else:
            yield (buyer, [])

results = {}
for k in range(0, K):
    dprint("Running for k: ", k)
    with timer:
        predicted = predict_category_products(testBuyers, category_buyers, category_products, k)

    scores = validate_products_for_buyers(B_test, predicted, all_c)
    #results[k] = tuple(np.average(list(scores), axis=0))
    results[k] = list(scores)

if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump(Result(results, timer),f)


printResults(results)

print("Average time %s" % timer.getAverage())