import sys
import pickle

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np
import helpers.weights as weights

from helpers.helpers import dprint, readArgs, printResults, MeasureTimer, Result

# Load orders
from predictor import predict_products_for_buyers, validate_products_for_buyers

(K, orderlim, saveto) = readArgs()

timer = MeasureTimer()

orders = data.cut_orders_by_repeated_buyers(data.load_orders(), orderlim)
#orders = list(filter(lambda o: o['promotion'] == None, orders))
buyers = set([order['buyer'] for order in orders])
products = set([order['product'] for order in orders])

# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Construct bipartite graph from train set
B = graph.construct_bi_graph_buyer_product(train)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)

# Get all test products from test set
testBuyers, testProducts = nx.bipartite.sets(B_test)

all_c = len(products)

product_info = {order['product']: order for order in orders}

results = [{}, {}]
for idx, m in enumerate([graph.all_neighbours, graph.common_neighbours]):
    w1 = weights.simple_weight()
    w2 = weights.bipartite_products_weights(B)
    w3 = weights.weight_products_category(product_info)
    w4 = weights.weight_products_promotion(product_info)
    for wi, w in enumerate([w1, w2, w3, w4]):
        def runForK(k):
            dprint("Running for k: ", k)
            with timer:
                predicted = predict_products_for_buyers(B, testBuyers, weights.cutOffK(w, k), m)
            scores = validate_products_for_buyers(B_test, predicted, all_c)
            #return tuple(np.average(list(scores), axis=0))
            return list(scores)
        results[idx][wi] = { k: runForK(k) for k in range(0, K) }


if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump(Result(results, timer), f)

for i, r in results[0].items():
    print("UNION W" + str(i+1))
    printResults(r)

print()

for i, r in results[1].items():
    print("INTERSECT W" + str(i+1))
    printResults(r)

print("Average time %s" % timer.getAverage())