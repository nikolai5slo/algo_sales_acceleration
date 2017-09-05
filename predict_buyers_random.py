from collections import defaultdict

import sys
import pickle

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np

from helpers.helpers import dprint, readArgs

from predictor import validate_buyers_for_products

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


def predict_random_buyers(testProducts, k):
    for product in testProducts:
        by = np.random.choice(list(buyers), all_c - int(all_c * k/100))
        yield (product, by)

results = {}
for k in np.linspace(0, 100, K):
    dprint("Running for k: ", k)
    predicted = predict_random_buyers(testProducts, k)

    scores = validate_buyers_for_products(B_test, predicted, all_c)
    results[k] = tuple(np.average(list(scores), axis=0))

if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump((results),f)



for k, scores in results.items():
    print("{0:.2f}".format(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v * 100), scores)))

